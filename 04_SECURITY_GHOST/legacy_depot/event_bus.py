#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
  MIOS CORE - CENTRAL EVENT BUS
  Module       : 01_MIOS_CORE/bot_depot/event_bus.py
  Version      : v2.0.0-EnterpriseEventBus
  Architecture : Central Publish/Subscribe Backbone for MIOS Bot Operations
  Rule         : Bots do not message each other directly. All interactions,
                 signals, alerts, and state transitions flow through Event Bus.
================================================================================
"""

import time
import inspect
import asyncio
import threading
import logging
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime, timezone

from cfel_auditor import cfel_auditor

logger = logging.getLogger("MIOS.EventBus")

# =====================================================================
# 📡 STANDART MIOS EVENT TİPLERİ
# =====================================================================
EVENT_BOT_HEALTH_CHANGED  = "BOT_HEALTH_CHANGED"
EVENT_BOT_OFFLINE         = "BOT_OFFLINE"
EVENT_BOT_RECOVERED       = "BOT_RECOVERED"
EVENT_SECURITY_ALERT      = "SECURITY_ALERT"
EVENT_SECURITY_EVENT      = "SECURITY_EVENT"
EVENT_CONFIG_CHANGED      = "CONFIG_CHANGED"
EVENT_TRADE_FILLED        = "TRADE_FILLED"
EVENT_SIGNAL_CREATED      = "SIGNAL_CREATED"
EVENT_GUARDIAN_ALERT      = "GUARDIAN_ALERT"
EVENT_CFEL_SEALED         = "CFEL_SEALED"
EVENT_SERVICE_RESTARTED   = "SERVICE_RESTARTED"
EVENT_DAILY_REPORT_DUE    = "DAILY_REPORT_DUE"
EVENT_SHIFT_CLOSING_DUE   = "SHIFT_CLOSING_DUE"
EVENT_COMMAND_EXECUTED    = "COMMAND_EXECUTED"
EVENT_TAMPER_DETECTED     = "TAMPER_DETECTED"
EVENT_UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"

# 🎯 Trading & Guardian Pozisyon Yaşam Döngüsü Olayları
EVENT_POSITION_OPENED             = "POSITION_OPENED"
EVENT_POSITION_UPDATED            = "POSITION_UPDATED"
EVENT_POSITION_CLOSE_REQUESTED    = "POSITION_CLOSE_REQUESTED"
EVENT_POSITION_CLOSED             = "POSITION_CLOSED"
EVENT_GUARDIAN_STOP_REQUESTED     = "GUARDIAN_STOP_REQUESTED"
EVENT_EMERGENCY_FREEZE_REQUESTED  = "EMERGENCY_FREEZE_REQUESTED"
EVENT_EMERGENCY_FREEZE_ACTIVE     = "EMERGENCY_FREEZE_ACTIVE"
EVENT_RECONCILIATION_FAILED       = "RECONCILIATION_FAILED"
EVENT_RISK_GATE_VETO              = "RISK_GATE_VETO"
EVENT_GUARDIAN_HEARTBEAT          = "GUARDIAN_HEARTBEAT"

# 📺 Medya ve Topluluk Operasyon Olayları (MucizeWORK YouTube & LinkedIn)
EVENT_MEDIA_INBOX_RECEIVED      = "MEDIA_INBOX_RECEIVED"
EVENT_MEDIA_CONTENT_VALIDATED   = "MEDIA_CONTENT_VALIDATED"
EVENT_MEDIA_UPLOAD_INITIATED    = "MEDIA_UPLOAD_INITIATED"
EVENT_MEDIA_UPLOAD_COMPLETED    = "MEDIA_UPLOAD_COMPLETED"
EVENT_MEDIA_VETO_TRIGGERED      = "MEDIA_VETO_TRIGGERED"
EVENT_MEDIA_ANALYTICS_COLLECTED = "MEDIA_ANALYTICS_COLLECTED"

# 💼 LinkedIn Medya Olayları
EVENT_LINKEDIN_POST_REQUESTED   = "LINKEDIN_POST_REQUESTED"
EVENT_LINKEDIN_POST_PUBLISHED   = "LINKEDIN_POST_PUBLISHED"
EVENT_LINKEDIN_VETO_TRIGGERED   = "LINKEDIN_VETO_TRIGGERED"

# 📧 Mail Engine Olayları
EVENT_MAIL_SEND_REQUESTED       = "MAIL_SEND_REQUESTED"
EVENT_MAIL_SENT                 = "MAIL_SENT"
EVENT_MAIL_SEND_FAILED          = "MAIL_SEND_FAILED"
EVENT_MAIL_RECEIVED             = "MAIL_RECEIVED"


class MIOSEvent:
    """Tekil bir MIOS Olayı veri yapısı."""
    def __init__(
        self,
        event_type: str,
        bot_id: str,
        data: Optional[Dict[str, Any]] = None,
        severity: str = "INFO",
        seal_cfel: bool = True
    ):
        self.event_type = event_type
        self.bot_id = bot_id
        self.data = data or {}
        self.severity = severity.upper()
        self.timestamp = datetime.now(timezone.utc).isoformat() + "Z"
        self.seal_cfel = seal_cfel
        self.cfel_hash: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "bot_id": self.bot_id,
            "severity": self.severity,
            "timestamp": self.timestamp,
            "data": self.data,
            "cfel_hash": self.cfel_hash,
        }

    def __repr__(self) -> str:
        return f"<MIOSEvent {self.event_type} bot={self.bot_id} sev={self.severity}>"


class MIOSEventBus:
    """
    MIOS Merkezi Asenkron Olay Omurgası (Event Bus).
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MIOSEventBus, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._subscribers = defaultdict(list)
        self._wildcard_subscribers = []
        self._history: List[MIOSEvent] = []
        self._bus_lock = threading.RLock()
        self._max_history = 1000
        self._initialized = True

    def subscribe(self, event_type: str, callback: Callable[[MIOSEvent], Any]) -> None:
        """Belirli bir olay türünü dinlemek için abone olur."""
        with self._bus_lock:
            if event_type == "*":
                self._wildcard_subscribers.append(callback)
            else:
                self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable[[MIOSEvent], Any]) -> None:
        """Aboneliği sonlandırır."""
        with self._bus_lock:
            if event_type == "*" and callback in self._wildcard_subscribers:
                self._wildcard_subscribers.remove(callback)
            elif callback in self._subscribers.get(event_type, []):
                self._subscribers[event_type].remove(callback)

    def publish(
        self,
        event_type: Any,
        bot_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        severity: str = "INFO",
        seal_cfel: bool = True
    ) -> MIOSEvent:
        """
        Olayı yayınlar, CFEL defterine mühürler ve abonelere dağıtır.
        """
        if isinstance(event_type, MIOSEvent):
            event = event_type
            event_type = event.event_type
            bot_id = event.bot_id
            data = event.data
            severity = event.severity
            seal_cfel = event.seal_cfel
        else:
            event = MIOSEvent(
                event_type=event_type,
                bot_id=bot_id or "unknown-bot",
                data=data,
                severity=severity,
                seal_cfel=seal_cfel
            )

        # CFEL Otomatik Mühürleme (Kritik veya mühür istenen olaylar)
        if seal_cfel:
            block_hash = cfel_auditor.seal_event(
                event_type=event_type,
                bot_id=bot_id,
                action=f"EVENT_BUS_PUBLISH_{severity}",
                result="DELIVERED",
                payload=data or {}
            )
            event.cfel_hash = block_hash

        with self._bus_lock:
            self._history.append(event)
            if len(self._history) > self._max_history:
                self._history.pop(0)

            handlers = list(self._subscribers.get(event_type, [])) + list(self._wildcard_subscribers)

        for handler in handlers:
            try:
                if inspect.iscoroutinefunction(handler):
                    asyncio.create_task(handler(event))
                else:
                    handler(event)
            except Exception as e:
                logger.warning(f"EventBus handler hatası ({event_type}): {e}")

        return event

    def get_recent_events(self, limit: int = 50, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Son olayları listeler."""
        with self._bus_lock:
            events = self._history
            if event_type:
                events = [e for e in events if e.event_type == event_type]
            return [e.to_dict() for e in events[-limit:]]

    def stats(self) -> Dict[str, Any]:
        """Event bus istatistikleri."""
        with self._bus_lock:
            return {
                "total_events_dispatched": len(self._history),
                "total_subscriptions": sum(len(v) for v in self._subscribers.values()) + len(self._wildcard_subscribers),
                "active_event_types": list(self._subscribers.keys()),
            }


# Singleton Instance
event_bus = MIOSEventBus()
