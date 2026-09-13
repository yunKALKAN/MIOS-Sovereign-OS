#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
  MIOS CORE - CENTRAL BOT DEPOT MASTER ORCHESTRATOR DAEMON
  Module       : 01_MIOS_CORE/bot_depot/daemon.py
  Version      : v2.5.0-EnterpriseDepotDaemon
  Architecture : Master Orchestration Loop for all MIOS Telegram & Service Bots
================================================================================
"""

import os
import sys
import time
import signal
import logging
import threading
from datetime import datetime, timezone

from treasury import treasury
from cfel_auditor import cfel_auditor
from event_bus import event_bus
from registry import bot_registry
from security_engine import security_engine
from health_monitor import health_monitor
from depot_dispatcher import depot_dispatcher
from live_command_bot import live_command_bot
from mioxid99_bot import mioxid99_bot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [MIOS-DEPOT] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger("MIOS.DepotMaster")


class MIOSBotDepotDaemon:
    """
    MIOS Bot Depot Merkezi Orkestrasyon ve Vardiya Yöneticisi.
    """
    def __init__(self):
        self.running = False
        self.last_daily_report_hour = -1
        self.last_shift_report_hour = -1

    def start(self):
        self.running = True
        logger.info("============================================================")
        logger.info("  🚀 MIOS CENTRAL BOT DEPOT DAEMON BAŞLATILIYOR")
        logger.info("  🏛️ Depo: MucizeWork MİOXid Operasyon Merkezi")
        logger.info("  🤖 Bot Ekibi: 6 Aktif Servis Botu Kayıtlı")
        logger.info("  📜 CFEL Defteri: Kriptografik SHA-256 Mühürleme Aktif")
        logger.info("  🔒 Secret Treasury: Korumalı / Sıfır Sızıntı")
        logger.info("============================================================")

        # CFEL Başlangıç Mührü
        cfel_auditor.seal_event(
            event_type="BOT_DEPOT_DAEMON_STARTED",
            bot_id="mios-core-master",
            action="BOOT_ORCHESTRATOR",
            result="ONLINE",
            payload={"bots_registered": len(bot_registry.list_bots())}
        )

        # Sinyal Yakalayıcılar
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

        # İlk Sistem Sağlık ve Güvenlik Taraması
        health_monitor.evaluate_system_health()
        security_engine.run_system_audit_scan()

        # İlk Başlangıç Vardiya Raporunu MİOXid Grubuna Bildir
        depot_dispatcher.broadcast_all_daily_reports()

        # Ana Yürütme Döngüsü
        loop_counter = 0
        while self.running:
            try:
                loop_counter += 1

                # 1. @MIOSLiveBot Telegram Polling (Her saniye)
                live_command_bot.poll_once()

                # 2. Kalp Atışı ve Sağlık Denetimi (Her 15 saniyede bir)
                if loop_counter % 15 == 0:
                    health_monitor.evaluate_system_health()

                # 3. Güvenlik ve Tampering Taraması (Her 60 saniyede bir)
                if loop_counter % 60 == 0:
                    security_engine.run_system_audit_scan()

                # 4. Günlük Vardiya ve Kapanış Raporu Zamanlayıcısı
                now_dt = datetime.now()
                # Her gün saat 09:00'da Günlük Rapor
                if now_dt.hour == 9 and self.last_daily_report_hour != 9:
                    logger.info("📅 Günlük Vardiya Raporu Gönderiliyor...")
                    depot_dispatcher.broadcast_all_daily_reports()
                    self.last_daily_report_hour = 9

                # Her gün saat 23:59'da Kapanış Vardiya Raporu
                if now_dt.hour == 23 and now_dt.minute >= 55 and self.last_shift_report_hour != 23:
                    logger.info("🌙 Günlük Kapanış Vardiya Raporu Gönderiliyor...")
                    depot_dispatcher.broadcast_closing_shift_report()
                    self.last_shift_report_hour = 23

                time.sleep(1.0)

            except Exception as e:
                logger.error(f"Daemon ana döngü hatası: {e}")
                time.sleep(2.0)

    def _handle_shutdown(self, signum, frame):
        logger.info(f"🛑 Kapatma sinyali alındı ({signum}), Bot Depot güvenle durduruluyor...")
        self.running = False
        cfel_auditor.seal_event(
            event_type="BOT_DEPOT_DAEMON_STOPPED",
            bot_id="mios-core-master",
            action="CLEAN_SHUTDOWN",
            result="OFFLINE"
        )
        sys.exit(0)


def main():
    daemon = MIOSBotDepotDaemon()
    daemon.start()


if __name__ == "__main__":
    main()
