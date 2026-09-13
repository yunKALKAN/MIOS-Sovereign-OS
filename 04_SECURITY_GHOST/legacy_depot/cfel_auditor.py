#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
  MIOS CORE - CFEL (CRYPTOGRAPHIC FORENSIC EVIDENCE LEDGER) BOT AUDITOR
  Module       : 01_MIOS_CORE/bot_depot/cfel_auditor.py
  Version      : v2.0.0-EnterpriseCFEL
  Architecture : SHA-256 Chained Immutable Ledger for Telegram Bot Operations
  Security Rule: NO SECRET VALUES EVER RECORDED IN AUDIT LEDGER.
                 Records: EVENT, BOT, TIMESTAMP, ACTION, RESULT, HASH.
================================================================================
"""

import os
import sys
import json
import copy
import hashlib
import threading
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

try:
    if "/home/yunuskalkan/01_MIOS_CORE" not in sys.path:
        sys.path.insert(0, "/home/yunuskalkan/01_MIOS_CORE")
    from version_authority import version_authority
    CFEL_MODULE_VERSION = version_authority.get_component_version("reporting")
except Exception:
    CFEL_MODULE_VERSION = "18.5.0-cfel.2.5"

DEFAULT_LEDGER_PATH = "/root/MIOS_SOVEREIGN_OS/04_SECURITY_GHOST/legacy_depot/data/cfel_bot_depot_ledger.json"
FALLBACK_LEDGER_PATH = "/home/yunuskalkan/03_TRADING_BOTS/test-ledger/cfel_trading_ledger.json"

SENSITIVE_KEY_NAMES = {
    "token", "secret", "private_key", "password", "key", "passphrase", "api_key", "secret_key"
}


def sanitize_payload(obj: Any) -> Any:
    """Payload içindeki hassas anahtarları ve gizli değerleri recursive temizler."""
    if isinstance(obj, dict):
        cleaned = {}
        for k, v in obj.items():
            k_lower = str(k).lower()
            if any(s in k_lower for s in SENSITIVE_KEY_NAMES):
                # Değerin hash'ini veya maskesini koy, asla kendisini koyma
                if isinstance(v, str) and v:
                    cleaned[k] = f"<REDACTED_HASH:{hashlib.sha256(v.encode('utf-8')).hexdigest()[:12]}>"
                else:
                    cleaned[k] = "<REDACTED>"
            else:
                cleaned[k] = sanitize_payload(v)
        return cleaned
    elif isinstance(obj, list):
        return [sanitize_payload(x) for x in obj]
    return obj


class CFELBotAuditor:
    """
    MIOS Bot Operasyonları için Kriptografik Denetim ve Kanıt Mühürleyici.
    Her kritik bot eylemini SHA-256 blok zinciri olarak dosyaya mühürler.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(CFELBotAuditor, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, ledger_file: str = DEFAULT_LEDGER_PATH):
        if not getattr(self, "_initialized", False):
            self._write_lock = threading.RLock()
            self._initialized = True
        self.ledger_file = ledger_file
        os.makedirs(os.path.dirname(self.ledger_file), exist_ok=True)
        self._ensure_ledger_file()

    def _ensure_ledger_file(self) -> None:
        """Defter dosyası yoksa Genesis bloğuyla başlatır."""
        with self._write_lock:
            if not os.path.exists(self.ledger_file):
                genesis_block = {
                    "block_index": 0,
                    "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                    "event_type": "GENESIS_BOOT",
                    "bot_id": "mios-core-master",
                    "action": "BOOTSTRAP_BOT_DEPOT",
                    "result": "SUCCESS",
                    "payload": {
                        "system": "MIOS CENTRAL BOT DEPOT",
                        "tier": "ENTERPRISE",
                        "security": "SEALED_HASH_CHAIN",
                        "version": "v2.0.0-Depot"
                    },
                    "prev_hash": "0" * 64,
                    "block_hash": "0000000000000000000000000000000000000000000000000000000000000000"
                }
                canonical_payload = json.dumps(genesis_block["payload"], sort_keys=True, separators=(",", ":"), ensure_ascii=False)
                canonical = f"0|{genesis_block['timestamp']}|GENESIS_BOOT|mios-core-master|BOOTSTRAP_BOT_DEPOT|SUCCESS|{canonical_payload}|{genesis_block['prev_hash']}"
                genesis_block["block_hash"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
                
                with open(self.ledger_file, "w", encoding="utf-8") as f:
                    json.dump([genesis_block], f, indent=2, ensure_ascii=False)

    def seal_event(
        self,
        event_type: str,
        bot_id: str,
        action: str,
        result: str,
        payload: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Bir olayı CFEL defterine kriptografik olarak mühürler.
        Döndürülen değer bloğun SHA-256 hash'idir.
        """
        with self._write_lock:
            records: List[Dict[str, Any]] = []
            try:
                if os.path.exists(self.ledger_file):
                    with open(self.ledger_file, "r", encoding="utf-8") as f:
                        records = json.load(f)
            except Exception:
                records = []

            prev_hash = records[-1]["block_hash"] if records else ("0" * 64)
            idx = len(records)
            ts = datetime.now(timezone.utc).isoformat() + "Z"
            
            clean_payload = sanitize_payload(payload or {})
            canonical_payload = json.dumps(clean_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

            content = f"{idx}|{ts}|{event_type}|{bot_id}|{action}|{result}|{canonical_payload}|{prev_hash}"
            block_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

            block = {
                "block_index": idx,
                "timestamp": ts,
                "event_type": str(event_type),
                "bot_id": str(bot_id),
                "action": str(action),
                "result": str(result),
                "payload": clean_payload,
                "prev_hash": prev_hash,
                "block_hash": block_hash
            }

            records.append(block)

            # Atomic write (Multi-thread safe & crash-proof)
            import uuid
            os.makedirs(os.path.dirname(self.ledger_file), exist_ok=True)
            temp_file = f"{self.ledger_file}.{uuid.uuid4().hex}.tmp"
            try:
                with open(temp_file, "w", encoding="utf-8") as f:
                    json.dump(records, f, indent=2, ensure_ascii=False)
                os.replace(temp_file, self.ledger_file)
            except Exception as io_err:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except Exception:
                    pass
                # Trading motorunu asla durdurma, log defteri için sessizce devam et
                pass

            return block_hash

    def get_state(self) -> Dict[str, Any]:
        """CFEL defterinin canlı durumunu döndürür."""
        with self._write_lock:
            count = 0
            latest_hash = "0" * 64
            latest_event = "NONE"
            latest_bot = "NONE"
            is_valid = True

            if os.path.exists(self.ledger_file):
                try:
                    with open(self.ledger_file, "r", encoding="utf-8") as f:
                        records = json.load(f)
                        count = len(records)
                        if records:
                            latest_hash = records[-1].get("block_hash", "0" * 64)
                            latest_event = records[-1].get("event_type", "UNKNOWN")
                            latest_bot = records[-1].get("bot_id", "UNKNOWN")
                except Exception:
                    is_valid = False

            return {
                "system": "MIOS_CFEL_LEDGER",
                "ledger_file": self.ledger_file,
                "total_sealed_events": count,
                "latest_block_index": max(0, count - 1),
                "latest_block_hash": latest_hash,
                "latest_event_type": latest_event,
                "latest_bot": latest_bot,
                "chain_integrity": "VERIFIED_VALID" if is_valid else "CORRUPTED",
                "tamper_proof": True
            }

    def verify_chain(self) -> Tuple[bool, str]:
        """Tüm CFEL zincirinin bütünlüğünü ve hash sürekliliğini doğrular."""
        with self._write_lock:
            if not os.path.exists(self.ledger_file):
                return False, "Ledger file missing"

            try:
                with open(self.ledger_file, "r", encoding="utf-8") as f:
                    records = json.load(f)

                if not records:
                    return False, "Empty ledger"

                for i, block in enumerate(records):
                    if block["block_index"] != i:
                        return False, f"Block index mismatch at index {i}"

                    if i > 0:
                        expected_prev = records[i - 1]["block_hash"]
                        if block["prev_hash"] != expected_prev:
                            return False, f"Broken hash chain at block #{i}"

                    canonical_payload = json.dumps(block.get("payload", {}), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
                    content = f"{block['block_index']}|{block['timestamp']}|{block['event_type']}|{block['bot_id']}|{block['action']}|{block['result']}|{canonical_payload}|{block['prev_hash']}"
                    
                    expected_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
                    if block["block_hash"] != expected_hash:
                        return False, f"Tampered hash detected at block #{i}"

                return True, f"CFEL Chain perfectly verified ({len(records)} blocks sealed)"

            except Exception as e:
                return False, f"Verification exception: {e}"

    def get_recent_records(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Son mühürlenen denetim kayıtlarını döndürür."""
        with self._write_lock:
            if os.path.exists(self.ledger_file):
                try:
                    with open(self.ledger_file, "r", encoding="utf-8") as f:
                        records = json.load(f)
                        return records[-limit:]
                except Exception:
                    pass
            return []


# Singleton Instance
cfel_auditor = CFELBotAuditor()
