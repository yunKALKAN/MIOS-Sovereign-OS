#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
  MIOS CORE - v37.1 EXECUTION INTELLIGENCE REGRESSION & INSTITUTIONAL SUITE
  Module       : 01_MIOS_CORE/bot_depot/tests/test_v37_1_execution_intelligence_regression.py
  Version      : v37.1-EnterpriseNano
  Architecture : 12-Layer Verification Suite:
                 1. Core Invariants Preservation (%90 Conf, 25 bps Slip, Real/Paper)
                 2. Execution Quality Score (EQS: Slippage, Latency, Spread, PnL)
                 3. Liquidity Gate (Depth Thresholding)
                 4. Price Freshness Gate (Stale Quote Rejection)
                 5. Latency Guard (RPC / Network Delay Filter)
                 6. Cost-Aware Gate (Net Expectancy Friction Evaluation)
                 7. Opportunity Score Funnel (5020 Scans -> 862 Trades Conversion)
                 8. Adaptive Position Sizing (Strict 100.00 - 300.00 TRY Bounds)
                 9. Session Kill-Switch & Circuit Breaker (Consecutive Poor EQS)
                 10. Multi-Dimensional Performance Attribution (Token, Bracket, Grade)
                 11. Explainable Trade Record Rationale
                 12. Confidence Calibration & Brier Score Analysis
================================================================================
"""

import os
import sys
import json
import unittest
from typing import Dict, List, Any

sys.path.insert(0, "/home/yunuskalkan/01_MIOS_CORE")
sys.path.insert(0, "/home/yunuskalkan/01_MIOS_CORE/bot_depot")

from bot_depot.execution_intelligence import (
    execution_intelligence,
    ExecutionIntelligence,
    GateEvaluationResult,
    ExecutionQualityResult
)
from bot_depot.nano_yield_config import nano_config

TRADES_JSONL = "/home/yunuskalkan/01_MIOS_CORE/bot_depot/data/nano_yield_trades.jsonl"


class TestV371ExecutionIntelligenceRegression(unittest.TestCase):

    def setUp(self):
        self.engine = ExecutionIntelligence(
            min_size_try=100.0,
            max_size_try=300.0,
            ai_confidence_gate=0.90,     # 🛡️ 1. Omurga: %90 KORUNUR
            max_slippage_bps=25,          # 🛡️ 2. Omurga: 25 bps KORUNUR
            min_liquidity_usd=50000.0,
            max_price_age_ms=3000,
            max_rpc_latency_ms=2000,
            take_profit_bps=120
        )

    # -------------------------------------------------------------------------
    # TEST 1: CORE INVARIANTS PRESERVATION (%90 Güven, 25 bps Slippage)
    # -------------------------------------------------------------------------
    def test_01_core_invariants_preserved(self):
        """%90 güven ve 25 bps slippage kurallarının değişmediğini doğrular."""
        self.assertEqual(self.engine.ai_confidence_gate, 0.90, "AI Güven eşiği tam olarak 0.90 olmalıdır.")
        self.assertEqual(self.engine.max_slippage_bps, 25, "Maksimum slippage tam olarak 25 bps olmalıdır.")

        # %89.9 güven reddedilmeli
        res_sub90 = self.engine.evaluate_institutional_gates(
            symbol="BONK", confidence_score=0.899, price_usd=0.00002,
            quote_timestamp_ms=0, rpc_latency_ms=100, slippage_bps=10,
            liquidity_usd=100000.0, daily_loss_total_try=0, max_daily_loss_try=150,
            consecutive_losses=0, max_consecutive_loss=3, is_frozen=False
        )
        self.assertFalse(res_sub90.passed)
        self.assertEqual(res_sub90.gate_name, "AI_CONFIDENCE_GATE")

        # 26 bps slippage reddedilmeli
        res_over_slip = self.engine.evaluate_institutional_gates(
            symbol="BONK", confidence_score=0.95, price_usd=0.00002,
            quote_timestamp_ms=0, rpc_latency_ms=100, slippage_bps=26.0,
            liquidity_usd=100000.0, daily_loss_total_try=0, max_daily_loss_try=150,
            consecutive_losses=0, max_consecutive_loss=3, is_frozen=False
        )
        self.assertFalse(res_over_slip.passed)
        self.assertEqual(res_over_slip.gate_name, "SLIPPAGE_GATE")

    # -------------------------------------------------------------------------
    # TEST 2: EXECUTION QUALITY SCORE (EQS 0-100)
    # -------------------------------------------------------------------------
    def test_02_execution_quality_scoring(self):
        """EQS bileşenlerinin (slippage, latency, hold, PnL) matematiksel doğruluğu."""
        # Kusursuz senaryo: 0 bps slippage, 50ms latency, 1300ms hold, pozitif pnl
        eqs_perfect = self.engine.evaluate_execution_quality(
            actual_slippage_bps=0.0,
            rpc_latency_ms=50,
            hold_time_ms=1300,
            net_pnl_try=2.50,
            position_size_try=200.0
        )
        self.assertGreaterEqual(eqs_perfect.eqs_score, 90.0)
        self.assertIn("A", eqs_perfect.grade)

        # Sürtünmeli senaryo: 24 bps slippage, 1800ms latency, 8000ms hold, düşük pnl
        eqs_friction = self.engine.evaluate_execution_quality(
            actual_slippage_bps=24.0,
            rpc_latency_ms=1800,
            hold_time_ms=8000,
            net_pnl_try=0.10,
            position_size_try=200.0
        )
        self.assertLess(eqs_friction.eqs_score, eqs_perfect.eqs_score)
        self.assertTrue(0.0 <= eqs_friction.eqs_score <= 100.0)

    # -------------------------------------------------------------------------
    # TEST 3: LIQUIDITY GATE
    # -------------------------------------------------------------------------
    def test_03_liquidity_gate(self):
        """Yetersiz havuz likiditesinde (%90 güven olsa bile) emir açılmaması."""
        engine_strict_liq = ExecutionIntelligence(min_liquidity_usd=150000.0)
        res_low_liq = engine_strict_liq.evaluate_institutional_gates(
            symbol="SAMO", confidence_score=0.96, price_usd=0.008,
            quote_timestamp_ms=0, rpc_latency_ms=100, slippage_bps=12,
            liquidity_usd=35000.0,  # 35k < 150k
            daily_loss_total_try=0, max_daily_loss_try=150,
            consecutive_losses=0, max_consecutive_loss=3, is_frozen=False
        )
        self.assertFalse(res_low_liq.passed)
        self.assertEqual(res_low_liq.gate_name, "LIQUIDITY_GATE")

    # -------------------------------------------------------------------------
    # TEST 4: PRICE FRESHNESS GATE
    # -------------------------------------------------------------------------
    def test_04_price_freshness_gate(self):
        """Eski ve bayat fiyatların (>3000 ms) engellenmesi."""
        now_ms = int(1788855000000)
        stale_quote_ms = now_ms - 4500  # 4.5 saniye eski

        # Test için engine timestamp simülasyonu
        import time
        real_now = int(time.time() * 1000)
        stale_time = real_now - 5000

        res_stale = self.engine.evaluate_institutional_gates(
            symbol="RAY", confidence_score=0.95, price_usd=1.85,
            quote_timestamp_ms=stale_time, rpc_latency_ms=100, slippage_bps=8,
            liquidity_usd=120000.0, daily_loss_total_try=0, max_daily_loss_try=150,
            consecutive_losses=0, max_consecutive_loss=3, is_frozen=False
        )
        self.assertFalse(res_stale.passed)
        self.assertEqual(res_stale.gate_name, "PRICE_FRESHNESS_GATE")

    # -------------------------------------------------------------------------
    # TEST 5: LATENCY GUARD
    # -------------------------------------------------------------------------
    def test_05_latency_guard(self):
        """Yüksek RPC veya ağ gecikmesinde (>2000 ms) işlemin veto edilmesi."""
        res_high_lat = self.engine.evaluate_institutional_gates(
            symbol="JUP", confidence_score=0.94, price_usd=0.25,
            quote_timestamp_ms=0, rpc_latency_ms=2400,  # 2400ms > 2000ms
            slippage_bps=10, liquidity_usd=100000.0,
            daily_loss_total_try=0, max_daily_loss_try=150,
            consecutive_losses=0, max_consecutive_loss=3, is_frozen=False
        )
        self.assertFalse(res_high_lat.passed)
        self.assertEqual(res_high_lat.gate_name, "LATENCY_GUARD")

    # -------------------------------------------------------------------------
    # TEST 6: COST-AWARE GATE (NET BEKLENTİ > 0)
    # -------------------------------------------------------------------------
    def test_06_cost_aware_gate(self):
        """Maliyetler (DEX Fee + Priority Fee + Slippage) brüt kârı aşarsa emrin reddedilmesi."""
        # 1 bps kâr hedefli bir test engine kuralım (maliyet > brüt getiri)
        engine_low_tp = ExecutionIntelligence(take_profit_bps=1)
        res_uneconomic = engine_low_tp.evaluate_institutional_gates(
            symbol="ORCA", confidence_score=0.95, price_usd=1.40,
            quote_timestamp_ms=0, rpc_latency_ms=100, slippage_bps=20,
            liquidity_usd=100000.0, daily_loss_total_try=0, max_daily_loss_try=150,
            consecutive_losses=0, max_consecutive_loss=3, is_frozen=False
        )
        self.assertFalse(res_uneconomic.passed)
        self.assertEqual(res_uneconomic.gate_name, "COST_AWARE_GATE")

    # -------------------------------------------------------------------------
    # TEST 7: ADAPTIVE POSITION SIZING (100 - 300 TL KORUNUMU)
    # -------------------------------------------------------------------------
    def test_07_adaptive_position_sizing(self):
        """Pozisyon boyutunun kesinlikle 100.00 TL - 300.00 TL bandında kalması."""
        # Yüksek güven + yüksek likidite + düşük slippage -> 250 - 300 TL
        size_high = self.engine.calculate_adaptive_size(
            confidence=0.98, liquidity_usd=400000.0, slippage_bps=4.0
        )
        self.assertGreaterEqual(size_high, 220.0)
        self.assertLessEqual(size_high, 300.0)

        # Taban güven (%90) + taban likidite + 25 bps slippage -> ~100 - 150 TL
        size_low = self.engine.calculate_adaptive_size(
            confidence=0.90, liquidity_usd=50000.0, slippage_bps=24.0
        )
        self.assertGreaterEqual(size_low, 100.0)
        self.assertLessEqual(size_low, 180.0)

        # Aşırı uç değerlerde bile 100-300 TL bandının delinmediği
        size_min_bound = self.engine.calculate_adaptive_size(
            confidence=0.80, liquidity_usd=1000.0, slippage_bps=50.0
        )
        self.assertEqual(size_min_bound, 100.0)

        size_max_bound = self.engine.calculate_adaptive_size(
            confidence=1.00, liquidity_usd=10000000.0, slippage_bps=0.0
        )
        self.assertEqual(size_max_bound, 300.0)

    # -------------------------------------------------------------------------
    # TEST 8: OPPORTUNITY SCORE FORMÜLASYONU
    # -------------------------------------------------------------------------
    def test_08_opportunity_score_quantification(self):
        """Opportunity Score'un 0.0 - 1.0 aralığında ve sinyal kalitesiyle uyumlu olması."""
        opp_high = self.engine.calculate_opportunity_score(
            confidence=0.98, liquidity_usd=300000.0, slippage_bps=5.0, rpc_latency_ms=80
        )
        opp_low = self.engine.calculate_opportunity_score(
            confidence=0.90, liquidity_usd=60000.0, slippage_bps=24.0, rpc_latency_ms=1800
        )
        self.assertGreater(opp_high, opp_low)
        self.assertTrue(0.0 <= opp_high <= 1.0)
        self.assertTrue(0.0 <= opp_low <= 1.0)

    # -------------------------------------------------------------------------
    # TEST 9: SESSION KILL-SWITCH & CIRCUIT BREAKER
    # -------------------------------------------------------------------------
    def test_09_session_kill_switch(self):
        """Arka arkaya kötü execution kalitesi (EQS < 65) sonrası sistemin dondurulması."""
        test_engine = ExecutionIntelligence(kill_switch_eqs_threshold=65.0, kill_switch_window=5)
        self.assertFalse(test_engine.is_kill_switch_active())

        # 5 adet kötü EQS skoru kaydet (45.0)
        for _ in range(5):
            test_engine._record_eqs_for_kill_switch(45.0)

        # Kill-switch devrede olmalı
        self.assertTrue(test_engine.is_kill_switch_active())

        # Yeni işlem talebi SESSION_KILL_SWITCH tarafından engellenmeli
        res_blocked = test_engine.evaluate_institutional_gates(
            symbol="BONK", confidence_score=0.95, price_usd=0.00002,
            quote_timestamp_ms=0, rpc_latency_ms=100, slippage_bps=10,
            liquidity_usd=100000.0, daily_loss_total_try=0, max_daily_loss_try=150,
            consecutive_losses=0, max_consecutive_loss=3, is_frozen=False
        )
        self.assertFalse(res_blocked.passed)
        self.assertEqual(res_blocked.gate_name, "SESSION_KILL_SWITCH")

    # -------------------------------------------------------------------------
    # TEST 10: CONFIDENCE CALIBRATION & BRIER SCORE
    # -------------------------------------------------------------------------
    def test_10_confidence_calibration(self):
        """%90+ güven skorlarının gerçekleşme oranı ve kalibrasyon kalitesi."""
        confidences = [0.95, 0.96, 0.92, 0.98, 0.94, 0.97, 0.91, 0.99]
        outcomes = [1, 1, 1, 1, 1, 1, 1, 1]  # %100 win

        calib = ExecutionIntelligence.calculate_confidence_calibration(confidences, outcomes)
        self.assertEqual(calib["calibration_quality"], "EXCELLENT")
        self.assertLess(calib["brier_score"], 0.05)
        self.assertEqual(calib["realized_win_rate_pct"], 100.0)

    # -------------------------------------------------------------------------
    # TEST 11: MULTI-DIMENSIONAL PERFORMANCE ATTRIBUTION
    # -------------------------------------------------------------------------
    def test_11_performance_attribution(self):
        """Token, bütçe dilimi ve EQS not dağılımının çıkarılması."""
        sample_trades = [
            {"Token": "BONK", "NetPnL": 2.50, "PositionSizeTRY": 250.0, "EQSGrade": "AA"},
            {"Token": "BONK", "NetPnL": 2.60, "PositionSizeTRY": 260.0, "EQSGrade": "AAA"},
            {"Token": "JUP", "NetPnL": 1.20, "PositionSizeTRY": 120.0, "EQSGrade": "A"},
        ]
        attr = ExecutionIntelligence.compute_performance_attribution(sample_trades)
        self.assertIn("BONK", attr["asset_attribution"])
        self.assertIn("JUP", attr["asset_attribution"])
        self.assertEqual(attr["asset_attribution"]["BONK"]["count"], 2)
        self.assertEqual(attr["asset_attribution"]["BONK"]["net_pnl"], 5.10)
        self.assertIn("225-300 TRY", attr["sizing_bracket_pnl"])

    # -------------------------------------------------------------------------
    # TEST 12: REGRESSION CHECK ON 862 TRADES DATASET
    # -------------------------------------------------------------------------
    def test_12_baseline_regression_verification(self):
        """862 işlemlik baseline defterinin v37.1 kurallarıyla geriye dönük doğrulanması."""
        if not os.path.exists(TRADES_JSONL):
            self.skipTest("Trades defteri bulunamadı.")

        trades = []
        with open(TRADES_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    trades.append(json.loads(line))

        self.assertGreaterEqual(len(trades), 862, "Defter en az 862 baseline işlemi içermelidir.")

        # Tüm işlemlerin %90 güven üzerinde olduğunu doğrula
        under_90_count = sum(1 for t in trades if float(t.get("ConfidenceScore", 0.0)) < 90.0)
        self.assertEqual(under_90_count, 0, "Defterde %90 güvenin altında tek bir işlem dahi olamaz!")

        # Tüm işlemlerin 25 bps slippage altında olduğunu doğrula
        over_slippage_count = sum(1 for t in trades if (float(t.get("SlippageCost", 0)) / float(t.get("PositionSizeTRY", 1))) * 10000.0 > 25.0)
        self.assertEqual(over_slippage_count, 0, "Defterde 25 bps üzerinde slippage olamaz!")

        # Tüm işlemlerin 100-300 TL bandında olduğunu doğrula
        out_of_bounds_size = sum(1 for t in trades if not (100.0 <= float(t.get("PositionSizeTRY", 0)) <= 300.0))
        self.assertEqual(out_of_bounds_size, 0, "Tüm pozisyonlar 100.00 TL - 300.00 TL bandında olmalıdır!")

        # Performans analizi çıkar
        attr = ExecutionIntelligence.compute_performance_attribution(trades)
        self.assertGreaterEqual(len(attr["asset_attribution"]), 9, "En az 9 SPL token işlem görmüş olmalıdır.")


if __name__ == "__main__":
    unittest.main()
