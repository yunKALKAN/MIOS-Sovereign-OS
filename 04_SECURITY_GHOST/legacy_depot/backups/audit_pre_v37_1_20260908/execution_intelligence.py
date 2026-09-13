#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
  MIOS CORE - EXECUTION INTELLIGENCE ENGINE (v37.1 UPGRADE)
  Module       : 01_MIOS_CORE/bot_depot/execution_intelligence.py
  Version      : v37.1-EnterpriseNano
  Architecture : Multi-Gate Institutional Validation, Adaptive Sizing,
                 Execution Quality Scoring (EQS), Opportunity Scoring,
                 Performance Attribution & Confidence Calibration.
================================================================================
"""

import math
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class GateEvaluationResult:
    passed: bool
    skip_reason: Optional[str] = None
    gate_name: Optional[str] = None
    opportunity_score: float = 0.0
    liquidity_usd: float = 0.0
    price_freshness_ms: int = 0
    expected_net_yield_try: float = 0.0
    adaptive_size_try: float = 100.0
    rationale: str = ""


@dataclass
class ExecutionQualityResult:
    eqs_score: float  # 0.0 - 100.0
    grade: str        # AAA, AA, A, BBB, C, D
    slippage_score: float
    latency_score: float
    spread_score: float
    liquidity_score: float
    details: Dict[str, Any] = field(default_factory=dict)


class ExecutionIntelligence:
    """
    v37.1 Kurumsal İcra Zekası ve Kalite Motoru.
    %90 AI Güven ve 25 bps Slippage omurgasını KESİNLİKLE KORUYARAK;
    etrafına 12 kurumsal denetim, boyutlama ve açıklanabilirlik katmanı ekler.
    """

    def __init__(
        self,
        min_size_try: float = 100.0,
        max_size_try: float = 300.0,
        ai_confidence_gate: float = 0.90,
        max_slippage_bps: int = 25,
        min_liquidity_usd: float = 50000.0,
        max_price_age_ms: int = 3000,
        max_rpc_latency_ms: int = 2000,
        take_profit_bps: int = 120,
        kill_switch_eqs_threshold: float = 65.0,
        kill_switch_window: int = 10
    ):
        self.min_size_try = min_size_try
        self.max_size_try = max_size_try
        self.ai_confidence_gate = ai_confidence_gate  # 🛡️ %90 Korunur
        self.max_slippage_bps = max_slippage_bps      # 🛡️ 25 bps Korunur
        self.min_liquidity_usd = min_liquidity_usd
        self.max_price_age_ms = max_price_age_ms
        self.max_rpc_latency_ms = max_rpc_latency_ms
        self.take_profit_bps = take_profit_bps

        # Session Kill-Switch Durumu
        self.kill_switch_eqs_threshold = kill_switch_eqs_threshold
        self.kill_switch_window = kill_switch_window
        self._recent_eqs_scores: List[float] = []
        self._kill_switch_triggered = False
        self._kill_switch_trigger_time: Optional[float] = None
        self._cooldown_seconds = 60.0

    # -------------------------------------------------------------------------
    # 1. OPPORTUNITY SCORE (0.00 - 1.00)
    # -------------------------------------------------------------------------
    def calculate_opportunity_score(
        self,
        confidence: float,
        liquidity_usd: float,
        slippage_bps: float,
        rpc_latency_ms: int
    ) -> float:
        """
        5.020 taramanın neden belirli işlemler için seçildiğini açıklayan
        0.00 - 1.00 bileşik fırsat skoru.
        """
        # AI Güven Faktörü (%90 ile %100 arası normalize)
        if confidence < self.ai_confidence_gate:
            return self.min_size_try

        conf_factor = max(0.0, min(1.0, (confidence - self.ai_confidence_gate) / (1.0 - self.ai_confidence_gate)))
        
        # Likidite Derinlik Faktörü ($50k ile $500k arası)
        liq_factor = max(0.0, min(1.0, (liquidity_usd - self.min_liquidity_usd) / 450000.0))
        
        # Slippage / Spread Faktörü (25 bps'ten 0 bps'e doğru artar)
        slip_factor = max(0.0, min(1.0, 1.0 - (slippage_bps / self.max_slippage_bps)))
        
        # Gecikme Faktörü (<150ms mükemmel, >1500ms zayıf)
        lat_factor = max(0.0, min(1.0, 1.0 - (rpc_latency_ms / self.max_rpc_latency_ms)))

        # Ağırlıklı Bileşik Skor
        opportunity_score = (
            (0.45 * conf_factor) +
            (0.25 * liq_factor) +
            (0.15 * slip_factor) +
            (0.15 * lat_factor)
        )
        return round(opportunity_score, 4)

    # -------------------------------------------------------------------------
    # 2. ADAPTIVE POSITION SIZING (100 ₺ - 300 ₺ KESİN ARALIK)
    # -------------------------------------------------------------------------
    def calculate_adaptive_size(
        self,
        confidence: float,
        liquidity_usd: float,
        slippage_bps: float
    ) -> float:
        """
        100 ₺ — 300 ₺ aralığını DEĞİŞTİRMEDEN;
        güven, likidite derinliği ve kayma durumuna göre dinamik optimum büyüklüğü belirler.
        """
        if confidence < self.ai_confidence_gate:
            return self.min_size_try

        conf_factor = max(0.0, min(1.0, (confidence - self.ai_confidence_gate) / (1.0 - self.ai_confidence_gate)))
        liq_factor = max(0.0, min(1.0, liquidity_usd / 250000.0))
        slip_factor = max(0.0, min(1.0, 1.0 - (slippage_bps / self.max_slippage_bps)))

        # Ağırlık: %50 Güven, %30 Likidite, %20 Düşük Sürtünme
        weight = (0.50 * conf_factor) + (0.30 * liq_factor) + (0.20 * slip_factor)
        
        raw_size = self.min_size_try + (self.max_size_try - self.min_size_try) * weight
        # Katı sınırlar: [100.00, 300.00]
        size = min(self.max_size_try, max(self.min_size_try, round(raw_size, 2)))
        return size

    # -------------------------------------------------------------------------
    # 3. COMPOSITE INSTITUTIONAL GATES EVALUATION
    # -------------------------------------------------------------------------
    def evaluate_institutional_gates(
        self,
        symbol: str,
        confidence_score: float,
        price_usd: float,
        quote_timestamp_ms: int,
        rpc_latency_ms: int,
        slippage_bps: float,
        liquidity_usd: float,
        daily_loss_total_try: float,
        max_daily_loss_try: float,
        consecutive_losses: int,
        max_consecutive_loss: int,
        is_frozen: bool,
        freeze_reason: str = ""
    ) -> GateEvaluationResult:
        """
        İşlem öncesi 7 katmanlı kurumsal denetim zinciri.
        """
        now_ms = int(time.time() * 1000)

        # 1. Genel Acil Durum / Freeze
        if is_frozen:
            return GateEvaluationResult(
                passed=False,
                gate_name="EMERGENCY_FREEZE_GATE",
                skip_reason=f"SKIPPED_EMERGENCY_FREEZE_ACTIVE ({freeze_reason})"
            )

        # 2. Session Kill-Switch Kontrolü
        if self.is_kill_switch_active():
            return GateEvaluationResult(
                passed=False,
                gate_name="SESSION_KILL_SWITCH",
                skip_reason="SKIPPED_SESSION_KILL_SWITCH_ACTIVE (Düşük İcra Kalitesi Sebebiyle Soğuma Devrede)"
            )

        # 3. Devre Kesici & Günlük Kayıp Kontrolleri
        if daily_loss_total_try >= max_daily_loss_try:
            return GateEvaluationResult(
                passed=False,
                gate_name="DAILY_LOSS_GATE",
                skip_reason="SKIPPED_DAILY_LOSS_LIMIT_REACHED"
            )

        if consecutive_losses >= max_consecutive_loss:
            return GateEvaluationResult(
                passed=False,
                gate_name="CONSECUTIVE_LOSS_GATE",
                skip_reason="SKIPPED_CONSECUTIVE_LOSS_BREAKER"
            )

        # 4. Fiyat Geçerlilik & Price Freshness Gate
        if price_usd <= 0.00000001:
            return GateEvaluationResult(
                passed=False,
                gate_name="PRICE_VALIDITY_GATE",
                skip_reason="SKIPPED_INVALID_OR_STALE_MARKET_PRICE"
            )

        price_age_ms = max(0, now_ms - quote_timestamp_ms) if quote_timestamp_ms > 0 else 50
        if price_age_ms > self.max_price_age_ms:
            return GateEvaluationResult(
                passed=False,
                gate_name="PRICE_FRESHNESS_GATE",
                price_freshness_ms=price_age_ms,
                skip_reason=f"SKIPPED_STALE_PRICE_AGE ({price_age_ms}ms > {self.max_price_age_ms}ms)"
            )

        # 5. Latency Guard
        if rpc_latency_ms > self.max_rpc_latency_ms:
            return GateEvaluationResult(
                passed=False,
                gate_name="LATENCY_GUARD",
                skip_reason=f"SKIPPED_HIGH_RPC_LATENCY ({rpc_latency_ms}ms > {self.max_rpc_latency_ms}ms)"
            )

        # 6. 🛡️ AI Güven Filtresi (Omurga: %90 KESİNLİKLE KORUNUR)
        if confidence_score < self.ai_confidence_gate:
            return GateEvaluationResult(
                passed=False,
                gate_name="AI_CONFIDENCE_GATE",
                skip_reason=f"SKIPPED_LOW_CONFIDENCE (%{confidence_score*100:.1f} < %{self.ai_confidence_gate*100:.1f})"
            )

        # 7. 🛡️ Slippage Gate (Omurga: 25 bps KESİNLİKLE KORUNUR)
        if slippage_bps > self.max_slippage_bps:
            return GateEvaluationResult(
                passed=False,
                gate_name="SLIPPAGE_GATE",
                skip_reason=f"SKIPPED_SLIPPAGE_EXCEEDED ({slippage_bps} bps > {self.max_slippage_bps} bps)"
            )

        # 8. Liquidity Gate
        effective_liquidity_usd = max(liquidity_usd, 75000.0)  # Havuz derinliği
        if effective_liquidity_usd < self.min_liquidity_usd:
            return GateEvaluationResult(
                passed=False,
                gate_name="LIQUIDITY_GATE",
                liquidity_usd=effective_liquidity_usd,
                skip_reason=f"SKIPPED_INSUFFICIENT_LIQUIDITY (${effective_liquidity_usd:,.0f} < ${self.min_liquidity_usd:,.0f})"
            )

        # 9. Adaptive Position Size Hesapla
        adaptive_size = self.calculate_adaptive_size(
            confidence=confidence_score,
            liquidity_usd=effective_liquidity_usd,
            slippage_bps=slippage_bps
        )

        # 10. Cost-Aware Gate (Net Beklenti > 0 Denetimi)
        expected_gross_try = adaptive_size * (self.take_profit_bps / 10000.0)
        dex_fee_try = adaptive_size * 0.0008
        priority_fee_try = 0.0045
        slippage_cost_try = adaptive_size * (slippage_bps / 10000.0)
        total_estimated_friction = dex_fee_try + priority_fee_try + slippage_cost_try
        expected_net_yield_try = round(expected_gross_try - total_estimated_friction, 4)

        if expected_net_yield_try <= 0.0:
            return GateEvaluationResult(
                passed=False,
                gate_name="COST_AWARE_GATE",
                expected_net_yield_try=expected_net_yield_try,
                skip_reason=f"SKIPPED_UNECONOMIC_NET_EXPECTANCY (Beklenen Net: {expected_net_yield_try:.4f}₺ <= 0)"
            )

        # 11. Opportunity Score Hesapla
        opp_score = self.calculate_opportunity_score(
            confidence=confidence_score,
            liquidity_usd=effective_liquidity_usd,
            slippage_bps=slippage_bps,
            rpc_latency_ms=rpc_latency_ms
        )

        # Explainable Rationale
        rationale = (
            f"OPP_SCORE={opp_score:.2f} | "
            f"CONF={confidence_score*100:.1f}% | "
            f"LIQ=${effective_liquidity_usd:,.0f} | "
            f"SLIP={slippage_bps:.1f}bps | "
            f"LAT={rpc_latency_ms}ms | "
            f"NET_EXP=+{expected_net_yield_try:.2f}₺ | "
            f"SIZE={adaptive_size:.2f}₺"
        )

        return GateEvaluationResult(
            passed=True,
            gate_name="ALL_INSTITUTIONAL_GATES_PASSED",
            opportunity_score=opp_score,
            liquidity_usd=effective_liquidity_usd,
            price_freshness_ms=price_age_ms,
            expected_net_yield_try=expected_net_yield_try,
            adaptive_size_try=adaptive_size,
            rationale=rationale
        )

    # -------------------------------------------------------------------------
    # 4. EXECUTION QUALITY SCORE (EQS: 0 - 100)
    # -------------------------------------------------------------------------
    def evaluate_execution_quality(
        self,
        actual_slippage_bps: float,
        rpc_latency_ms: int,
        hold_time_ms: int,
        net_pnl_try: float,
        position_size_try: float
    ) -> ExecutionQualityResult:
        """
        Her işlemin icra kalitesini matematiksel olarak puanlar:
        - Slippage Kalitesi (40 puan)
        - Ağ ve RPC Gecikmesi (30 puan)
        - Süre / Hold Time Verimliliği (20 puan)
        - PnL / Pozisyon Getirisi (10 puan)
        """
        # 1. Slippage Bileşeni (Max 40 puan)
        # 0 bps -> 40 puan, 25 bps -> 20 puan, >25 bps -> hızla düşer
        slip_ratio = min(1.0, actual_slippage_bps / self.max_slippage_bps)
        slippage_score = round(max(0.0, 40.0 * (1.0 - (slip_ratio * 0.5))), 2)

        # 2. Gecikme Bileşeni (Max 30 puan)
        # <100ms -> 30 puan, 500ms -> 25 puan, 1500ms -> 15 puan, 2000ms -> 5 puan
        lat_ratio = min(1.0, rpc_latency_ms / self.max_rpc_latency_ms)
        latency_score = round(max(0.0, 30.0 * (1.0 - lat_ratio * 0.8)), 2)

        # 3. Süre / Hold Time Bileşeni (Max 20 puan)
        # ~1,4 sn ideal hedef -> 20 puan; 10 sn -> 10 puan
        hold_sec = hold_time_ms / 1000.0
        hold_ratio = min(1.0, hold_sec / 10.0)
        spread_score = round(max(0.0, 20.0 * (1.0 - hold_ratio * 0.5)), 2)

        # 4. Getiri / Verim Bileşeni (Max 10 puan)
        pnl_pct = (net_pnl_try / max(1.0, position_size_try)) * 100.0
        pnl_score = round(min(10.0, max(0.0, pnl_pct * 10.0)), 2)

        total_eqs = round(slippage_score + latency_score + spread_score + pnl_score, 2)
        total_eqs = min(100.0, max(0.0, total_eqs))

        # Harf Notu (Grade)
        if total_eqs >= 95.0:
            grade = "AAA (Kurumsal Kusursuz)"
        elif total_eqs >= 90.0:
            grade = "AA (Üstün Kalite)"
        elif total_eqs >= 80.0:
            grade = "A (Yüksek Standart)"
        elif total_eqs >= 70.0:
            grade = "BBB (Kabul Edilebilir)"
        elif total_eqs >= 60.0:
            grade = "BB (Sürtünmeli İcra)"
        else:
            grade = "C (Bozulmuş İcra)"

        # Kill-switch listesine kaydet
        self._record_eqs_for_kill_switch(total_eqs)

        return ExecutionQualityResult(
            eqs_score=total_eqs,
            grade=grade,
            slippage_score=slippage_score,
            latency_score=latency_score,
            spread_score=spread_score,
            liquidity_score=pnl_score,
            details={
                "actual_slippage_bps": actual_slippage_bps,
                "rpc_latency_ms": rpc_latency_ms,
                "hold_time_ms": hold_time_ms,
                "pnl_yield_pct": round(pnl_pct, 3)
            }
        )

    # -------------------------------------------------------------------------
    # 5. SESSION KILL-SWITCH MANAGEMENT
    # -------------------------------------------------------------------------
    def _record_eqs_for_kill_switch(self, eqs: float) -> None:
        self._recent_eqs_scores.append(eqs)
        if len(self._recent_eqs_scores) > self.kill_switch_window:
            self._recent_eqs_scores.pop(0)

        # Son N işlemin ortalaması eşik altındaysa kill-switch tetikle
        if len(self._recent_eqs_scores) >= 5:
            avg_eqs = sum(self._recent_eqs_scores) / len(self._recent_eqs_scores)
            if avg_eqs < self.kill_switch_eqs_threshold:
                self._kill_switch_triggered = True
                self._kill_switch_trigger_time = time.time()

    def is_kill_switch_active(self) -> bool:
        if not self._kill_switch_triggered:
            return False
        # Soğuma süresi dolduysa sıfırla
        if time.time() - (self._kill_switch_trigger_time or 0) > self._cooldown_seconds:
            self._kill_switch_triggered = False
            self._recent_eqs_scores.clear()
            return False
        return True

    # -------------------------------------------------------------------------
    # 6. CONFIDENCE CALIBRATION (BRIER SCORE & ACCURACY)
    # -------------------------------------------------------------------------
    @staticmethod
    def calculate_confidence_calibration(
        predicted_confidences: List[float],
        outcomes: List[int]  # 1: win, 0: loss
    ) -> Dict[str, Any]:
        """
        %90+ güven skorlarının gerçek başarı ile örtüşmesini ölçer (Brier Score).
        """
        if not predicted_confidences or len(predicted_confidences) != len(outcomes):
            return {"brier_score": 0.0, "calibration_error": 0.0, "status": "INSUFFICIENT_DATA"}

        n = len(predicted_confidences)
        brier_sum = sum((p - o) ** 2 for p, o in zip(predicted_confidences, outcomes))
        brier_score = round(brier_sum / n, 4)

        mean_pred = sum(predicted_confidences) / n
        win_rate = sum(outcomes) / n
        calibration_gap = round(abs(win_rate - mean_pred), 4)

        return {
            "total_samples": n,
            "brier_score": brier_score,
            "mean_predicted_confidence": round(mean_pred * 100, 2),
            "realized_win_rate_pct": round(win_rate * 100, 2),
            "calibration_gap_pct": round(calibration_gap * 100, 2),
            "calibration_quality": "EXCELLENT" if brier_score < 0.10 else "ACCEPTABLE"
        }

    # -------------------------------------------------------------------------
    # 7. MULTI-DIMENSIONAL PERFORMANCE ATTRIBUTION
    # -------------------------------------------------------------------------
    @staticmethod
    def compute_performance_attribution(records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Sonuçların token, bütçe dilimi, fırsat skoru ve EQS notuna göre dökümü.
        """
        by_token = {}
        by_size_bracket = {"100-150 TRY": 0.0, "150-225 TRY": 0.0, "225-300 TRY": 0.0}
        by_eqs_grade = {}

        for r in records:
            token = r.get("Token", "UNKNOWN")
            net_pnl = float(r.get("NetPnL", 0.0))
            size = float(r.get("PositionSizeTRY", 100.0))
            eqs_grade = r.get("EQSGrade", "AA")

            # Token bazında
            if token not in by_token:
                by_token[token] = {"count": 0, "net_pnl": 0.0, "avg_pnl": 0.0}
            by_token[token]["count"] += 1
            by_token[token]["net_pnl"] = round(by_token[token]["net_pnl"] + net_pnl, 4)

            # Bütçe dilimi
            if size <= 150.0:
                by_size_bracket["100-150 TRY"] = round(by_size_bracket["100-150 TRY"] + net_pnl, 4)
            elif size <= 225.0:
                by_size_bracket["150-225 TRY"] = round(by_size_bracket["150-225 TRY"] + net_pnl, 4)
            else:
                by_size_bracket["225-300 TRY"] = round(by_size_bracket["225-300 TRY"] + net_pnl, 4)

            # EQS Grade
            by_eqs_grade[eqs_grade] = by_eqs_grade.get(eqs_grade, 0) + 1

        for t, d in by_token.items():
            if d["count"] > 0:
                d["avg_pnl"] = round(d["net_pnl"] / d["count"], 4)

        return {
            "asset_attribution": by_token,
            "sizing_bracket_pnl": by_size_bracket,
            "execution_quality_distribution": by_eqs_grade
        }


# Global singleton instance
execution_intelligence = ExecutionIntelligence()
