#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
  MIOS CORE - MİOXID 99 LEGACY BOT INTEGRATION BRIDGE
  Module       : 01_MIOS_CORE/bot_depot/mioxid99_bot.py
  Version      : v1.0.0-MioxiD99
  Bot Username : @mucizework_runtime_bot (Bot ID: 8763036932)
  Purpose      : Preserves legacy runtime notification functions while integrating
                 directly into MIOS Core Bot Registry, Secret Treasury, and Event Bus.
================================================================================
"""

import time
import json
import logging
import requests
import threading
from typing import Any, Dict, List, Optional

from treasury import treasury
from registry import bot_registry
from cfel_auditor import cfel_auditor
from event_bus import event_bus, EVENT_TRADE_FILLED, EVENT_GUARDIAN_ALERT

logger = logging.getLogger("MIOS.MioxiD99")


class MIOXid99Bot:
    """
    Eski MİOXid 99 Botunun Merkezi MIOS Registry ve Event Bus Köprüsü.
    
    Önceki işlevlerini (trading alarmları, runtime bildirimleri) eksiksiz sürdürür,
    aynı zamanda tüm olayları merkezi CFEL defterine mühürler.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MIOXid99Bot, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self.bot_id = "mioxid-99"
        self.telegram_username = "@mucizework_runtime_bot"
        self._initialized = True

    def get_token(self) -> Optional[str]:
        return treasury.get_mioxid99_token(self.bot_id)

    def send_legacy_notification(self, title: str, text: str, chat_id: Optional[str] = None) -> bool:
        """
        Eski bot yapısıyla uyumlu bildirim gönderimi.
        Mevcut bot.py, mioxid_fleet.py ve guardian scriptleri bu fonksiyonu doğrudan çağırabilir.
        """
        token = self.get_token()
        target_chat = chat_id or treasury.get_signal_chat_id(self.bot_id)
        if not token or not target_chat:
            logger.debug(f"[MIOXID_99_SIMULATION] {title}: {text}")
            return True

        # Metrik ve Heartbeat Güncelle
        bot_registry.record_metric(self.bot_id, "events", 1)
        bot_registry.update_heartbeat(self.bot_id, "ONLINE")

        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {
                "chat_id": target_chat,
                "text": f"🛡️ *[MİOXİD 99 - {title}]*\n\n{text}",
                "parse_mode": "Markdown",
            }
            r = requests.post(url, json=payload, timeout=3.0)
            
            # CFEL Mührü
            cfel_auditor.seal_event(
                event_type="MIOXID99_NOTIFICATION_SENT",
                bot_id=self.bot_id,
                action="BROADCAST_MESSAGE",
                result="DELIVERED" if r.status_code == 200 else "API_ERROR",
                payload={"title": title, "status_code": r.status_code}
            )
            return r.status_code == 200
        except Exception as e:
            bot_registry.record_metric(self.bot_id, "errors", 1)
            logger.debug(f"Mioxid99 send error: {e}")
            return False

    def info(self) -> Dict[str, Any]:
        """MioxiD 99 tespit ve durum raporu."""
        return {
            "bot_id": self.bot_id,
            "name": "MİOXid 99",
            "username": self.telegram_username,
            "role": "Legacy Runtime Bridge & Trading Notification Daemon",
            "status": bot_registry.get_bot(self.bot_id).status if bot_registry.get_bot(self.bot_id) else "ONLINE",
            "token_configured": bool(self.get_token()),
            "secret_scope": "SCOPE_MIOXID_99",
        }


# Singleton Instance
mioxid99_bot = MIOXid99Bot()
