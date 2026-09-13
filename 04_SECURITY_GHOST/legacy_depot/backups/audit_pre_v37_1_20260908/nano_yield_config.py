#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
  MIOS CORE - NANO-YIELD STRATEGY CONFIGURATION & RISK GATES
  Module       : 01_MIOS_CORE/bot_depot/nano_yield_config.py
  Version      : v37.0-EnterpriseNano
  Strategy     : nano-yield-1.8 | Risk: risk-2.4 | Schema: EGF-2.5
================================================================================
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class NanoYieldConfig:
    # Sürüm Bilgileri
    bot_version: str = "v37.1-EnterpriseNano"
    strategy_version: str = "nano-yield-1.8-ExecIntel"
    risk_version: str = "risk-2.4-AdaptiveGates"
    data_schema: str = "EGF-2.6"

    # İcra ve Veri Modu
    execution_mode: str = "PAPER"
    data_mode: str = "REAL"

    # Fırsat & Bütçe Parametreleri
    target_yield_per_sec_try: float = 0.15
    min_position_size_try: float = 100.00
    max_position_size_try: float = 300.00
    default_micro_budget_try: float = 150.00

    # Risk & Kâr / Zarar Kapıları
    ai_confidence_gate: float = 0.90         # %90+ Ultra Yüksek Güven Filtresi
    max_slippage_bps: int = 25               # %0.25 Maksimum Kayma Toleransı
    take_profit_bps: int = 120               # %1.20 Take Profit Hedefi
    hard_stop_bps: int = 60                  # %0.60 Stop-Loss Sermaye Koruma
    min_liquidity_usd: float = 50000.0       # Minimum Havuz Likiditesi ($50k)
    max_price_age_sec: float = 5.0           # Maksimum Fiyat Yaşı (5 saniye)
    max_hold_time_ms: int = 10000            # Maksimum Pozisyonda Kalma Süresi (10s)
    max_quote_age_ms: int = 3000             # Maksimum Quote Yaşı (3s)
    max_rpc_latency_ms: int = 2000           # Maksimum RPC Gecikmesi (2000ms)

    # Günlük ve Ardışık Zarar Limitleri (Circuit Breakers)
    max_daily_loss_try: float = 150.00       # Günlük Maksimum Zarar Limiti
    max_consecutive_loss: int = 3            # Maksimum Ardışık Kayıp Sayısı

    # Canlı İcra, Jupiter ve RPC Yapılandırması
    jupiter_quote_api: str = "https://api.jup.ag/swap/v1/quote"
    jupiter_swap_api: str = "https://api.jup.ag/swap/v1/swap"
    active_positions_path: str = "/home/yunuskalkan/01_MIOS_CORE/bot_depot/data/nano_yield_active_positions.json"
    ata_rent_sol: float = 0.00203928         # Standart SPL ATA rent maliyeti (~0.00204 SOL)
    sol_reserve_sol: float = 0.015           # Cüzdanda zorunlu tutulması gereken SOL rezervi
    guardian_heartbeat_timeout_sec: float = 30.0 # Guardian'dan haber alınamazsa yeni işlem engeli
    signal_dedup_window_sec: float = 45.0    # Aynı sinyalin tekrar icrasını önleme penceresi
    rpc_failover_list: List[str] = None

    # Token Evreni (Solana Mainnet)
    token_universe: Dict[str, Dict[str, str]] = None

    def __post_init__(self):
        if self.rpc_failover_list is None:
            self.rpc_failover_list = [
                "https://api.mainnet-beta.solana.com",
                "https://solana-rpc.publicnode.com",
                "https://rpc.ankr.com/solana"
            ]
        if self.token_universe is None:
            self.token_universe = {
                "SOL": {"name": "Solana", "mint": "So11111111111111111111111111111111111111112", "coingecko_id": "solana"},
                "WIF": {"name": "dogwifhat", "mint": "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm", "coingecko_id": "dogwifcoin"},
                "BONK": {"name": "Bonk", "mint": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263", "coingecko_id": "bonk"},
                "JUP": {"name": "Jupiter", "mint": "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN", "coingecko_id": "jupiter-exchange-solana"},
                "RAY": {"name": "Raydium", "mint": "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R", "coingecko_id": "raydium"},
                "PYTH": {"name": "Pyth Network", "mint": "HZ1JovNiPvGrGNiiYvEozEVgZ58xaU3RKwX8eACQBCt3", "coingecko_id": "pyth-network"},
                "RENDER": {"name": "Render", "mint": "rndrizKT3Dn1i7eo9YvqkQCVT9Z57gAZ9hCYFr4bkU", "coingecko_id": "render-token"},
                "SAMO": {"name": "Samoyedcoin", "mint": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU", "coingecko_id": "samoyedcoin"},
                "BOME": {"name": "Book of Meme", "mint": "ukHH6c7mMyPWCf1b9pnWe25TSpkDDt3H5pQZgZ74J82", "coingecko_id": "book-of-meme"},
                "POPCAT": {"name": "Popcat", "mint": "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr", "coingecko_id": "popcat"},
                "DRIFT": {"name": "Drift Protocol", "mint": "DriFtupJYLTosbwoN8koMbEYSx54aFAVLddWsbksjwg7", "coingecko_id": "drift-protocol"},
                "TNSR": {"name": "Tensor", "mint": "TNSRxcUxoT9xBG3de7PiJyTDYu7kskLqcpddxnEJAS6", "coingecko_id": "tensor"},
                "SLERF": {"name": "Slerf", "mint": "71GffhDvhc5wN7bFmP1i7D645BvDskT5D5h6gQy4pump", "coingecko_id": "slerf"},
                "ORCA": {"name": "Orca", "mint": "orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE", "coingecko_id": "orca"},
                "MOTHER": {"name": "Mother Iggy", "mint": "3S8qX1MsMqRbiwKg2cQYX7nis1oHMghWBDisY6nMpump", "coingecko_id": "mother-iggy"},
                "IO": {"name": "io.net", "mint": "BZLbGTNCSFfoth2GYDtWr7e4imWzpR5jqcUuGEwr646K", "coingecko_id": "io-net"},
                "PENGU": {"name": "Pudgy Penguins", "mint": "2zMMhcVQEXDtdE6vsFS7S7D5oUodfJHE8vd1gnBouauv", "coingecko_id": "pudgy-penguins"},
                "JTO": {"name": "Jito", "mint": "jtojtomepa8beP8AuQc6eXt5FriJwfFMwQx2v2f9mCL", "coingecko_id": "jito-governance-token"},
                "MEW": {"name": "cat in a dogs world", "mint": "MEW1gQWJ3nEXg2qgERiKu7FAFj79PHvQVREQUzScPP5", "coingecko_id": "cat-in-a-dogs-world"},
                "USDC": {"name": "USD Coin", "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "coingecko_id": "usd-coin"}
            }

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


nano_config = NanoYieldConfig()
