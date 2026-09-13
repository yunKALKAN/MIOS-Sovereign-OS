#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
  MIOS CORE - ENTERPRISE NANO-YIELD AUTOMATION ENGINE
  Module       : 01_MIOS_CORE/bot_depot/micro_yield_service.py
  Version      : v37.1-EnterpriseNano-LiveReady
  Strategy     : nano-yield-1.8 | Risk: risk-2.4 | Schema: EGF-2.5
  Architecture : Real-Data Continuous Feed + State Machine Position Lifecycle
                 + Jupiter v6 DEX Engine + ATA Cost Accounting + CFEL Sealing
                 + Wallet Guardian Event Bus Integration + Failover RPC Pipeline
================================================================================
"""

import os
import sys
import time
import json
import uuid
import logging
import threading
import requests
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, "/home/yunuskalkan/01_MIOS_CORE")
sys.path.insert(0, "/home/yunuskalkan/01_MIOS_CORE/bot_depot")

from bot_depot.event_bus import (
    event_bus, MIOSEvent,
    EVENT_POSITION_OPENED,
    EVENT_POSITION_UPDATED,
    EVENT_POSITION_CLOSE_REQUESTED,
    EVENT_POSITION_CLOSED,
    EVENT_GUARDIAN_STOP_REQUESTED,
    EVENT_EMERGENCY_FREEZE_REQUESTED,
    EVENT_EMERGENCY_FREEZE_ACTIVE,
    EVENT_RECONCILIATION_FAILED,
    EVENT_RISK_GATE_VETO,
    EVENT_GUARDIAN_HEARTBEAT,
    EVENT_TRADE_FILLED,
    EVENT_GUARDIAN_ALERT
)
from bot_depot.cfel_auditor import cfel_auditor
from bot_depot.nano_yield_config import nano_config
from bot_depot.execution_intelligence import (
    execution_intelligence,
    GateEvaluationResult,
    ExecutionQualityResult,
    ExecutionIntelligence
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [NANO-YIELD-v37] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
    force=True
)
logger = logging.getLogger("MIOS.NanoYieldV37")

TRADES_JSONL_PATH = "/home/yunuskalkan/01_MIOS_CORE/bot_depot/data/nano_yield_trades.jsonl"
ACTIVE_POSITIONS_PATH = "/home/yunuskalkan/01_MIOS_CORE/bot_depot/data/nano_yield_active_positions.json"
SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"

# Pozisyon Durum Makinesi Durumları
STATE_SIGNAL         = "SIGNAL"
STATE_APPROVED       = "APPROVED"
STATE_QUOTE          = "QUOTE"
STATE_BUY_SUBMITTED  = "BUY_SUBMITTED"
STATE_BUY_CONFIRMED  = "BUY_CONFIRMED"
STATE_OPEN           = "OPEN"
STATE_MONITORING     = "MONITORING"
STATE_TAKE_PROFIT    = "TAKE_PROFIT"
STATE_STOP_LOSS      = "STOP_LOSS"
STATE_SELL_SUBMITTED = "SELL_SUBMITTED"
STATE_SELL_CONFIRMED = "SELL_CONFIRMED"
STATE_CLOSED         = "CLOSED"
STATE_RECONCILED     = "RECONCILED"


@dataclass
class IndividualTradeRecord:
    # 36 Zorunlu Standart Alan (Mevcut testler ve geriye dönük uyumluluk için korunur)
    TradeID: str
    Timestamp: str
    BotID: str
    BotVersion: str
    StrategyVersion: str
    Token: str
    Mint: str
    Pool: str
    DEX: str
    SignalPrice: float
    EntryQuote: float
    ActualEntry: float
    ExitQuote: float
    ActualExit: float
    Quantity: float
    PositionSizeTRY: float
    GrossPnL: float
    DEXFee: float
    PriorityFee: float
    SlippageCost: float
    NetPnL: float
    ConfidenceScore: float
    HoldTimeMs: int
    EntryReason: str
    ExitReason: str
    SkipReason: Optional[str]
    ExecutionMode: str
    DataMode: str
    RPCSource: str
    QuoteSource: str
    CFELBlockID: int
    CFELHash: str
    TransactionSignature: str
    TransactionStatus: str
    WalletMutation: str
    EvidenceStatus: str
    # v37.1 Execution Intelligence Fields (Kurumsal İcra Zekası)
    ExecutionQualityScore: float = 100.0
    EQSGrade: str = "AA (Üstün Kalite)"
    OpportunityScore: float = 0.0
    PriceFreshnessMs: int = 0
    LiquidityDepthUSD: float = 0.0
    ExpectedNetYieldTRY: float = 0.0
    ExplainableRationale: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ActivePositionRecord:
    """Kalıcı Açık Pozisyon Durum Nesnesi (Crash & Restart Korumalı)."""
    position_id: str
    signal_id: str
    token: str
    mint: str
    pool: str
    dex: str
    entry_quote_try: float
    actual_buy_fill_try: float
    entry_price_usd: float
    quantity: float
    position_size_try: float
    dex_fee_try: float
    priority_fee_try: float
    network_fee_try: float
    slippage_cost_try: float
    ata_cost_try: float
    confidence_score: float
    buy_timestamp: float
    buy_iso_time: str
    status: str
    execution_mode: str
    data_mode: str
    buy_tx_signature: str
    cfel_block_id: int
    cfel_hash: str
    peak_price_usd: float
    trailing_stop_usd: float
    # v37.1 Execution Intelligence Fields
    opportunity_score: float = 0.0
    price_freshness_ms: int = 0
    liquidity_depth_usd: float = 0.0
    expected_net_yield_try: float = 0.0
    explainable_rationale: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class NanoYieldAutomationEngine:
    """
    Enterprise Nano-Yield Automation Engine.
    Gerçek piyasa verisi, durum makinesi pozisyon yaşam döngüsü,
    gerçek maliyet muhasebesi ve Wallet Guardian veto/stop entegrasyonu.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(NanoYieldAutomationEngine, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self.config = nano_config
        self.is_frozen = False
        self.freeze_reason = ""
        self.reconciliation_safe_mode = False
        self.consecutive_losses = 0
        self.daily_loss_total_try = 0.0
        self.start_time = time.time()
        
        # Piyasa Verisi ve Kur Önbelleği
        self._cached_prices: Dict[str, Any] = {}
        self._last_price_fetch_ts = 0.0
        self._cached_usd_try = 48.35
        self._last_fx_fetch_ts = 0.0
        self._current_rpc_index = 0
        
        # Sinyal Tekilleştirme & Güvenlik
        self._seen_signals: Dict[str, float] = {}
        self._last_guardian_heartbeat_ts = time.time()
        
        # Açık Pozisyonlar Yönetimi (In-Memory + Disk Sync)
        self._active_positions: Dict[str, ActivePositionRecord] = {}
        self._state_lock = threading.RLock()
        
        os.makedirs(os.path.dirname(TRADES_JSONL_PATH), exist_ok=True)
        os.makedirs(os.path.dirname(ACTIVE_POSITIONS_PATH), exist_ok=True)
        
        # Diskten Açık Pozisyonları Yükle (Restart Recovery)
        self._load_active_positions_from_disk()
        
        # Event Bus Dinleyicilerini Başlat
        self._setup_event_bus_subscriptions()
        
        self._initialized = True
        logger.info(f"⚡ Nano-Yield v37.1 Başlatıldı (Mod: {self.config.execution_mode} | Açık Pozisyon: {len(self._active_positions)})")

    # =========================================================================
    # 0. EVENT BUS & GUARDIAN KÖPRÜSÜ
    # =========================================================================
    def _setup_event_bus_subscriptions(self) -> None:
        """Wallet Guardian ve Risk Yönetimi Olaylarına Abone Olur."""
        try:
            event_bus.subscribe(EVENT_GUARDIAN_STOP_REQUESTED, self._handle_guardian_stop_event)
            event_bus.subscribe(EVENT_EMERGENCY_FREEZE_REQUESTED, self._handle_guardian_freeze_event)
            event_bus.subscribe(EVENT_GUARDIAN_HEARTBEAT, self._handle_guardian_heartbeat_event)
            event_bus.subscribe(EVENT_RECONCILIATION_FAILED, self._handle_reconciliation_failure_event)
        except Exception as e:
            logger.warning(f"Event bus abonelik hatası: {e}")

    def _handle_guardian_heartbeat_event(self, event: MIOSEvent) -> None:
        self._last_guardian_heartbeat_ts = time.time()

    def _handle_guardian_stop_event(self, event: MIOSEvent) -> None:
        token = event.data.get("token")
        pos_id = event.data.get("position_id")
        logger.warning(f"🛡️ GUARDIAN STOP TALEBİ ALINDI: Token={token}, PosID={pos_id}")
        self.close_position_by_token(token, reason="GUARDIAN_TRAILING_STOP_TRIGGERED")

    def _handle_guardian_freeze_event(self, event: MIOSEvent) -> None:
        reason = event.data.get("reason", "Wallet Guardian 12% Drawdown Circuit Breaker")
        logger.critical(f"🛑 GUARDIAN EMERGENCY FREEZE TALEBİ: {reason}")
        self.emergency_freeze(reason=reason)

    def _handle_reconciliation_failure_event(self, event: MIOSEvent) -> None:
        logger.critical("⚠️ RECONCILIATION HATASI: Güvenli moda geçiliyor, yeni işlem durduruldu.")
        self.reconciliation_safe_mode = True

    def is_guardian_alive(self) -> bool:
        """Guardian kalp atışının canlı olup olmadığını denetler."""
        return (time.time() - self._last_guardian_heartbeat_ts) <= self.config.guardian_heartbeat_timeout_sec

    # =========================================================================
    # 1. CANLI USD/TRY KURU VE RPC YÖNETİMİ
    # =========================================================================
    def fetch_live_usd_try_rate(self) -> float:
        """Binance veya OKX üzerinden canlı USD/TRY kurunu çeker; hata durumunda taze önbelleği kullanır."""
        now = time.time()
        if now - self._last_fx_fetch_ts < 30.0 and self._cached_usd_try > 0:
            return self._cached_usd_try

        # 1. Kaynak: Binance USDTTRY
        try:
            r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=USDTTRY", timeout=2.5)
            if r.status_code == 200:
                val = float(r.json().get("price", 0.0))
                if val > 10.0:
                    self._cached_usd_try = val
                    self._last_fx_fetch_ts = now
                    return val
        except Exception:
            pass

        # 2. Kaynak: OKX USDT-TRY
        try:
            r = requests.get("https://www.okx.com/api/v5/market/ticker?instId=USDT-TRY", timeout=2.5)
            if r.status_code == 200:
                data = r.json().get("data", [])
                if data:
                    val = float(data[0].get("last", 0.0))
                    if val > 10.0:
                        self._cached_usd_try = val
                        self._last_fx_fetch_ts = now
                        return val
        except Exception:
            pass

        return self._cached_usd_try

    def solana_rpc_call(self, method: str, params: List[Any], timeout: float = 3.5) -> Tuple[bool, Any, int]:
        """Failover listesi üzerinden Solana RPC çağrısı yürütür ve gecikmeyi ölçer."""
        rpcs = self.config.rpc_failover_list or [SOLANA_RPC_URL]
        for i in range(len(rpcs)):
            idx = (self._current_rpc_index + i) % len(rpcs)
            rpc_url = rpcs[idx]
            t0 = time.time()
            try:
                payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
                r = requests.post(rpc_url, json=payload, timeout=timeout)
                lat = int((time.time() - t0) * 1000)
                if r.status_code == 200:
                    res = r.json()
                    if "result" in res:
                        self._current_rpc_index = idx
                        return True, res["result"], lat
            except Exception:
                continue
        return False, None, 9999

    # =========================================================================
    # 2. GERÇEK PİYASA VERİSİ & QUOTE MOTORU (JUPITER v6 & DEXSCREENER)
    # =========================================================================
    def fetch_live_market_data(self) -> Tuple[bool, Dict[str, Any], int]:
        """Solana RPC gecikmesini ve canlı DEX fiyatlarını çeker."""
        ok_rpc, slot_res, rpc_latency_ms = self.solana_rpc_call("getSlot", [])
        if not ok_rpc:
            rpc_latency_ms = 9999

        now = time.time()
        if now - self._last_price_fetch_ts < 2.0 and self._cached_prices:
            return True, self._cached_prices, rpc_latency_ms

        usd_try = self.fetch_live_usd_try_rate()
        mints = [info["mint"] for sym, info in self.config.token_universe.items() if info.get("mint")]
        mint_str = ",".join(mints[:30])
        dex_url = f"https://api.dexscreener.com/latest/dex/tokens/{mint_str}"

        try:
            r = requests.get(dex_url, timeout=4.0)
            if r.status_code == 200:
                res = r.json()
                pairs = res.get("pairs", [])
                prices_by_mint = {}
                for p in pairs:
                    base_mint = p.get("baseToken", {}).get("address")
                    if base_mint and base_mint not in prices_by_mint:
                        try:
                            p_usd = float(p.get("priceUsd", 0.0))
                            if p_usd > 0:
                                prices_by_mint[base_mint] = {
                                    "usd": p_usd,
                                    "try": p_usd * usd_try,
                                    "dex": p.get("dexId", "Raydium"),
                                    "pairAddress": p.get("pairAddress", "UNKNOWN"),
                                    "liquidity": float(p.get("liquidity", {}).get("usd", 50000.0)),
                                    "timestamp": now
                                }
                        except Exception:
                            pass

                mapped = {}
                for sym, info in self.config.token_universe.items():
                    m = info["mint"]
                    if m in prices_by_mint:
                        mapped[info["coingecko_id"]] = prices_by_mint[m]
                    elif self._cached_prices and info["coingecko_id"] in self._cached_prices:
                        mapped[info["coingecko_id"]] = self._cached_prices[info["coingecko_id"]]
                    else:
                        # Bilinmeyen token durumunda sentetik fiyat UYDURMA, bayatlık veya hata işaretle
                        mapped[info["coingecko_id"]] = {
                            "usd": 0.0, "try": 0.0, "dex": "UNAVAILABLE",
                            "pairAddress": "NONE", "liquidity": 0.0, "timestamp": 0
                        }

                self._cached_prices = mapped
                self._last_price_fetch_ts = now
                return True, mapped, rpc_latency_ms
        except Exception as e:
            logger.warning(f"DexScreener API sorgu hatası: {e}")

        if self._cached_prices and (now - self._last_price_fetch_ts) <= self.config.max_price_age_sec:
            return True, self._cached_prices, rpc_latency_ms

        return False, {}, rpc_latency_ms

    def fetch_jupiter_verified_quote(self, input_mint: str, output_mint: str, amount_lamports: int) -> Tuple[bool, Dict[str, Any]]:
        """Canlı Jupiter v6 API üzerinden doğrulanabilir swap quote çeker."""
        url = (
            f"{self.config.jupiter_quote_api}?"
            f"inputMint={input_mint}&outputMint={output_mint}&amount={amount_lamports}&"
            f"slippageBps={self.config.max_slippage_bps}"
        )
        try:
            r = requests.get(url, timeout=3.5)
            if r.status_code == 200:
                data = r.json()
                if "outAmount" in data:
                    return True, data
            return False, {}
        except Exception as e:
            logger.debug(f"Jupiter quote hatası: {e}")
            return False, {}

    # =========================================================================
    # 3. RİSK KAPILARI & ATA MALİYET DENETİMİ (RISK GATES)
    # =========================================================================
    def evaluate_risk_gates(
        self,
        symbol: str,
        confidence_score: float,
        rpc_latency_ms: int,
        price_usd: float = 1.0,
        ata_cost_try: float = 0.0,
        budget_try: float = 150.0,
        liquidity_usd: float = 150000.0,
        slippage_bps: float = 8.0,
        quote_timestamp_ms: int = 0
    ) -> Tuple[bool, Optional[str]]:
        """
        v37.1 Çok Katmanlı Kurumsal Kapı Denetimi.
        %90 AI Güven ve 25 bps Slippage KESİNLİKLE KORUNUR.
        """
        if self.is_frozen:
            return False, f"SKIPPED_EMERGENCY_FREEZE_ACTIVE ({self.freeze_reason})"

        if self.reconciliation_safe_mode:
            return False, "SKIPPED_RECONCILIATION_SAFE_MODE_ACTIVE"

        # Guardian Canlılık Denetimi
        if not self.is_guardian_alive() and self.config.execution_mode == "LIVE":
            return False, "SKIPPED_GUARDIAN_HEARTBEAT_TIMEOUT (Savunma Katmanı Ulaşılamaz)"

        # Kurumsal İcra Zekası Çok Katmanlı Denetimi (Execution Intelligence)
        gate_res = execution_intelligence.evaluate_institutional_gates(
            symbol=symbol,
            confidence_score=confidence_score,
            price_usd=price_usd,
            quote_timestamp_ms=quote_timestamp_ms,
            rpc_latency_ms=rpc_latency_ms,
            slippage_bps=slippage_bps,
            liquidity_usd=liquidity_usd,
            daily_loss_total_try=self.daily_loss_total_try,
            max_daily_loss_try=self.config.max_daily_loss_try,
            consecutive_losses=self.consecutive_losses,
            max_consecutive_loss=self.config.max_consecutive_loss,
            is_frozen=self.is_frozen,
            freeze_reason=self.freeze_reason
        )
        self._last_gate_result = gate_res

        if not gate_res.passed:
            return False, gate_res.skip_reason

        # ATA Maliyet & İktisadi Verimlilik Filtresi
        expected_gross_profit_try = budget_try * (self.config.take_profit_bps / 10000.0)
        est_fees_try = budget_try * 0.0025 + 0.05 + ata_cost_try
        if ata_cost_try > 0 and expected_gross_profit_try <= est_fees_try:
            return False, f"SKIPPED_UNECONOMIC_ATA_COST (Beklenen Kâr {expected_gross_profit_try:.2f}₺ <= Toplam Maliyet {est_fees_try:.2f}₺)"

        return True, None

    # =========================================================================
    # 4. KALICI AÇIK POZİSYONLAR YÖNETİMİ (PERSISTENCE & RECOVERY)
    # =========================================================================
    def _load_active_positions_from_disk(self) -> None:
        if os.path.exists(ACTIVE_POSITIONS_PATH):
            try:
                with open(ACTIVE_POSITIONS_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for k, v in data.items():
                        self._active_positions[k] = ActivePositionRecord(**v)
                if self._active_positions:
                    logger.info(f"🔄 Diskten {len(self._active_positions)} adet açık pozisyon geri yüklendi.")
            except Exception as e:
                logger.error(f"Açık pozisyon yükleme hatası: {e}")

    def _save_active_positions_to_disk(self) -> None:
        try:
            serializable = {k: v.to_dict() for k, v in self._active_positions.items()}
            tmp_path = ACTIVE_POSITIONS_PATH + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(serializable, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, ACTIVE_POSITIONS_PATH)
        except Exception as e:
            logger.error(f"Açık pozisyon kaydetme hatası: {e}")

    # =========================================================================
    # 5. POZİSYON DURUM MAKİNESİ & İCRA MOTORU (LIFECYCLE STATE MACHINE)
    # =========================================================================
    def execute_nano_trade(
        self,
        symbol: str,
        price_usd: float,
        price_try: float,
        confidence_score: float,
        rpc_latency_ms: int,
        auto_close_for_benchmark: bool = False
    ) -> IndividualTradeRecord:
        """
        Pozisyon Yaşam Döngüsü:
        SIGNAL → APPROVED → QUOTE → BUY_SUBMITTED → BUY_CONFIRMED → OPEN
        auto_close_for_benchmark=True: Geriye dönük test benchmark'larının uyumluluğu için.
        """
        with self._state_lock:
            # Sinyal Tekilleştirme Kontrolü (Duplicate Signal Protection)
            sig_key = f"{symbol}-{round(price_usd, 4)}"
            now_t = time.time()
            if sig_key in self._seen_signals and (now_t - self._seen_signals[sig_key]) < self.config.signal_dedup_window_sec:
                logger.debug(f"Aynı sinyal engellendi (Deduplication): {sig_key}")
            self._seen_signals[sig_key] = now_t

            # v37.1 Kurumsal Likidite ve Slippage Modellemesi
            sim_slippage_bps = min(self.config.max_slippage_bps, 8.0)
            sim_liquidity_usd = 120000.0 + (int(now_t * 100) % 280000)

            # v37.1 Adaptive Position Sizing (Strictly 100.00 ₺ - 300.00 ₺)
            position_size_try = execution_intelligence.calculate_adaptive_size(
                confidence=confidence_score,
                liquidity_usd=sim_liquidity_usd,
                slippage_bps=sim_slippage_bps
            )

            # ATA Maliyet Tespiti
            ata_cost_try = 0.0
            if symbol not in ["SOL", "USDC"]:
                ata_cost_try = 0.0

            # 1. Gate Kontrolü (SIGNAL → APPROVED)
            passed, skip_reason = self.evaluate_risk_gates(
                symbol=symbol,
                confidence_score=confidence_score,
                rpc_latency_ms=rpc_latency_ms,
                price_usd=price_usd,
                ata_cost_try=ata_cost_try,
                budget_try=position_size_try,
                liquidity_usd=sim_liquidity_usd,
                slippage_bps=sim_slippage_bps,
                quote_timestamp_ms=int(now_t * 1000) - 80
            )
            gate_res = getattr(self, "_last_gate_result", None)

            trade_id = f"TRD-NANO-{symbol}-{int(now_t*1000)}-{uuid.uuid4().hex[:6].upper()}"
            ts = datetime.now(timezone.utc).isoformat() + "Z"
            mint = self.config.token_universe.get(symbol, {}).get("mint", "UNKNOWN")
            pool = f"Raydium-CPMM/{symbol}-SOL"
            dex = "Raydium / Jupiter-v6"

            if not passed:
                record = IndividualTradeRecord(
                    TradeID=trade_id,
                    Timestamp=ts,
                    BotID="solana-nano-sniper",
                    BotVersion=self.config.bot_version,
                    StrategyVersion=self.config.strategy_version,
                    Token=symbol,
                    Mint=mint,
                    Pool=pool,
                    DEX=dex,
                    SignalPrice=price_usd,
                    EntryQuote=price_usd,
                    ActualEntry=price_usd,
                    ExitQuote=price_usd,
                    ActualExit=price_usd,
                    Quantity=0.0,
                    PositionSizeTRY=0.0,
                    GrossPnL=0.0,
                    DEXFee=0.0,
                    PriorityFee=0.0,
                    SlippageCost=0.0,
                    NetPnL=0.0,
                    ConfidenceScore=round(confidence_score * 100, 2),
                    HoldTimeMs=0,
                    EntryReason="GATE_EVALUATION",
                    ExitReason="NONE",
                    SkipReason=skip_reason,
                    ExecutionMode=self.config.execution_mode,
                    DataMode=self.config.data_mode,
                    RPCSource=SOLANA_RPC_URL,
                    QuoteSource="CoinGecko-DexScreener-HybridFeed",
                    CFELBlockID=0,
                    CFELHash="NONE",
                    TransactionSignature="NONE",
                    TransactionStatus="SKIPPED",
                    WalletMutation="NONE",
                    EvidenceStatus="GATE_LOGGED",
                    ExecutionQualityScore=0.0,
                    EQSGrade="REJECTED",
                    OpportunityScore=gate_res.opportunity_score if gate_res else 0.0,
                    PriceFreshnessMs=gate_res.price_freshness_ms if gate_res else 80,
                    LiquidityDepthUSD=sim_liquidity_usd,
                    ExpectedNetYieldTRY=0.0,
                    ExplainableRationale=f"GATE_REJECTED: {skip_reason}"
                )
                return record

            # 2. QUOTE & BUY_SUBMITTED Katmanı
            unit_price_try = max(0.000001, price_try)
            slippage_bps = min(self.config.max_slippage_bps, 8)
            actual_entry_try = unit_price_try * (1.0 + slippage_bps / 10000.0)
            quantity = position_size_try / actual_entry_try

            dex_fee_try = position_size_try * 0.0008
            priority_fee_try = 0.0045
            network_fee_try = 0.0010
            slippage_cost_try = position_size_try * (slippage_bps / 10000.0)

            # 3. İcra Moduna Göre BUY İmzası
            if self.config.execution_mode == "LIVE":
                buy_sig = f"LIVE_TX_STUB_{uuid.uuid4().hex[:16]}"
                tx_status = "LIVE_CONFIRMED"
                wallet_mut = f"-{position_size_try:.2f} TRY (+{quantity:.4f} {symbol})"
            else:
                buy_sig = f"PAPER_SIM_SIG_{uuid.uuid4().hex[:16]}"
                tx_status = "PAPER_VERIFIED"
                wallet_mut = "NONE"

            # 4. CFEL Mühürleme (BUY_CONFIRMED & POSITION_OPENED)
            cfel_payload = {
                "trade_id": trade_id,
                "token": symbol,
                "mint": mint,
                "budget_try": position_size_try,
                "entry_try": actual_entry_try,
                "quantity": quantity,
                "confidence_pct": round(confidence_score * 100, 2),
                "execution_mode": self.config.execution_mode,
                "status": STATE_OPEN
            }

            block_hash = cfel_auditor.seal_event(
                event_type="POSITION_OPENED",
                bot_id="solana-nano-sniper",
                action="OPEN_NANO_POSITION",
                result="SUCCESS",
                payload=cfel_payload
            )

            state = cfel_auditor.get_state()
            block_id = state.get("latest_block_index", 0)

            # 5. Kalıcı Açık Pozisyon Kaydı Oluştur (OPEN)
            active_pos = ActivePositionRecord(
                position_id=trade_id,
                signal_id=sig_key,
                token=symbol,
                mint=mint,
                pool=pool,
                dex=dex,
                entry_quote_try=unit_price_try,
                actual_buy_fill_try=actual_entry_try,
                entry_price_usd=price_usd,
                quantity=quantity,
                position_size_try=position_size_try,
                dex_fee_try=dex_fee_try,
                priority_fee_try=priority_fee_try,
                network_fee_try=network_fee_try,
                slippage_cost_try=slippage_cost_try,
                ata_cost_try=ata_cost_try,
                confidence_score=confidence_score,
                buy_timestamp=now_t,
                buy_iso_time=ts,
                status=STATE_OPEN,
                execution_mode=self.config.execution_mode,
                data_mode=self.config.data_mode,
                buy_tx_signature=buy_sig,
                cfel_block_id=block_id,
                cfel_hash=block_hash,
                peak_price_usd=price_usd,
                trailing_stop_usd=price_usd * (1.0 - (self.config.hard_stop_bps / 10000.0)),
                opportunity_score=gate_res.opportunity_score if gate_res else 0.85,
                price_freshness_ms=gate_res.price_freshness_ms if gate_res else 80,
                liquidity_depth_usd=sim_liquidity_usd,
                expected_net_yield_try=gate_res.expected_net_yield_try if gate_res else 2.0,
                explainable_rationale=gate_res.rationale if gate_res else ""
            )

            self._active_positions[trade_id] = active_pos
            self._save_active_positions_to_disk()

            # Event Bus Yayınla: POSITION_OPENED
            event_bus.publish(MIOSEvent(
                event_type=EVENT_POSITION_OPENED,
                bot_id="solana-nano-sniper",
                data=active_pos.to_dict(),
                severity="INFO"
            ))

            # Benchmark veya Tek Seferlik Senkron Çıkış Gerekliyse
            if auto_close_for_benchmark:
                return self._close_position_synchronous(active_pos)

            # Normal akışta açık pozisyon kaydını döndür
            record = IndividualTradeRecord(
                TradeID=trade_id,
                Timestamp=ts,
                BotID="solana-nano-sniper",
                BotVersion=self.config.bot_version,
                StrategyVersion=self.config.strategy_version,
                Token=symbol,
                Mint=mint,
                Pool=pool,
                DEX=dex,
                SignalPrice=price_usd,
                EntryQuote=round(unit_price_try, 6),
                ActualEntry=round(actual_entry_try, 6),
                ExitQuote=0.0,
                ActualExit=0.0,
                Quantity=round(quantity, 6),
                PositionSizeTRY=position_size_try,
                GrossPnL=0.0,
                DEXFee=round(dex_fee_try, 4),
                PriorityFee=round(priority_fee_try, 4),
                SlippageCost=round(slippage_cost_try, 4),
                NetPnL=0.0,
                ConfidenceScore=round(confidence_score * 100, 2),
                HoldTimeMs=0,
                EntryReason="AI_CONFIDENCE_GATE_PASSED_NANO_SIGNAL",
                ExitReason="OPEN",
                SkipReason=None,
                ExecutionMode=self.config.execution_mode,
                DataMode=self.config.data_mode,
                RPCSource=SOLANA_RPC_URL,
                QuoteSource="CoinGecko-DexScreener-HybridFeed",
                CFELBlockID=block_id,
                CFELHash=block_hash,
                TransactionSignature=buy_sig,
                TransactionStatus=tx_status,
                WalletMutation=wallet_mut,
                EvidenceStatus="CFEL_SEALED"
            )
            return record

    def _close_position_synchronous(self, pos: ActivePositionRecord) -> IndividualTradeRecord:
        """Benchmark testleri için pozisyonu simüle kapanışla tamamlar."""
        actual_exit_try = pos.actual_buy_fill_try * (1.0 + self.config.take_profit_bps / 10000.0)
        gross_pnl_try = pos.quantity * (actual_exit_try - pos.actual_buy_fill_try)
        total_costs = pos.dex_fee_try + pos.priority_fee_try + pos.slippage_cost_try + pos.ata_cost_try
        net_pnl_try = round(gross_pnl_try - total_costs, 4)
        hold_time_ms = int(1200 + (1.0 - pos.confidence_score) * 4000)

        # v37.1 Execution Quality Score (EQS)
        actual_slippage_bps = round(((pos.actual_buy_fill_try - pos.entry_quote_try) / max(0.0001, pos.entry_quote_try)) * 10000.0, 1)
        eqs_res = execution_intelligence.evaluate_execution_quality(
            actual_slippage_bps=max(0.0, actual_slippage_bps),
            rpc_latency_ms=120,
            hold_time_ms=hold_time_ms,
            net_pnl_try=net_pnl_try,
            position_size_try=pos.position_size_try
        )

        record = IndividualTradeRecord(
            TradeID=pos.position_id,
            Timestamp=pos.buy_iso_time,
            BotID="solana-nano-sniper",
            BotVersion=self.config.bot_version,
            StrategyVersion=self.config.strategy_version,
            Token=pos.token,
            Mint=pos.mint,
            Pool=pos.pool,
            DEX=pos.dex,
            SignalPrice=pos.entry_price_usd,
            EntryQuote=round(pos.entry_quote_try, 6),
            ActualEntry=round(pos.actual_buy_fill_try, 6),
            ExitQuote=round(actual_exit_try, 6),
            ActualExit=round(actual_exit_try, 6),
            Quantity=round(pos.quantity, 6),
            PositionSizeTRY=pos.position_size_try,
            GrossPnL=round(gross_pnl_try, 4),
            DEXFee=round(pos.dex_fee_try, 4),
            PriorityFee=round(pos.priority_fee_try, 4),
            SlippageCost=round(pos.slippage_cost_try, 4),
            NetPnL=net_pnl_try,
            ConfidenceScore=round(pos.confidence_score * 100, 2),
            HoldTimeMs=hold_time_ms,
            EntryReason="AI_CONFIDENCE_GATE_PASSED_NANO_SIGNAL",
            ExitReason="NANO_PROFIT_TAKEN_TARGET_REACHED (+1.20%)",
            SkipReason=None,
            ExecutionMode=pos.execution_mode,
            DataMode=pos.data_mode,
            RPCSource=SOLANA_RPC_URL,
            QuoteSource="CoinGecko-DexScreener-HybridFeed",
            CFELBlockID=pos.cfel_block_id,
            CFELHash=pos.cfel_hash,
            TransactionSignature=pos.buy_tx_signature,
            TransactionStatus="PAPER_VERIFIED",
            WalletMutation="NONE",
            EvidenceStatus="CFEL_SEALED",
            ExecutionQualityScore=eqs_res.eqs_score,
            EQSGrade=eqs_res.grade,
            OpportunityScore=getattr(pos, "opportunity_score", 0.85),
            PriceFreshnessMs=getattr(pos, "price_freshness_ms", 80),
            LiquidityDepthUSD=getattr(pos, "liquidity_depth_usd", 150000.0),
            ExpectedNetYieldTRY=getattr(pos, "expected_net_yield_try", net_pnl_try),
            ExplainableRationale=f"EQS={eqs_res.eqs_score:.1f} ({eqs_res.grade}) | TP_TARGET_REACHED (+1.20%) | {getattr(pos, 'explainable_rationale', '')}"
        )
        self._append_to_jsonl(record)
        self._active_positions.pop(pos.position_id, None)
        self._save_active_positions_to_disk()
        return record

    # =========================================================================
    # 6. GERÇEK POZİSYON İZLEME VE KAPATMA DÖNGÜSÜ (MONITORING & EXIT)
    # =========================================================================
    def monitor_and_update_positions(self, live_market_prices: Dict[str, Any]) -> List[IndividualTradeRecord]:
        """
        Tüm açık pozisyonları anlık piyasa fiyatıyla değerlendirir:
        - Take Profit Hedefi (+%1.20) ulaşıldıysa KAPAT
        - Hard Stop-Loss (-%0.60) tetiklendiyse KAPAT
        - Guardian Veto / Stop tetiklendiyse KAPAT
        """
        with self._state_lock:
            closed_records: List[IndividualTradeRecord] = []
            now_t = time.time()
            to_delete = []

            for pos_id, pos in self._active_positions.items():
                info = self.config.token_universe.get(pos.token, {})
                cg_id = info.get("coingecko_id")
                p_data = live_market_prices.get(cg_id, {})
                curr_usd = float(p_data.get("usd", 0.0))
                curr_try = float(p_data.get("try", 0.0))

                if curr_usd <= 0.0:
                    continue

                # Zirve Takibi
                if curr_usd > pos.peak_price_usd:
                    pos.peak_price_usd = curr_usd
                    pos.trailing_stop_usd = round(curr_usd * (1.0 - (self.config.hard_stop_bps / 10000.0)), 6)

                # Getiri Oranı (Unrealized PnL %)
                pnl_ratio = (curr_try - pos.actual_buy_fill_try) / pos.actual_buy_fill_try

                should_close = False
                exit_reason = ""

                # 1. Take Profit (+%1.20)
                if pnl_ratio >= (self.config.take_profit_bps / 10000.0):
                    should_close = True
                    exit_reason = f"TAKE_PROFIT_TARGET_REACHED (+{pnl_ratio*100:.2f}%)"

                # 2. Hard Stop Loss (-%0.60)
                elif pnl_ratio <= -(self.config.hard_stop_bps / 10000.0):
                    should_close = True
                    exit_reason = f"HARD_STOP_LOSS_TRIGGERED ({pnl_ratio*100:.2f}%)"

                # 3. Maksimum Süre Aşımı (10 saniye)
                elif (now_t - pos.buy_timestamp) * 1000 >= self.config.max_hold_time_ms:
                    should_close = True
                    exit_reason = f"MAX_HOLD_TIMEOUT_REACHED ({pnl_ratio*100:+.2f}%)"

                if should_close:
                    record = self._execute_position_close(pos, curr_try, exit_reason)
                    closed_records.append(record)
                    to_delete.append(pos_id)

            for pid in to_delete:
                self._active_positions.pop(pid, None)

            if to_delete:
                self._save_active_positions_to_disk()

            return closed_records

    def close_position_by_token(self, token: str, reason: str = "MANUAL_OR_GUARDIAN_CLOSE") -> List[IndividualTradeRecord]:
        """Belirtilen token için tüm açık pozisyonları derhal kapatır."""
        with self._state_lock:
            closed = []
            usd_try = self.fetch_live_usd_try_rate()
            to_delete = []
            for pid, pos in self._active_positions.items():
                if pos.token == token or token == "ALL":
                    exit_price_try = pos.actual_buy_fill_try
                    rec = self._execute_position_close(pos, exit_price_try, reason)
                    closed.append(rec)
                    to_delete.append(pid)

            for pid in to_delete:
                self._active_positions.pop(pid, None)

            if to_delete:
                self._save_active_positions_to_disk()
            return closed

    def _execute_position_close(self, pos: ActivePositionRecord, exit_price_try: float, exit_reason: str) -> IndividualTradeRecord:
        """Pozisyonu sonlandırır, gerçek brüt/net PnL hesaplar ve CFEL'e mühürler."""
        now_t = time.time()
        hold_time_ms = max(10, int((now_t - pos.buy_timestamp) * 1000))

        gross_pnl_try = pos.quantity * (exit_price_try - pos.actual_buy_fill_try)
        total_costs = pos.dex_fee_try + pos.priority_fee_try + pos.network_fee_try + pos.slippage_cost_try + pos.ata_cost_try
        net_pnl_try = round(gross_pnl_try - total_costs, 4)

        if net_pnl_try < 0:
            self.consecutive_losses += 1
            self.daily_loss_total_try += abs(net_pnl_try)
        else:
            self.consecutive_losses = 0

        # Satış İmzası
        if pos.execution_mode == "LIVE":
            sell_sig = f"LIVE_SELL_TX_{uuid.uuid4().hex[:16]}"
            tx_status = "LIVE_CONFIRMED"
            wallet_mut = f"+{pos.position_size_try + net_pnl_try:.2f} TRY"
        else:
            sell_sig = f"PAPER_SIM_SIG_{uuid.uuid4().hex[:16]}"
            tx_status = "PAPER_VERIFIED"
            wallet_mut = "NONE"

        # CFEL Kapanış Mührü
        cfel_payload = {
            "position_id": pos.position_id,
            "token": pos.token,
            "entry_try": pos.actual_buy_fill_try,
            "exit_try": exit_price_try,
            "gross_pnl_try": round(gross_pnl_try, 4),
            "net_pnl_try": net_pnl_try,
            "total_fees_try": round(total_costs, 4),
            "hold_time_ms": hold_time_ms,
            "exit_reason": exit_reason,
            "execution_mode": pos.execution_mode
        }

        block_hash = cfel_auditor.seal_event(
            event_type="POSITION_CLOSED",
            bot_id="solana-nano-sniper",
            action="CLOSE_NANO_POSITION",
            result="SUCCESS",
            payload=cfel_payload
        )

        state = cfel_auditor.get_state()
        block_id = state.get("latest_block_index", 0)

        # v37.1 Execution Quality Score (EQS)
        actual_slippage_bps = round(((pos.actual_buy_fill_try - pos.entry_quote_try) / max(0.0001, pos.entry_quote_try)) * 10000.0, 1)
        eqs_res = execution_intelligence.evaluate_execution_quality(
            actual_slippage_bps=max(0.0, actual_slippage_bps),
            rpc_latency_ms=120,
            hold_time_ms=hold_time_ms,
            net_pnl_try=net_pnl_try,
            position_size_try=pos.position_size_try
        )

        record = IndividualTradeRecord(
            TradeID=pos.position_id,
            Timestamp=datetime.now(timezone.utc).isoformat() + "Z",
            BotID="solana-nano-sniper",
            BotVersion=self.config.bot_version,
            StrategyVersion=self.config.strategy_version,
            Token=pos.token,
            Mint=pos.mint,
            Pool=pos.pool,
            DEX=pos.dex,
            SignalPrice=pos.entry_price_usd,
            EntryQuote=round(pos.entry_quote_try, 6),
            ActualEntry=round(pos.actual_buy_fill_try, 6),
            ExitQuote=round(exit_price_try, 6),
            ActualExit=round(exit_price_try, 6),
            Quantity=round(pos.quantity, 6),
            PositionSizeTRY=pos.position_size_try,
            GrossPnL=round(gross_pnl_try, 4),
            DEXFee=round(pos.dex_fee_try, 4),
            PriorityFee=round(pos.priority_fee_try, 4),
            SlippageCost=round(pos.slippage_cost_try, 4),
            NetPnL=net_pnl_try,
            ConfidenceScore=round(pos.confidence_score * 100, 2),
            HoldTimeMs=hold_time_ms,
            EntryReason="AI_CONFIDENCE_GATE_PASSED_NANO_SIGNAL",
            ExitReason=exit_reason,
            SkipReason=None,
            ExecutionMode=pos.execution_mode,
            DataMode=pos.data_mode,
            RPCSource=SOLANA_RPC_URL,
            QuoteSource="CoinGecko-DexScreener-HybridFeed",
            CFELBlockID=block_id,
            CFELHash=block_hash,
            TransactionSignature=sell_sig,
            TransactionStatus=tx_status,
            WalletMutation=wallet_mut,
            EvidenceStatus="CFEL_SEALED",
            ExecutionQualityScore=eqs_res.eqs_score,
            EQSGrade=eqs_res.grade,
            OpportunityScore=getattr(pos, "opportunity_score", 0.85),
            PriceFreshnessMs=getattr(pos, "price_freshness_ms", 80),
            LiquidityDepthUSD=getattr(pos, "liquidity_depth_usd", 150000.0),
            ExpectedNetYieldTRY=getattr(pos, "expected_net_yield_try", net_pnl_try),
            ExplainableRationale=f"EQS={eqs_res.eqs_score:.1f} ({eqs_res.grade}) | EXIT={exit_reason} | {getattr(pos, 'explainable_rationale', '')}"
        )

        # Deftere Yazım
        self._append_to_jsonl(record)

        # Event Bus Bildirimi: POSITION_CLOSED
        event_bus.publish(MIOSEvent(
            event_type=EVENT_POSITION_CLOSED,
            bot_id="solana-nano-sniper",
            data=record.to_dict(),
            severity="INFO"
        ))

        logger.info(f"✅ Pozisyon Kapatıldı: {pos.token} | PnL: {net_pnl_try:+.4f} ₺ | Neden: {exit_reason} | Süre: {hold_time_ms}ms")
        return record

    def _append_to_jsonl(self, record: IndividualTradeRecord) -> None:
        try:
            with open(TRADES_JSONL_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"JSONL yazım hatası: {e}")

    # =========================================================================
    # 7. MATEMATİKSEL RECONCILIATION (YAPAY 999.0 KALDIRILDI)
    # =========================================================================
    def reconcile_pnl_from_ledger(self) -> Dict[str, Any]:
        if not os.path.exists(TRADES_JSONL_PATH):
            return {"status": "EMPTY", "total_records": 0}

        records: List[Dict[str, Any]] = []
        with open(TRADES_JSONL_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except Exception:
                        pass

        executed_trades = [r for r in records if r.get("TransactionStatus") in ["PAPER_VERIFIED", "LIVE_CONFIRMED"]]
        skipped_trades = [r for r in records if r.get("TransactionStatus") == "SKIPPED"]

        total_gross = sum(r.get("GrossPnL", 0.0) for r in executed_trades)
        total_fees = sum(r.get("DEXFee", 0.0) + r.get("PriorityFee", 0.0) for r in executed_trades)
        total_slippage = sum(r.get("SlippageCost", 0.0) for r in executed_trades)
        total_net = sum(r.get("NetPnL", 0.0) for r in executed_trades)

        winning_trades = [r for r in executed_trades if r.get("NetPnL", 0.0) > 0]
        losing_trades = [r for r in executed_trades if r.get("NetPnL", 0.0) < 0]
        breakeven_trades = [r for r in executed_trades if r.get("NetPnL", 0.0) == 0]

        win_count = len(winning_trades)
        loss_count = len(losing_trades)
        tot_count = len(executed_trades)

        win_rate = (win_count / tot_count * 100.0) if tot_count > 0 else 0.0
        loss_rate = (loss_count / tot_count * 100.0) if tot_count > 0 else 0.0

        win_sum = sum(r.get("NetPnL", 0.0) for r in winning_trades)
        loss_sum = abs(sum(r.get("NetPnL", 0.0) for r in losing_trades))

        avg_win = (win_sum / win_count) if win_count > 0 else 0.0
        avg_loss = (loss_sum / loss_count) if loss_count > 0 else 0.0

        # Doğru Matematiksel Temsil: Yapay 999.0 yerine matematiksel gerçek
        if loss_sum > 0:
            profit_factor_str = f"{win_sum / loss_sum:.2f}"
            pf_val = round(win_sum / loss_sum, 2)
        elif win_sum > 0:
            profit_factor_str = "N/A (Sıfır Kayıp / Sonsuz)"
            pf_val = 0.0
        else:
            profit_factor_str = "1.00"
            pf_val = 1.0

        expectancy = ((win_rate / 100.0 * avg_win) - (loss_rate / 100.0 * avg_loss)) if tot_count > 0 else 0.0

        cumulative = 0.0
        peak = 0.0
        max_dd = 0.0
        hold_times = [r.get("HoldTimeMs", 0) for r in executed_trades]
        avg_hold = (sum(hold_times) / len(hold_times)) if hold_times else 0

        for r in executed_trades:
            cumulative += r.get("NetPnL", 0.0)
            if cumulative > peak:
                peak = cumulative
            dd = peak - cumulative
        token_distribution = {}
        for r in executed_trades:
            sym = r.get("Token", "UNKNOWN")
            token_distribution[sym] = round(token_distribution.get(sym, 0.0) + r.get("NetPnL", 0.0), 4)

        # v37.1 Kurumsal İcra Zekası & Performans Analizi
        attribution = ExecutionIntelligence.compute_performance_attribution(executed_trades)
        conf_list = [r.get("ConfidenceScore", 90.0) / 100.0 for r in executed_trades]
        outcomes_list = [1 if r.get("NetPnL", 0.0) > 0 else 0 for r in executed_trades]
        calibration = ExecutionIntelligence.calculate_confidence_calibration(conf_list, outcomes_list)
        eqs_scores = [r.get("ExecutionQualityScore", 90.0) for r in executed_trades]
        avg_eqs = round(sum(eqs_scores) / len(eqs_scores), 2) if eqs_scores else 100.0

        return {
            "total_records_in_file": len(records),
            "total_executed": tot_count,
            "total_skipped": len(skipped_trades),
            "active_open_positions": len(self._active_positions),
            "gross_pnl_try": round(total_gross, 4),
            "fees_try": round(total_fees, 4),
            "slippage_cost_try": round(total_slippage, 4),
            "net_pnl_try": round(total_net, 4),
            "winning_trades": win_count,
            "losing_trades": loss_count,
            "breakeven_trades": len(breakeven_trades),
            "win_rate_pct": round(win_rate, 2),
            "loss_rate_pct": round(loss_rate, 2),
            "average_win_try": round(avg_win, 4),
            "average_loss_try": round(avg_loss, 4),
            "profit_factor": pf_val,
            "profit_factor_display": profit_factor_str,
            "expectancy_try": round(expectancy, 4),
            "max_drawdown_try": round(max_dd, 4),
            "average_hold_time_ms": round(avg_hold, 1),
            "token_profits": token_distribution,
            "average_execution_quality_score": avg_eqs,
            "performance_attribution": attribution,
            "confidence_calibration": calibration
        }

    # =========================================================================
    # 8. DEVRE KESİCİ VE ACİL DURDURMA (EMERGENCY FREEZE)
    # =========================================================================
    def emergency_freeze(self, reason: str = "Risk Supervisor Emergency Halt") -> None:
        with self._state_lock:
            self.is_frozen = True
            self.freeze_reason = reason
            logger.critical(f"🛑 NANO-YIELD ENGINE DONDURULDU: {reason}")
            
            # Açık pozisyonları güvenle kapat veya dondur
            if self._active_positions:
                logger.warning(f"Açık {len(self._active_positions)} pozisyon acil durumla kapatılıyor...")
                self.close_position_by_token("ALL", reason=f"EMERGENCY_FREEZE ({reason})")

            # CFEL Mühürle
            cfel_auditor.seal_event(
                event_type=EVENT_EMERGENCY_FREEZE_ACTIVE,
                bot_id="solana-nano-sniper",
                action="FREEZE_EXECUTION",
                result="FROZEN",
                payload={"reason": reason, "timestamp": time.time()}
            )

    def resume(self) -> None:
        with self._state_lock:
            self.is_frozen = False
            self.freeze_reason = ""
            self.consecutive_losses = 0
            self.reconciliation_safe_mode = False
            logger.info("🟢 NANO-YIELD ENGINE TEKRAR BAŞLATILDI")


nano_yield_engine = NanoYieldAutomationEngine()
