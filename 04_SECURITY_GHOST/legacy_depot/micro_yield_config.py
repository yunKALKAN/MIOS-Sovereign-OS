# ============================================================
# MIOS NANO-YIELD AUTONOMOUS CAPITAL CONFIGURATION v1
# ============================================================

execution_mode: str = "LIVE"
wallet_address: str = "GPFL3KoAZkiArX6e3hogpQQWKFVnQg24tCPvzaD5tukq"
rpc_endpoint: str = "https://api.mainnet-beta.solana.com"

# Sermaye & Slot Koruması
trade_budget_sol: float = 0.001
ata_rent_reserve_sol: float = 0.002039
safety_buffer_sol: float = 0.000400

# Dinamik Kasa Tabanı (0.002 SOL altında alım denenmez)
dynamic_buy_floor_sol: float = 0.002

# Slot & Risk Sınırları
max_open_positions: int = 1
daily_loss_limit_try: float = -5.00
circuit_breaker_cooldown_seconds: int = 4 * 60 * 60

# Kâr Kilidi Eşikleri
profit_lock_trigger_try: float = 25.00
profit_lock_ratio: float = 0.50

# Strateji Zamanlama & Çıkış
staged_tp_bps: int = 50          # +%0.50 eşiği
staged_tp_hold_seconds: int = 90 # 90 saniye barajı
max_hold_seconds: int = 180      # 180 saniye timeout
sell_slippage_bps: int = 350     # Volatilite korumalı satış toleransı
