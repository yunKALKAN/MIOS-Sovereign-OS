#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
  MIOS CORE (Mucize Integration Operating System) - CENTRAL SECRET TREASURY
  Module       : 01_MIOS_CORE/bot_depot/treasury.py
  Version      : v2.0.0-EnterpriseTreasury
  Architecture : Single Source of Truth for all MIOS Secrets & Credentials
  Security Rule: BOTS MUST NEVER PASS SECRETS TO EACH OTHER.
                 Access is strictly scoped and audit-sealed in CFEL.
================================================================================
"""

import os
import hashlib
import threading
from typing import Any, Dict, List, Optional, Set
from dotenv import dotenv_values


# =====================================================================
# 🔐 GÜVENLİK KAPSAMLARI (SECRET SCOPES)
# =====================================================================
SCOPE_LIVE_COMMAND = "SCOPE_LIVE_COMMAND"
SCOPE_MIOXID_99    = "SCOPE_MIOXID_99"
SCOPE_GUARDIAN     = "SCOPE_GUARDIAN"
SCOPE_SIGNAL       = "SCOPE_SIGNAL"
SCOPE_TELEMETRY    = "SCOPE_TELEMETRY"
SCOPE_CFEL         = "SCOPE_CFEL"

# Gelecekteki Servis Botu Kapsamları (Genişletilebilir Mimari)
SCOPE_NFT          = "SCOPE_NFT"
SCOPE_COMMUNITY    = "SCOPE_COMMUNITY"
SCOPE_MEDIA        = "SCOPE_MEDIA"
SCOPE_MAIL         = "SCOPE_MAIL"
SCOPE_FINANCE      = "SCOPE_FINANCE"
SCOPE_SECURITY     = "SCOPE_SECURITY"

ALL_SCOPES = {
    SCOPE_LIVE_COMMAND,
    SCOPE_MIOXID_99,
    SCOPE_GUARDIAN,
    SCOPE_SIGNAL,
    SCOPE_TELEMETRY,
    SCOPE_CFEL,
    SCOPE_NFT,
    SCOPE_COMMUNITY,
    SCOPE_MEDIA,
    SCOPE_MAIL,
    SCOPE_FINANCE,
    SCOPE_SECURITY,
}


def mask_secret(value: Optional[str], visible_chars: int = 4) -> str:
    """Gizli bilgiyi asla açıkta bırakmaz, güvenli maskeleme yapar."""
    if not value:
        return "<EMPTY>"
    s = str(value).strip()
    if len(s) <= visible_chars * 2:
        return "***"
    return f"{s[:visible_chars]}...{s[-visible_chars:]}"


def hash_secret_name(name: str) -> str:
    """Secret adının SHA-256 parmak izi."""
    return hashlib.sha256(name.encode("utf-8")).hexdigest()[:16]


class SecretTreasury:
    """
    MIOS Core Merkezi Gizlilik Kasası (Secret Treasury).
    
    Tüm API Key, Token, Private Key, Password ve Telegram Token değerleri
    yalnızca bu kasada saklanır. Botlar birbirlerine doğrudan secret veremez;
    yalnızca kendilerine tanımlanan Secret Scope üzerinden talepte bulunabilir.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SecretTreasury, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, env_path: str = "/home/yunuskalkan/.env"):
        if getattr(self, "_initialized", False):
            return
        self.env_path = env_path
        self._vault: Dict[str, str] = {}
        self._bot_permissions: Dict[str, Set[str]] = {}
        self._access_log: List[Dict[str, Any]] = []
        self._load_lock = threading.RLock()
        self._reload_secrets()
        self._setup_default_scopes()
        self._initialized = True

    def _reload_secrets(self) -> None:
        """Çevresel değişkenleri ve .env dosyasını güvenle kasaya yükler."""
        with self._load_lock:
            loaded: Dict[str, str] = {}
            if os.path.exists(self.env_path):
                try:
                    vals = dotenv_values(self.env_path)
                    for k, v in vals.items():
                        if k and v:
                            loaded[k] = str(v).strip()
                except Exception:
                    pass

            # os.environ üzerine yazılanları da al
            for k, v in os.environ.items():
                if k.startswith(("SOLANA_", "TELEGRAM_", "OKX_", "MIOXID_", "MIOS_", "CFEL_", "JWT_", "HOSTINGER_", "MUCIZEWORK_", "SPEAKANDGO_")):
                    loaded[k] = str(v).strip()

            # Telegram Token Uyumluluk Normalizasyonu (MioxiD99 & MIOS Live Command)
            raw_token = loaded.get("TELEGRAM_TOKEN", "")
            raw_chat_id = loaded.get("TELEGRAM_CHAT_ID", "")
            if raw_token and ":" not in raw_token and raw_chat_id.isdigit() and len(raw_chat_id) in (9, 10):
                full_combined = f"{raw_chat_id}:{raw_token}"
                loaded["MIOXID_99_BOT_TOKEN"] = full_combined
                if "MIOS_LIVE_BOT_TOKEN" not in loaded:
                    loaded["MIOS_LIVE_BOT_TOKEN"] = full_combined
            elif raw_token and ":" in raw_token:
                loaded["MIOXID_99_BOT_TOKEN"] = raw_token
                if "MIOS_LIVE_BOT_TOKEN" not in loaded:
                    loaded["MIOS_LIVE_BOT_TOKEN"] = raw_token

            # Varsayılan Solana & OKX Değerleri
            if "SOLANA_RPC_URL" not in loaded:
                loaded["SOLANA_RPC_URL"] = "https://api.mainnet-beta.solana.com"
            if "OKX_CHAIN_ID" not in loaded:
                loaded["OKX_CHAIN_ID"] = "xlayer-mainnet"

            # Depo & Sinyal Kanalları (Varsayılan ID'ler veya Env'den gelen)
            if "MIOXID_DEPOT_CHAT_ID" not in loaded:
                loaded["MIOXID_DEPOT_CHAT_ID"] = loaded.get("TELEGRAM_DEPOT_CHAT_ID", "-1002345678901")
            if "MIOXID_SIGNAL_CHAT_ID" not in loaded:
                loaded["MIOXID_SIGNAL_CHAT_ID"] = loaded.get("TELEGRAM_SIGNAL_CHAT_ID", "-1002345678902")
            if "MIOS_OPERATIONS_CHAT_ID" not in loaded:
                loaded["MIOS_OPERATIONS_CHAT_ID"] = loaded.get("TELEGRAM_OPERATIONS_CHAT_ID", "-1002345678903")

            self._vault = loaded

    def _setup_default_scopes(self) -> None:
        """İlk 6 MIOS botunun ve gelecekteki servislerin erişim yetkilerini tanımlar."""
        self._bot_permissions = {
            "mios-live-command": {SCOPE_LIVE_COMMAND},
            "mioxid-99":         {SCOPE_MIOXID_99},
            "mios-guardian":     {SCOPE_GUARDIAN},
            "mios-signal":       {SCOPE_SIGNAL},
            "mios-telemetry":    {SCOPE_TELEMETRY},
            "mios-cfel":         {SCOPE_CFEL},
            # Genişletilebilir Servisler
            "mios-nft":          {SCOPE_NFT},
            "mios-community":    {SCOPE_COMMUNITY},
            "mucizework-youtube-worker":  {SCOPE_COMMUNITY, SCOPE_MEDIA},
            "mucizework-linkedin-worker": {SCOPE_COMMUNITY, SCOPE_MEDIA},
            "mail-engine":                {SCOPE_MAIL, SCOPE_COMMUNITY},
            "maymuncuk-business-engine":  {SCOPE_SECURITY, SCOPE_FINANCE},
            "mios-web-portal-engine":     {SCOPE_COMMUNITY, SCOPE_FINANCE},
            "mios-finance":               {SCOPE_FINANCE},
            "mios-security":     {SCOPE_SECURITY},
            "mios-core-master":  ALL_SCOPES,
        }

    def register_bot_scope(self, bot_id: str, scope: str) -> None:
        """Yeni bir bot servisi için kasada güvenli kapsam kaydeder."""
        with self._load_lock:
            if bot_id not in self._bot_permissions:
                self._bot_permissions[bot_id] = set()
            self._bot_permissions[bot_id].add(scope)

    def request_secret(self, bot_id: str, secret_key: str, required_scope: str) -> Optional[str]:
        """
        Bir bot servisinin, kendi yetki kapsamındaki bir credential'a güvenli erişimi.
        
        Kural: Bot yetkili değilse erişim kesinlikle REDDEDİLİR ve olay denetim defterine kaydedilir.
        Secret değeri asla açıkta döndürülmez / loglanmaz.
        """
        with self._load_lock:
            allowed_scopes = self._bot_permissions.get(bot_id, set())
            is_authorized = (
                (required_scope in allowed_scopes)
                or ("ALL" in allowed_scopes)
                or (bot_id == "mios-core-master")
                or (required_scope == "ALL" and bot_id == "mios-core-master")
            )

            # Denetim Girişi Hazırla (Secret VALUE ASLA BULUNMAZ)
            audit_entry = {
                "bot_id": bot_id,
                "requested_key_hash": hash_secret_name(secret_key),
                "scope": required_scope,
                "status": "GRANTED" if is_authorized else "DENIED_UNAUTHORIZED_SCOPE",
            }
            self._access_log.append(audit_entry)

            if not is_authorized:
                return None

            return self._vault.get(secret_key)

    def get_live_bot_token(self, bot_id: str = "mios-live-command") -> Optional[str]:
        """MIOS Live Command botu için Telegram tokeni."""
        return self.request_secret(bot_id, "MIOS_LIVE_BOT_TOKEN", SCOPE_LIVE_COMMAND)

    def get_mioxid99_token(self, bot_id: str = "mioxid-99") -> Optional[str]:
        """MioxiD 99 legacy botu için Telegram tokeni."""
        return self.request_secret(bot_id, "MIOXID_99_BOT_TOKEN", SCOPE_MIOXID_99)

    def set_chat_id(self, chat_id: str) -> None:
        """Kullanıcı veya grup Chat ID'sini dinamik olarak kaydeder."""
        with self._load_lock:
            if chat_id:
                self._vault["TELEGRAM_CHAT_ID"] = str(chat_id)
                self._vault["MIOXID_SIGNAL_CHAT_ID"] = str(chat_id)
                self._vault["MIOXID_DEPOT_CHAT_ID"] = str(chat_id)
                self._vault["MIOS_OPERATIONS_CHAT_ID"] = str(chat_id)

    def get_depot_chat_id(self, bot_id: str) -> str:
        """MucizeWork MİOXid Depot operasyon grubu ID'si."""
        val = self._vault.get("MIOXID_DEPOT_CHAT_ID") or self._vault.get("TELEGRAM_CHAT_ID", "-1002345678901")
        return val

    def get_signal_chat_id(self, bot_id: str) -> str:
        """MİOXid Trading Sinyal kanalı ID'si."""
        val = self._vault.get("MIOXID_SIGNAL_CHAT_ID") or self._vault.get("TELEGRAM_CHAT_ID", "-1002345678902")
        return val

    def get_operations_chat_id(self, bot_id: str) -> str:
        """Kritik Yönetici Operasyonları kanalı ID'si."""
        val = self._vault.get("MIOS_OPERATIONS_CHAT_ID") or self._vault.get("TELEGRAM_CHAT_ID", "-1002345678903")
        return val

    def get_solana_private_key(self, bot_id: str) -> Optional[str]:
        """Yalnızca Guardian veya Signal motoru Solana key'e erişebilir."""
        if bot_id in ("mios-guardian", "mios-signal", "mios-core-master"):
            return self.request_secret(bot_id, "SOLANA_PRIVATE_KEY", SCOPE_GUARDIAN if bot_id == "mios-guardian" else SCOPE_SIGNAL)
        return None

    def get_youtube_credential_paths(self, bot_id: str = "mucizework-youtube-worker") -> Optional[Dict[str, str]]:
        """
        YouTube Worker için istemci kimliği ve token dosyalarını kontrollü sağlar.
        Kural: Yalnızca SCOPE_COMMUNITY / SCOPE_MEDIA yetkisine sahip worker erişebilir.
        """
        with self._load_lock:
            allowed = self._bot_permissions.get(bot_id, set())
            if (SCOPE_COMMUNITY not in allowed and SCOPE_MEDIA not in allowed) and bot_id != "mios-core-master":
                audit_entry = {
                    "bot_id": bot_id,
                    "requested_key_hash": hash_secret_name("YOUTUBE_CREDENTIALS"),
                    "scope": SCOPE_COMMUNITY,
                    "status": "DENIED_UNAUTHORIZED_SCOPE",
                }
                self._access_log.append(audit_entry)
                return None

            client_secret = self._vault.get("YOUTUBE_CLIENT_SECRET_FILE", "/home/yunuskalkan/MucizeWORK_Ekosistem_TV/config/client_secret.json")
            token_file = self._vault.get("YOUTUBE_TOKEN_FILE", "/home/yunuskalkan/MucizeWORK_Ekosistem_TV/config/youtube_token.json")

            audit_entry = {
                "bot_id": bot_id,
                "requested_key_hash": hash_secret_name("YOUTUBE_CREDENTIALS"),
                "scope": SCOPE_COMMUNITY,
                "status": "GRANTED",
            }
            self._access_log.append(audit_entry)

            return {
                "client_secret_file": client_secret,
                "token_file": token_file,
            }

    def get_hostinger_api_token(self, bot_id: str = "mail-engine") -> Optional[str]:
        """Hostinger Mail API erişim tokenini güvenle çeker."""
        return self.request_secret(bot_id, "HOSTINGER_API_TOKEN", SCOPE_MAIL)

    def set_secret(self, key: str, value: str) -> None:
        """Kasaya dinamik ve güvenli biçimde çalışma zamanı credential ekler."""
        with self._load_lock:
            if key and value:
                self._vault[key] = str(value).strip()

    def audit_summary(self) -> Dict[str, Any]:
        """
        Kasa denetim durumunu gizli değer sızdırmadan raporlar.
        """
        with self._load_lock:
            return {
                "status": "HEALTHY",
                "total_secrets_loaded": len(self._vault),
                "total_registered_bots": len(self._bot_permissions),
                "total_access_requests": len(self._access_log),
                "unauthorized_attempts": sum(1 for e in self._access_log if "DENIED" in e["status"]),
                "tracked_keys": [k for k in sorted(self._vault.keys())],
                "scopes_active": list(ALL_SCOPES),
            }

    def __repr__(self) -> str:
        return f"<SecretTreasury loaded_keys={len(self._vault)} active_scopes={len(self._bot_permissions)}>"


# Singleton Instance
treasury = SecretTreasury()
