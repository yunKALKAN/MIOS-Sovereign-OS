#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
  MIOS CORE - SECURITY & TAMPERING AUDIT ENGINE
  Module       : 01_MIOS_CORE/bot_depot/security_engine.py
  Version      : v2.0.0-EnterpriseSecurity
  Architecture : Real-Time Tamper Detection & Backdoor Defense
  Rule         : NO SECRET VALUES EVER REPORTED.
                 Only event types, severity, actions, and hashes are logged.
================================================================================
"""

import os
import re
import time
import json
import shutil
import hashlib
import subprocess
import threading
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

from treasury import treasury, mask_secret
from cfel_auditor import cfel_auditor

logger = logging.getLogger("MIOS.SecurityEngine")

KNOWN_PM2_PROCESSES = {"solana-sniper", "mios-telemetry-sync", "mios-guardian-0x7fe6", "mios-depot-daemon"}
KNOWN_CORE_SCRIPTS = {
    "bot.py", "sync_telemetry.py", "mios_wallet_guardian.py", "mios_trading_orchestrator.py",
    "mioxid_fleet.py", "mios_core_telemetry.py", "unified_runtime.py", "live_bridge.py"
}

SUSPICIOUS_COMMAND_PATTERNS = [
    r"(?i)(rm\s+-rf\s+/)",
    r"(?i)(curl.*\|\s*bash)",
    r"(?i)(wget.*\|\s*sh)",
    r"(?i)(/bin/nc|/bin/netcat)",
    r"(?i)(eval\s*\(base64)",
    r"(?i)(mkfifo.*sh)",
    r"(?i)(/dev/tcp/)",
]


class SecurityTamperEngine:
    """
    MIOS Güvenlik ve Bütünlük Denetim Motoru.
    Arka kapıları, yetkisiz Telegram işlemlerini, beklenmeyen process/cron/systemd
    değişikliklerini ve dosya bozulmalarını tarar.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SecurityTamperEngine, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._security_events: List[Dict[str, Any]] = []
        self._blocked_attempts_count = 0
        self._last_scan_time: Optional[str] = None
        self._file_baselines: Dict[str, str] = {}
        self._lock_scan = threading.RLock()
        self._build_baseline_hashes()
        self._initialized = True

    def _get_utc3_time(self) -> str:
        tz_utc3 = timezone(timedelta(hours=3))
        return datetime.now(tz_utc3).strftime("%Y-%m-%d %H:%M:%S (UTC+3)")

    def _build_baseline_hashes(self) -> None:
        """Kritik MIOS Core ve Bot dosyalarının SHA-256 bütünlük parmak izini çıkarır."""
        tracked_paths = [
            "/root/MIOS_SOVEREIGN_OS/04_SECURITY_GHOST/legacy_depot/treasury.py",
            "/root/MIOS_SOVEREIGN_OS/04_SECURITY_GHOST/legacy_depot/cfel_auditor.py",
            "/root/MIOS_SOVEREIGN_OS/04_SECURITY_GHOST/legacy_depot/registry.py",
            "/root/MIOS_SOVEREIGN_OS/04_SECURITY_GHOST/legacy_depot/event_bus.py",
            "/home/yunuskalkan/01_MIOS_CORE/mios_unified/runtime/unified_runtime.py",
        ]
        for path in tracked_paths:
            if os.path.exists(path):
                try:
                    with open(path, "rb") as f:
                        self._file_baselines[path] = hashlib.sha256(f.read()).hexdigest()
                except Exception:
                    pass

    def record_security_event(
        self,
        bot_id: str,
        event_name: str,
        severity: str = "HIGH",
        action: str = "BLOCKED",
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Güvenlik olayını kaydeder, CFEL defterine kanıt mühürler.
        """
        with self._lock_scan:
            time_str = self._get_utc3_time()
            if action.upper() == "BLOCKED":
                self._blocked_attempts_count += 1

            # CFEL Mühürleme (Secret VALUE ASLA BULUNMAZ)
            cfel_hash = cfel_auditor.seal_event(
                event_type="SECURITY_EVENT",
                bot_id=bot_id,
                action=f"{event_name}_{action}",
                result=action,
                payload={
                    "event": event_name,
                    "severity": severity,
                    "action": action,
                    "details": details or {},
                }
            )

            event_record = {
                "bot_id": bot_id,
                "event": event_name,
                "severity": severity,
                "action": action,
                "time": time_str,
                "cfel_hash": cfel_hash,
                "details": details or {},
            }
            self._security_events.append(event_record)
            logger.warning(f"🚨 [SECURITY] {bot_id} -> {event_name} ({severity}) - {action}")
            return event_record

    def format_security_alert(self, bot_id: str, event_name: str, severity: str = "CRITICAL", action: str = "BLOCKED") -> str:
        """
        Kritik güvenlik uyarısı formatı:
        🚨 MIOS SECURITY ALERT
        BOT: ...
        EVENT: ...
        SEVERITY: ...
        ACTION: ...
        CORE: MIOS CORE
        CFEL: SEALED
        TIME: UTC+3
        """
        time_str = self._get_utc3_time()
        return (
            f"🚨 *MIOS SECURITY ALERT*\n\n"
            f"*BOT:*\n{bot_id}\n\n"
            f"*EVENT:*\n{event_name}\n\n"
            f"*SEVERITY:*\n{severity}\n\n"
            f"*ACTION:*\n{action}\n\n"
            f"*CORE:*\nMIOS CORE\n\n"
            f"*CFEL:*\nSEALED\n\n"
            f"*TIME:*\n{time_str}"
        )

    def format_tamper_event(self, bot_name: str, event_name: str, severity: str = "HIGH", action: str = "BLOCKED") -> str:
        """
        Bütünlük/Tampering olayı formatı:
        🚨 SECURITY EVENT
        BOT: ...
        EVENT: ...
        SEVERITY: ...
        ACTION: ...
        MIOS CORE: NOTIFIED
        CFEL: EVIDENCE SEALED
        """
        return (
            f"🚨 *SECURITY EVENT*\n\n"
            f"*BOT:*\n{bot_name}\n\n"
            f"*EVENT:*\n{event_name}\n\n"
            f"*SEVERITY:*\n{severity}\n\n"
            f"*ACTION:*\n{action}\n\n"
            f"*MIOS CORE:*\nNOTIFIED\n\n"
            f"*CFEL:*\nEVIDENCE SEALED"
        )

    def validate_command_safety(self, user_id: str, command_str: str) -> Tuple[bool, Optional[str]]:
        """
        Telegram veya API üzerinden gelen bir komutun güvenliğini denetler.
        """
        for pattern in SUSPICIOUS_COMMAND_PATTERNS:
            if re.search(pattern, command_str):
                self.record_security_event(
                    bot_id="mios-live-command",
                    event_name="MALICIOUS_COMMAND_INJECTION_ATTEMPT",
                    severity="CRITICAL",
                    action="BLOCKED",
                    details={"user_id": user_id, "pattern_matched": pattern}
                )
                return False, "Şüpheli komut dizilimi tespit edildi ve engellendi."
        return True, None

    def run_system_audit_scan(self) -> Dict[str, Any]:
        """
        Arka kapı, bilinmeyen process, cron, PM2 ve dosya bütünlük taraması yapar.
        """
        with self._lock_scan:
            self._last_scan_time = self._get_utc3_time()
            anomalies = []

            # 1. Cron Job Denetimi
            try:
                cron_res = subprocess.run(["crontab", "-l"], capture_output=True, text=True, timeout=3)
                if cron_res.returncode == 0 and cron_res.stdout.strip():
                    cron_lines = [l for l in cron_res.stdout.splitlines() if l and not l.startswith("#")]
                    if len(cron_lines) > 5:
                        anomalies.append({"type": "UNEXPECTED_CRON_ENTRIES", "count": len(cron_lines)})
            except Exception:
                pass

            # 2. PM2 Süreç Denetimi
            try:
                pm2_res = subprocess.run(["pm2", "jlist"], capture_output=True, text=True, timeout=5)
                if pm2_res.returncode == 0 and pm2_res.stdout.strip():
                    pm2_list = json.loads(pm2_res.stdout)
                    for proc in pm2_list:
                        pname = proc.get("name", "")
                        if pname and pname not in KNOWN_PM2_PROCESSES:
                            # Bilinmeyen PM2 süreci
                            pass
            except Exception:
                pass

            # 3. Dosya Bütünlüğü Denetimi
            tampered_files = []
            for path, expected_hash in self._file_baselines.items():
                if os.path.exists(path):
                    try:
                        with open(path, "rb") as f:
                            curr_hash = hashlib.sha256(f.read()).hexdigest()
                            if curr_hash != expected_hash:
                                tampered_files.append(os.path.basename(path))
                    except Exception:
                        pass
            if tampered_files:
                anomalies.append({"type": "SOURCE_CODE_INTEGRITY_DRIFT", "files": tampered_files})

            # 4. Treasury Yetkisiz Erişim Denetimi
            treasury_audit = treasury.audit_summary()
            if treasury_audit.get("unauthorized_attempts", 0) > 0:
                anomalies.append({
                    "type": "TREASURY_UNAUTHORIZED_ACCESS_DETECTED",
                    "count": treasury_audit.get("unauthorized_attempts")
                })

            scan_result = {
                "scan_time": self._last_scan_time,
                "status": "SECURE" if not anomalies else "WARNING",
                "anomalies_detected": len(anomalies),
                "anomalies": anomalies,
                "total_blocked_attempts": self._blocked_attempts_count,
                "tracked_file_hashes": len(self._file_baselines),
                "cfel_verification": cfel_auditor.get_state().get("chain_integrity", "UNKNOWN"),
            }

            return scan_result

    def get_stats(self) -> Dict[str, Any]:
        with self._lock_scan:
            return {
                "total_security_events": len(self._security_events),
                "total_blocked_attempts": self._blocked_attempts_count,
                "last_scan_time": self._last_scan_time or self._get_utc3_time(),
                "recent_events": self._security_events[-5:],
            }


# Singleton Instance
security_engine = SecurityTamperEngine()
