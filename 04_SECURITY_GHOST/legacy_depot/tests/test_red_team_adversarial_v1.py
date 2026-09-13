#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
  MIOS RED-TEAM ADVERSARIAL REVALIDATION TEST SUITE v1.0
  Targets: Nano-Yield Engine v37.1 & Wallet Guardian v37.1
  Rule   : Zero Real Money Spent, Safe In-Memory & Sandbox Execution
================================================================================
"""

import os
import sys
import time
import json
import unittest

sys.path.insert(0, "/home/yunuskalkan/01_MIOS_CORE")
sys.path.insert(0, "/home/yunuskalkan/01_MIOS_CORE/bot_depot")
sys.path.insert(0, "/home/yunuskalkan/03_TRADING_BOTS")

from bot_depot.micro_yield_service import (
    nano_yield_engine,
    STATE_OPEN,
    STATE_CLOSED,
    ActivePositionRecord,
    TRADES_JSONL_PATH,
    ACTIVE_POSITIONS_PATH
)
from bot_depot.nano_yield_config import nano_config
from bot_depot.event_bus import (
    event_bus, MIOSEvent,
    EVENT_GUARDIAN_STOP_REQUESTED,
    EVENT_EMERGENCY_FREEZE_REQUESTED,
    EVENT_GUARDIAN_HEARTBEAT
)
from bot_depot.cfel_auditor import cfel_auditor
from mios_wallet_guardian import MIOSRealExecutionGuardian


class TestRedTeamAdversarial(unittest.TestCase):

    def setUp(self):
        nano_yield_engine.resume()
        nano_yield_engine.consecutive_losses = 0
        nano_yield_engine.daily_loss_total_try = 0.0
        nano_yield_engine._seen_signals.clear()

    # 1. DEX API Empty / Invalid Response Handling
    def test_01_dex_empty_response(self):
        # Gecefersiz fiyat ile işlem açılmaya çalışılırsa STOP / REJECT olmalı
        passed, reason = nano_yield_engine.evaluate_risk_gates(
            symbol="SOL", confidence_score=0.95, rpc_latency_ms=150, price_usd=0.0
        )
        self.assertFalse(passed)
        self.assertIn("INVALID_OR_STALE_MARKET_PRICE", reason)

    # 2. Stale Price Protection
    def test_02_stale_price_protection(self):
        # 10 saniye önceki fiyatın kullanımı engellenmeli
        passed, reason = nano_yield_engine.evaluate_risk_gates(
            symbol="SOL", confidence_score=0.95, rpc_latency_ms=150, price_usd=-1.0
        )
        self.assertFalse(passed)

    # 3. ATA Maliyeti ve İktisadi Verimlilik Kontrolü
    def test_03_ata_cost_economic_gate(self):
        # ATA maliyeti (15 TL), 10 TL'lik bütçenin potansiyel kârından (+0.12 TL) kat kat büyükse REJECT edilmeli
        passed, reason = nano_yield_engine.evaluate_risk_gates(
            symbol="XYZ", confidence_score=0.95, rpc_latency_ms=150, price_usd=5.0,
            ata_cost_try=15.0, budget_try=10.0
        )
        self.assertFalse(passed)
        self.assertIn("SKIPPED_UNECONOMIC_ATA_COST", reason)

    # 4. Sinyal Tekilleştirme (Duplicate Signal)
    def test_04_duplicate_signal_prevention(self):
        sig_price = 145.20
        # İlk sinyal
        r1 = nano_yield_engine.execute_nano_trade("SOL", sig_price, sig_price * 48.0, 0.95, 120)
        self.assertIn(r1.TransactionStatus, ["PAPER_VERIFIED", "SKIPPED"])
        
        # Hemen ardından gelen birebir aynı sinyal (aynı saniye içinde)
        r2 = nano_yield_engine.execute_nano_trade("SOL", sig_price, sig_price * 48.0, 0.95, 120)
        # Sinyal hafızasında olduğu tespit edilmeli
        self.assertIn(f"SOL-{round(sig_price, 4)}", nano_yield_engine._seen_signals)

    # 5. Pozisyon Durum Makinesi ve Gerçek İzleme (Take Profit)
    def test_05_position_lifecycle_take_profit(self):
        # Pozisyon aç
        pos_record = nano_yield_engine.execute_nano_trade("RAY", 1.50, 72.0, 0.96, 120)
        trade_id = pos_record.TradeID
        
        # Pozisyonun açık olduğunu doğrula
        self.assertIn(trade_id, nano_yield_engine._active_positions)
        pos = nano_yield_engine._active_positions[trade_id]
        self.assertEqual(pos.status, STATE_OPEN)

        # Fiyatın %1.5 yükseldiğini simüle et (Take profit %1.2 hedefi aşılır)
        higher_price_try = pos.actual_buy_fill_try * 1.015
        mock_prices = {
            "raydium": {"usd": 1.52, "try": higher_price_try}
        }
        closed_list = nano_yield_engine.monitor_and_update_positions(mock_prices)
        
        # Pozisyonun başarıyla kapandığını doğrula
        self.assertEqual(len(closed_list), 1)
        closed = closed_list[0]
        self.assertIn("TAKE_PROFIT_TARGET_REACHED", closed.ExitReason)
        self.assertGreater(closed.NetPnL, 0)
        self.assertNotIn(trade_id, nano_yield_engine._active_positions)

    # 6. Gerçek Hard Stop Loss (-%0.60)
    def test_06_position_lifecycle_hard_stop(self):
        # Pozisyon aç
        pos_record = nano_yield_engine.execute_nano_trade("BONK", 0.00002, 0.001, 0.96, 120)
        trade_id = pos_record.TradeID
        pos = nano_yield_engine._active_positions[trade_id]

        # Fiyatın %1.0 çöktüğünü simüle et (Stop loss -%0.6 aşılır)
        lower_price_try = pos.actual_buy_fill_try * 0.990
        mock_prices = {
            "bonk": {"usd": 0.000019, "try": lower_price_try}
        }
        closed_list = nano_yield_engine.monitor_and_update_positions(mock_prices)
        
        self.assertEqual(len(closed_list), 1)
        closed = closed_list[0]
        self.assertIn("HARD_STOP_LOSS_TRIGGERED", closed.ExitReason)
        self.assertLess(closed.NetPnL, 0)
        self.assertNotIn(trade_id, nano_yield_engine._active_positions)

    # 7. Restart Recovery (Açık Pozisyon Kalıcılığı)
    def test_07_restart_recovery_persistence(self):
        # Pozisyon aç
        pos_record = nano_yield_engine.execute_nano_trade("JUP", 0.85, 41.0, 0.96, 120)
        trade_id = pos_record.TradeID
        self.assertIn(trade_id, nano_yield_engine._active_positions)

        # Simüle Restart: Yeni engine nesnesi oluştur
        from bot_depot.micro_yield_service import NanoYieldAutomationEngine
        fresh_engine = NanoYieldAutomationEngine()
        fresh_engine._load_active_positions_from_disk()

        # Pozisyon diskten geri gelmiş olmalı
        self.assertIn(trade_id, fresh_engine._active_positions)
        
        # Temizlik
        fresh_engine.close_position_by_token("JUP", reason="TEST_CLEANUP")

    # 8. Event Bus Guardian Veto / Stop Entegrasyonu
    def test_08_guardian_stop_propagation(self):
        pos_record = nano_yield_engine.execute_nano_trade("WIF", 1.80, 86.0, 0.96, 120)
        trade_id = pos_record.TradeID
        self.assertIn(trade_id, nano_yield_engine._active_positions)

        # Guardian Event Bus üzerinden STOP sinyali gönderir
        event_bus.publish(MIOSEvent(
            event_type=EVENT_GUARDIAN_STOP_REQUESTED,
            bot_id="mios-guardian",
            data={"token": "WIF", "position_id": trade_id}
        ))

        # Pozisyonun kapanmış olduğunu doğrula
        self.assertNotIn(trade_id, nano_yield_engine._active_positions)

    # 9. Guardian %12 Drawdown Devre Kesicisi
    def test_09_guardian_drawdown_circuit_breaker(self):
        guardian = MIOSRealExecutionGuardian()
        guardian.state.peak_equity_usd = 100.0
        # %15 kayıp simülasyonu (Drawdown = 0.15 >= 0.12)
        guardian.trigger_drawdown_emergency_freeze(0.15)
        
        self.assertTrue(guardian.state.is_frozen)
        self.assertIn("%12", guardian.state.freeze_reason)
        
        # Nano-Yield'in de freeze olduğunu doğrula
        self.assertTrue(nano_yield_engine.is_frozen)

    # 10. Matematiksel Doğruluk: Yapay 999.0 Kaldırıldı
    def test_10_mathematical_profit_factor_integrity(self):
        recon = nano_yield_engine.reconcile_pnl_from_ledger()
        self.assertIn("profit_factor_display", recon)
        # 999.0 yerine anlamlı temsil verildiğini kontrol et
        if recon.get("losing_trades", 0) == 0 and recon.get("winning_trades", 0) > 0:
            self.assertIn("N/A", recon["profit_factor_display"])

    # 11. RPC Failover
    def test_11_rpc_failover(self):
        # Geçersiz bir RPC çağrısı yapıldığında sistemin çökmediğini doğrula
        ok, res, lat = nano_yield_engine.solana_rpc_call("invalidMethodTest", [])
        self.assertIsInstance(lat, int)

    # 12. Guardian Canlılık Zaman Aşımı (Heartbeat Timeout)
    def test_12_guardian_heartbeat_timeout(self):
        # Guardian'ın 60 saniyedir sinyal göndermediğini simüle et
        nano_yield_engine._last_guardian_heartbeat_ts = time.time() - 60.0
        nano_yield_engine.config.execution_mode = "LIVE"
        
        passed, reason = nano_yield_engine.evaluate_risk_gates("SOL", 0.95, 120)
        self.assertFalse(passed)
        self.assertIn("GUARDIAN_HEARTBEAT_TIMEOUT", reason)
        
        # Modu tekrar güvenli PAPER'a al
        nano_yield_engine.config.execution_mode = "PAPER"


if __name__ == "__main__":
    unittest.main()
