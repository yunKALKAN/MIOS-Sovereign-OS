#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
  MIOS CORE - CENTRAL BOT REGISTRY
  Module       : 01_MIOS_CORE/bot_depot/registry.py
  Version      : v2.5.0-EnterpriseBotRegistry
  Architecture : Centralized Registry of all MIOS Telegram & Service Bots
  Security Rule: NEVER STORE SECRET VALUES IN REGISTRY.
                 Stores: BOT_ID, NAME, TYPE, STATUS, OWNER, TELEGRAM_USERNAME,
                         PROCESS, VERSION, LAST_SEEN, HEALTH, PERMISSIONS,
                         SECRET_SCOPE, METRICS, TIER, MAINTENANCE_MODE.
================================================================================
"""

import os
import json
import time
import threading
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

REGISTRY_STATE_FILE = "/root/MIOS_SOVEREIGN_OS/04_SECURITY_GHOST/legacy_depot/data/registry_state.json"

from treasury import (
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
)

# Central Version Authority Integration
try:
    if "/home/yunuskalkan/01_MIOS_CORE" not in sys.path:
        sys.path.insert(0, "/home/yunuskalkan/01_MIOS_CORE")
    from version_authority import version_authority
    BOTDEPOT_MASTER_VERSION = version_authority.get_component_version("bot_service")
except Exception:
    BOTDEPOT_MASTER_VERSION = "18.5.0-botdepot.v37"


@dataclass
class BotMetrics:
    commands: int = 0
    events: int = 0
    errors: int = 0
    warnings: int = 0
    security_events: int = 0
    unauthorized_attempts: int = 0
    config_changes: int = 0
    restarts: int = 0
    last_health_check: str = ""
    start_time: float = field(default_factory=time.time)

    def uptime_str(self) -> str:
        elapsed = int(time.time() - self.start_time)
        hours = elapsed // 3600
        mins = (elapsed % 3600) // 60
        return f"{hours:02d}h {mins:02d}m"


@dataclass
class BotDescriptor:
    bot_id: str
    name: str
    type: str
    status: str
    owner: str
    telegram_username: str
    process: str
    version: str
    last_seen: str
    health: float
    permissions: List[str]
    secret_scope: str
    tier: str = "PRO"
    maintenance_mode: bool = False
    maintenance_reason: str = ""
    lineage_version: str = ""
    metrics: BotMetrics = field(default_factory=BotMetrics)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bot_id": self.bot_id,
            "name": self.name,
            "type": self.type,
            "status": self.status,
            "owner": self.owner,
            "telegram_username": self.telegram_username,
            "process": self.process,
            "version": self.version,
            "lineage_version": self.lineage_version,
            "last_seen": self.last_seen,
            "health": self.health,
            "health_pct": f"{self.health:.1f}%",
            "tier": self.tier,
            "maintenance_mode": self.maintenance_mode,
            "maintenance_reason": self.maintenance_reason,
            "permissions": self.permissions,
            "secret_scope": self.secret_scope,
            "uptime": self.metrics.uptime_str(),
            "metrics": asdict(self.metrics),
        }


class BotRegistry:
    """
    MIOS Core Merkezi Bot Kayıt Defteri.
    Tüm bot servislerinin durumlarını, sağlık oranlarını, paket seviyelerini ve bakım modlarını yönetir.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(BotRegistry, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._bots: Dict[str, BotDescriptor] = {}
        self._system_tier: str = "PRO"
        self._global_maintenance: bool = False
        self._global_maintenance_reason: str = ""
        self._registry_lock = threading.RLock()
        self._register_initial_team()
        self._initialized = True

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")

    def _register_initial_team(self) -> None:
        """İlk 6 MIOS botunu v2.5.0-Enterprise sürümüyle merkezi kayıt defterine tanımlar."""
        now = self._now_iso()

        initial_team = [
            BotDescriptor(
                bot_id="mios-live-command",
                name="MIOS Live Command",
                type="COMMAND_INTERFACE",
                status="ONLINE",
                owner="MIOS Core",
                telegram_username="@MIOSLiveBot",
                process="bot_depot.live_command_bot",
                version=BOTDEPOT_MASTER_VERSION,
                lineage_version="v2.5.0-LiveCommand",
                last_seen=now,
                health=99.9,
                permissions=["user_command_handling", "interactive_menu", "telemetry_query", "shift_reporting", "upsell_engine"],
                secret_scope=SCOPE_LIVE_COMMAND,
                tier="PRO",
            ),
            BotDescriptor(
                bot_id="mioxid-99",
                name="MİOXid 99",
                type="LEGACY_RUNTIME_BRIDGE",
                status="ONLINE",
                owner="MIOS Core",
                telegram_username="@mucizework_runtime_bot",
                process="bot_depot.mioxid99_bot",
                version=BOTDEPOT_MASTER_VERSION,
                lineage_version="v2.5.0-MioxiD99",
                last_seen=now,
                health=99.9,
                permissions=["runtime_notification_broadcast", "legacy_bridge", "upsell_broadcast"],
                secret_scope=SCOPE_MIOXID_99,
                tier="ENTERPRISE",
            ),
            BotDescriptor(
                bot_id="mios-guardian",
                name="MIOS Guardian",
                type="RISK_WALLET_PROTECTOR",
                status="ONLINE",
                owner="MIOS Core",
                telegram_username="internal",
                process="03_TRADING_BOTS/mios_wallet_guardian.py",
                version=BOTDEPOT_MASTER_VERSION,
                lineage_version="v2.5.0-LiveGuardian",
                last_seen=now,
                health=99.9,
                permissions=["wallet_monitoring", "trailing_profit_lock", "emergency_halt"],
                secret_scope=SCOPE_GUARDIAN,
                tier="PRO",
            ),
            BotDescriptor(
                bot_id="mios-signal",
                name="MIOS Signal",
                type="SIGNAL_TRADING_ENGINE",
                status="ONLINE",
                owner="MIOS Core",
                telegram_username="internal",
                process="bot.py (solana-sniper)",
                version=BOTDEPOT_MASTER_VERSION,
                lineage_version="v36.0-EnterpriseSniper",
                last_seen=now,
                health=99.9,
                permissions=["market_analysis", "ml_inference", "dex_execution"],
                secret_scope=SCOPE_SIGNAL,
                tier="ENTERPRISE",
            ),
            BotDescriptor(
                bot_id="mios-telemetry",
                name="MIOS Telemetry",
                type="TELEMETRY_SYNC_ENGINE",
                status="ONLINE",
                owner="MIOS Core",
                telegram_username="internal",
                process="05_SCRIPTS/sync_telemetry.py",
                version=BOTDEPOT_MASTER_VERSION,
                lineage_version="v2.5.0-CoreTelemetry",
                last_seen=now,
                health=99.9,
                permissions=["state_normalization", "remote_sync", "metrics_aggregation"],
                secret_scope=SCOPE_TELEMETRY,
                tier="ENTERPRISE",
            ),
            BotDescriptor(
                bot_id="mios-cfel",
                name="MIOS CFEL",
                type="FORENSIC_AUDIT_LEDGER",
                status="ONLINE",
                owner="MIOS Core",
                telegram_username="internal",
                process="01_MIOS_CORE/cfel_auditor.py",
                version=BOTDEPOT_MASTER_VERSION,
                lineage_version="v2.5.0-CFEL",
                last_seen=now,
                health=100.0,
                permissions=["cryptographic_hashing", "evidence_sealing", "integrity_audit", "upsell_provenance"],
                secret_scope=SCOPE_CFEL,
                tier="ENTERPRISE",
            ),
            BotDescriptor(
                bot_id="solana-nano-sniper",
                name="MIOS Nano-Yield Engine",
                type="NANO_YIELD_AUTOMATION",
                status="ONLINE",
                owner="MIOS Core",
                telegram_username="internal",
                process="01_MIOS_CORE/bot_depot/micro_yield_service.py",
                version=BOTDEPOT_MASTER_VERSION,
                lineage_version="v37.0-EnterpriseNano",
                last_seen=now,
                health=100.0,
                permissions=["nano_yield_execution", "real_data_feed", "cfel_sealing", "risk_gate_enforcement"],
                secret_scope=SCOPE_SIGNAL,
                tier="PRO",
            ),
            BotDescriptor(
                bot_id="mucizework-youtube-worker",
                name="MucizeWORK YouTube Media Engine",
                type="MEDIA_COMMUNITY_ENGINE",
                status="VETO_BLOCKED",
                owner="MIOS Core",
                telegram_username="@mucizeworkxis",
                process="MucizeWORK_Ekosistem_TV/app/worker.py",
                version=BOTDEPOT_MASTER_VERSION,
                lineage_version="v1.0.0-MediaOrchestra",
                last_seen=now,
                health=100.0,
                permissions=[
                    "youtube_media_pipeline",
                    "content_ingestion",
                    "privacy_compliance",
                    "metadata_optimization",
                    "shorts_derivation",
                    "community_contracts",
                    "cfel_evidence_sealing",
                    "analytics_telemetry",
                ],
                secret_scope=SCOPE_COMMUNITY,
                tier="ENTERPRISE",
                maintenance_mode=False,
                maintenance_reason="Kanal yetkilendirmesi bekleniyor (@mucizeworkxis)",
            ),
            BotDescriptor(
                bot_id="mucizework-linkedin-worker",
                name="MucizeWORK LinkedIn Media Engine",
                type="LINKEDIN_MEDIA_ENGINE",
                status="DISABLED_WAITING_AUTH",
                owner="MIOS Core",
                telegram_username="internal",
                process="MucizeWORK_Ekosistem_TV/app/linkedin/worker.py",
                version=BOTDEPOT_MASTER_VERSION,
                lineage_version="v1.0.0-LinkedInOrchestra",
                last_seen=now,
                health=100.0,
                permissions=[
                    "linkedin_posts_api",
                    "member_social_publishing",
                    "profile_verification",
                    "cfel_evidence_sealing",
                    "dry_run_simulation",
                ],
                secret_scope=SCOPE_MEDIA,
                tier="ENTERPRISE",
                maintenance_mode=False,
                maintenance_reason="LinkedIn OAuth ve üye URN doğrulaması bekleniyor",
            ),
            BotDescriptor(
                bot_id="mios-mail-engine",
                name="MIOS Mail & Communication Engine",
                type="MAIL_COMMUNICATION_ENGINE",
                status="ONLINE_READY",
                owner="MIOS Core",
                telegram_username="internal",
                process="01_MIOS_CORE/mail_engine/engine.py",
                version=BOTDEPOT_MASTER_VERSION,
                lineage_version="v2.0.0-MucizeWORK-Hostinger",
                last_seen=now,
                health=100.0,
                permissions=[
                    "smtp_ssl_465",
                    "smtp_starttls_587",
                    "imap_ssl_993",
                    "hostinger_api_discovery",
                    "multi_domain_routing",
                    "event_bus_publishing",
                    "cfel_evidence_sealing",
                    "role_policy_enforcement",
                ],
                secret_scope=SCOPE_MAIL,
                tier="ENTERPRISE",
                maintenance_mode=False,
                maintenance_reason="",
            ),
            BotDescriptor(
                bot_id="maymuncuk-business-engine",
                name="Maymuncuk Adaptive Business Engine",
                type="ADAPTIVE_BUSINESS_ENGINE",
                status="ONLINE",
                owner="MIOS Core",
                telegram_username="internal",
                process="maymuncuk/app/src/server.js",
                version=BOTDEPOT_MASTER_VERSION,
                lineage_version="v1.0.0-Maymuncuk",
                last_seen=now,
                health=100.0,
                permissions=[
                    "dna_analysis",
                    "workflow_generation",
                    "adaptive_onboarding",
                    "business_operations",
                    "cfel_evidence_sealing",
                ],
                secret_scope=SCOPE_SECURITY,
                tier="ENTERPRISE",
                maintenance_mode=False,
                maintenance_reason="",
            ),
            BotDescriptor(
                bot_id="mios-web-portal-engine",
                name="MIOS Web & SaaS Portal Engine",
                type="WEB_SAAS_INTERFACE",
                status="ONLINE",
                owner="MIOS Core",
                telegram_username="internal",
                process="chat_mios_engine.py / nginx",
                version=BOTDEPOT_MASTER_VERSION,
                lineage_version="v1.0.0-WebPortals",
                last_seen=now,
                health=100.0,
                permissions=[
                    "landing_portal",
                    "pricing_engine",
                    "passport_identity",
                    "wallet_view",
                    "chat_ai_interface",
                    "cfel_audit_view",
                ],
                secret_scope=SCOPE_COMMUNITY,
                tier="PRO",
                maintenance_mode=False,
                maintenance_reason="",
            ),
        ]

        for bot in initial_team:
            bot.metrics.last_health_check = now
            self._bots[bot.bot_id] = bot

    def register_bot(self, descriptor: BotDescriptor) -> None:
        """Yeni bir servis botunu güvenle kaydeder."""
        with self._registry_lock:
            descriptor.last_seen = self._now_iso()
            descriptor.metrics.last_health_check = self._now_iso()
            self._bots[descriptor.bot_id] = descriptor

    def get_bot(self, bot_id: str) -> Optional[BotDescriptor]:
        with self._registry_lock:
            return self._bots.get(bot_id)

    def list_bots(self) -> List[BotDescriptor]:
        with self._registry_lock:
            return list(self._bots.values())

    def update_heartbeat(self, bot_id: str, status: str = "ONLINE") -> None:
        """Bot kalp atışını ve durumunu günceller."""
        with self._registry_lock:
            bot = self._bots.get(bot_id)
            if bot:
                bot.last_seen = self._now_iso()
                if not bot.maintenance_mode:
                    bot.status = status

    def update_health(self, bot_id: str, health_score: float) -> None:
        """Bot sağlık skorunu günceller."""
        with self._registry_lock:
            bot = self._bots.get(bot_id)
            if bot:
                bot.health = max(0.0, min(100.0, float(health_score)))
                bot.metrics.last_health_check = self._now_iso()

    def record_metric(self, bot_id: str, metric_name: str, delta: int = 1) -> None:
        """Bot operasyonel sayaçlarını (events, commands, errors vs.) artırır."""
        with self._registry_lock:
            bot = self._bots.get(bot_id)
            if bot and hasattr(bot.metrics, metric_name):
                curr = getattr(bot.metrics, metric_name)
                setattr(bot.metrics, metric_name, curr + delta)

    def set_status(self, bot_id: str, status: str) -> None:
        with self._registry_lock:
            bot = self._bots.get(bot_id)
            if bot:
                bot.status = status
                bot.last_seen = self._now_iso()

    def _save_state(self) -> None:
        """Kayıt defteri bakım ve servis durumunu diske yazar."""
        try:
            os.makedirs(os.path.dirname(REGISTRY_STATE_FILE), exist_ok=True)
            state = {
                "global_maintenance": self._global_maintenance,
                "global_maintenance_reason": self._global_maintenance_reason,
                "bots": {
                    b_id: {
                        "status": b.status,
                        "maintenance_mode": b.maintenance_mode,
                        "maintenance_reason": b.maintenance_reason
                    }
                    for b_id, b in self._bots.items()
                }
            }
            with open(REGISTRY_STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def _load_state(self) -> None:
        """Diskteki kayıt defteri durumunu yükler."""
        if not os.path.exists(REGISTRY_STATE_FILE):
            return
        try:
            with open(REGISTRY_STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
            self._global_maintenance = state.get("global_maintenance", False)
            self._global_maintenance_reason = state.get("global_maintenance_reason", "")
            bots_state = state.get("bots", {})
            for b_id, s in bots_state.items():
                if b_id in self._bots:
                    self._bots[b_id].status = s.get("status", self._bots[b_id].status)
                    self._bots[b_id].maintenance_mode = s.get("maintenance_mode", False)
                    self._bots[b_id].maintenance_reason = s.get("maintenance_reason", "")
        except Exception:
            pass

    def set_maintenance_mode(self, bot_id: Optional[str] = None, enabled: bool = True, reason: str = "Planlı Servis & Sürüm Yükseltme") -> None:
        """Belirtilen botu veya tüm ekibi bakım / servis moduna alır veya moddan çıkarır."""
        with self._registry_lock:
            now = self._now_iso()
            if bot_id is None:
                self._global_maintenance = enabled
                self._global_maintenance_reason = reason if enabled else ""
                for bot in self._bots.values():
                    bot.maintenance_mode = enabled
                    bot.maintenance_reason = reason if enabled else ""
                    bot.status = "MAINTENANCE" if enabled else "ONLINE"
                    bot.last_seen = now
            else:
                bot = self._bots.get(bot_id)
                if bot:
                    bot.maintenance_mode = enabled
                    bot.maintenance_reason = reason if enabled else ""
                    bot.status = "MAINTENANCE" if enabled else "ONLINE"
                    bot.last_seen = now
            self._save_state()

    def is_maintenance_mode(self, bot_id: Optional[str] = None) -> bool:
        with self._registry_lock:
            self._load_state()
            if bot_id is None:
                return self._global_maintenance
            bot = self._bots.get(bot_id)
            return (bot.maintenance_mode if bot else False) or self._global_maintenance

    def generate_agents_view(self) -> str:
        """
        MIOS Core /agents komutunun tam format çıktısını üretir.
        """
        with self._registry_lock:
            self._load_state()
            lines = ["🤖 *MIOS BOT TEAM*", ""]
            if self._global_maintenance:
                lines.append("⚠️ *[GENEL BAKIM & SERVİS MODU AKTİF]*")
                lines.append(f"📌 Sebep: _{self._global_maintenance_reason}_\n")

            for bot in self._bots.values():
                if bot.maintenance_mode or bot.status == "MAINTENANCE":
                    icon = "🛠️"
                    stat_txt = f"BAKIMDA / SERVİSTE ({bot.maintenance_reason or 'Yükseltme'})"
                elif bot.status == "ONLINE":
                    icon = "🟢"
                    stat_txt = f"ONLINE [Çekirdek Altyapı / {bot.tier}]"
                elif bot.status == "STANDBY":
                    icon = "🟡"
                    stat_txt = f"STANDBY [Çekirdek Altyapı / {bot.tier}]"
                else:
                    icon = "🔴"
                    stat_txt = f"OFFLINE [Çekirdek Altyapı / {bot.tier}]"

                lines.append(f"{icon} *{bot.name}* (`{bot.version}`)")
                lines.append(f"   {stat_txt}")
                lines.append(f"   HEALTH: {bot.health:.1f}%\n")
            return "\n".join(lines).strip()

    def to_dict(self) -> Dict[str, Any]:
        """Tüm registry durumunu telemetri ve API için serialize eder."""
        with self._registry_lock:
            self._load_state()
            bots_list = [bot.to_dict() for bot in self._bots.values()]
            online_count = sum(1 for b in self._bots.values() if b.status == "ONLINE")
            offline_count = sum(1 for b in self._bots.values() if b.status == "OFFLINE")
            maint_count = sum(1 for b in self._bots.values() if b.status == "MAINTENANCE" or b.maintenance_mode)
            avg_health = sum(b.health for b in self._bots.values()) / max(1, len(self._bots))

            return {
                "total_bots": len(self._bots),
                "online_bots": online_count,
                "offline_bots": offline_count,
                "maintenance_bots": maint_count,
                "global_maintenance": self._global_maintenance,
                "global_maintenance_reason": self._global_maintenance_reason,
                "average_health_pct": round(avg_health, 2),
                "system_status": "MAINTENANCE" if self._global_maintenance else ("NORMAL" if offline_count == 0 else "ATTENTION_REQUIRED"),
                "bots": bots_list,
            }


# Singleton Instance
bot_registry = BotRegistry()
