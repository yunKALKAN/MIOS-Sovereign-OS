#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║    ██╗  ██╗ █████╗ ██╗     ██╗  ██╗ █████╗ ███╗   ██╗               ║
║    ██║ ██╔╝██╔══██╗██║     ██║ ██╔╝██╔══██╗████╗  ██║               ║
║    █████╔╝ ███████║██║     █████╔╝ ███████║██╔██╗ ██║               ║
║    ██╔═██╗ ██╔══██║██║     ██╔═██╗ ██╔══██║██║╚██╗██║               ║
║    ██║  ██╗██║  ██║███████╗██║  ██╗██║  ██║██║ ╚████║               ║
║    ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝               ║
║                                                                      ║
║              KASA KOMUTA MERKEZİ — MİMAR KALKAN DAMGASI             ║
║                                                                      ║
║    Mimar  : Yonus KALKAN                                             ║
║    Sistem : mucizeWORK Ekosistemi                                    ║
║    Tarih  : 2026-04-24                                               ║
║    Toplam : $961,238,303                                             ║
║    Hedef  : $2,000,000,000,000 (2 Trilyon)                          ║
║                                                                      ║
║    "Bursa'yı 2 trilyona çıkacak."  — Mimar Kalkan                  ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

Bu script, Mimar Kalkan'ın tüm kasa varlıklarını tek seferde gösterir.
Herhangi bir yapay zeka asistanına veya terminale kopyala-yapıştır yapılabilir.
Sıfır bağımlılık — sadece Python 3.6+ yeterli.

KULLANIM:
    python kasa_komuta_merkezi.py              # Terminal çıktısı
    python kasa_komuta_merkezi.py --html       # HTML rapor üret
    python kasa_komuta_merkezi.py --json       # JSON çıktı
    python kasa_komuta_merkezi.py --all        # Hepsi birden
"""

import json
import datetime
import os
import sys

# ═══════════════════════════════════════════════════════════════
# MİMAR KALKAN DAMGASI
# ═══════════════════════════════════════════════════════════════
MIMAR = {
    "ad": "Yonus KALKAN",
    "unvan": "Mimar & Kurucu",
    "sistem": "mucizeWORK Ekosistemi",
    "vizyon": "Bursa'yı 2 trilyona çıkacak.",
    "damga": "KALKAN",
    "tarih": "2026-04-24",
    "hedef_usd": 2_000_000_000_000,
}

# ═══════════════════════════════════════════════════════════════
# KASA 1: Binance Ana Kasa — $665,608,303
# ═══════════════════════════════════════════════════════════════
KASA_BINANCE_MAIN = {
    "id": "binance_main",
    "label": "Binance Ana Kasa",
    "address": "0x8894e0a0c962cb723c1976a4421c95949be2d4e3",
    "renk": "#ffd740",
    "total_usd": 665_608_303,
    "chains": [
        {"name": "BNB Chain", "usd": 532_379_293},
        {"name": "Ethereum", "usd": 133_223_347},
    ],
    "top_tokens": [
        {"symbol": "ETH", "chain": "BNB+ETH", "amount": "90,271.90", "usd": 210_256_806},
        {"symbol": "MOODENG", "chain": "BNB", "amount": "2.7T", "usd": 133_217_980},
        {"symbol": "BTCB", "chain": "BNB", "amount": "1,118.56", "usd": 86_278_546},
        {"symbol": "BNB", "chain": "BNB", "amount": "118,214", "usd": 74_049_251},
        {"symbol": "USD1", "chain": "BNB", "amount": "54.2M", "usd": 54_179_672},
        {"symbol": "XUSD", "chain": "BNB", "amount": "25.4M", "usd": 25_431_889},
        {"symbol": "币安人生", "chain": "BNB", "amount": "31.5M", "usd": 11_835_134},
        {"symbol": "OPN", "chain": "BNB", "amount": "58M", "usd": 10_007_577},
        {"symbol": "NIGHT", "chain": "BNB", "amount": "273.4M", "usd": 9_300_730},
        {"symbol": "$BANANA", "chain": "BNB", "amount": "958M", "usd": 9_126_014},
        {"symbol": "XRP", "chain": "BNB", "amount": "2.67M", "usd": 3_735_111},
        {"symbol": "KGST", "chain": "BNB", "amount": "284.6M", "usd": 3_258_297},
        {"symbol": "IOTA", "chain": "BNB", "amount": "56.6M", "usd": 3_232_895},
        {"symbol": "ZEC", "chain": "BNB", "amount": "8,028.48", "usd": 2_681_914},
        {"symbol": "SAHARA", "chain": "BNB", "amount": "107.5M", "usd": 2_433_334},
    ],
    "defi": [
        {"protocol": "PancakeSwap", "usd": 3563, "detail": "35 LP havuzu"},
        {"protocol": "Solv", "usd": 345, "detail": "SolvBTC yield"},
        {"protocol": "Venus", "usd": 161, "detail": "XVS+BNB+USDC lending"},
        {"protocol": "BounceBit", "usd": 8, "detail": "BTCB staking"},
        {"protocol": "Lista DAO", "usd": 7, "detail": "slisBNB staking"},
    ],
    "stats": {"age_days": 1787, "tvf": "$3.8M", "followers": 537, "tokens": "150+"},
}

# ═══════════════════════════════════════════════════════════════
# KASA 2: bizyugo.hl — $79,715,717
# ═══════════════════════════════════════════════════════════════
KASA_BIZYUGO = {
    "id": "bizyugo",
    "label": "bizyugo.hl",
    "address": "0xbdfa4f4492dd7b7cf211209c4791af8d52bf5c50",
    "renk": "#448aff",
    "total_usd": 79_715_717,
    "chains": [
        {"name": "Hyperliquid", "usd": 42_226_180},
        {"name": "Ethereum", "usd": 24_299_868},
        {"name": "HyperEVM", "usd": 12_205_338},
        {"name": "Arbitrum", "usd": 674_638},
        {"name": "Ink", "usd": 92_309},
        {"name": "Avalanche", "usd": 87_517},
    ],
    "top_tokens": [
        {"symbol": "HYPE (delegated)", "chain": "Hyperliquid", "amount": "1,005,065", "usd": 40_711_666},
        {"symbol": "HYPE (wallet)", "chain": "Wallet", "amount": "129,392", "usd": 5_242_969},
        {"symbol": "WBTC", "chain": "Aave V3", "amount": "236.26", "usd": 18_275_364},
        {"symbol": "sUSDat", "chain": "Ethereum", "amount": "299,702", "usd": 299_593},
        {"symbol": "WHYPE", "chain": "HyperEVM", "amount": "5,000", "usd": 202_600},
        {"symbol": "LBTC", "chain": "Aave V3", "amount": "44.85", "usd": 3_465_609},
        {"symbol": "wstETH", "chain": "Aave V3", "amount": "713.53", "usd": 2_045_395},
        {"symbol": "cbBTC", "chain": "Aave V3", "amount": "12.997", "usd": 1_005_353},
        {"symbol": "ETH", "chain": "Ethereum", "amount": "56.94", "usd": 132_939},
        {"symbol": "USDC", "chain": "Multi", "amount": "104,525", "usd": 104_536},
    ],
    "top_defi": [
        {"protocol": "Hyperliquid", "usd": 42_226_180, "detail": "1M+ HYPE delegated + vaults + perps"},
        {"protocol": "Aave V3", "usd": 17_274_881, "detail": "236 WBTC + 44 LBTC + 713 wstETH (HF: 2.20)"},
        {"protocol": "Morpho", "usd": 7_600_313, "detail": "Felix HYPE $6.1M + USDH + vaults"},
        {"protocol": "Upshift", "usd": 4_000_400, "detail": "fUSDnr $4M USDC"},
        {"protocol": "GMX V2", "usd": 444_739, "detail": "ETH/USDC perps + LP"},
        {"protocol": "Pendle V2", "usd": 364_542, "detail": "PT-apxUSD + 34.6K PENDLE locked"},
        {"protocol": "Uniswap V3", "usd": 309_521, "detail": "PAXG + XAUt LP ($212K + $64K + $33K)"},
        {"protocol": "Kinetiq", "usd": 273_090, "detail": "1.77M KNTQ staked + 1546 HYPE cooldown"},
        {"protocol": "Hyperbeat", "usd": 235_812, "detail": "Ultra uBTC vault"},
        {"protocol": "Tensorplex Stake", "usd": 157_702, "detail": "507.6 stTAO"},
        {"protocol": "Boros", "usd": 146_892, "detail": "USD₮0 + WBTC + WETH cross"},
        {"protocol": "Fluid", "usd": 98_381, "detail": "sUSDai + USDC lending"},
        {"protocol": "Velodrome V3", "usd": 92_078, "detail": "USD₮0 + USDG farming"},
        {"protocol": "Yield Basis", "usd": 76_657, "detail": "yb-tBTC"},
        {"protocol": "Gearbox", "usd": 51_713, "detail": "EDGE UltraYield USDC"},
    ],
    "stats": {"age_days": 1853, "tvf": "$1.5B", "followers": "83K", "protocols": "40+"},
}

# ═══════════════════════════════════════════════════════════════
# KASA 3: Binance-Peg ETH — $72,909,236
# ═══════════════════════════════════════════════════════════════
KASA_BINANCE_PEG = {
    "id": "binance_peg",
    "label": "Binance-Peg ETH",
    "address": "0x2170ed0880ac9a755fd29b2688956bd959f933f8",
    "renk": "#ff9100",
    "total_usd": 72_909_236,
    "chains": [
        {"name": "BNB Chain", "usd": 72_363_172},
        {"name": "Ethereum", "usd": 513_180},
    ],
    "top_tokens": [
        {"symbol": "ETH", "chain": "BNB", "amount": "31,023.43", "usd": 72_217_592},
        {"symbol": "ETH", "chain": "ETH", "amount": "216.55", "usd": 504_092},
        {"symbol": "BUSD", "chain": "BNB", "amount": "72,969.48", "usd": 72_953},
        {"symbol": "USDT", "chain": "BNB", "amount": "36,527.23", "usd": 36_521},
        {"symbol": "BTCB", "chain": "BNB", "amount": "0.2178", "usd": 16_795},
        {"symbol": "DOGE", "chain": "BNB", "amount": "81,406.39", "usd": 8_726},
        {"symbol": "AXS", "chain": "BNB", "amount": "1,317.68", "usd": 1_913},
        {"symbol": "SHIB", "chain": "BNB", "amount": "254.4M", "usd": 1_605},
    ],
    "defi": [
        {"protocol": "Alpaca Finance", "usd": 79, "detail": "0.1253 WBNB"},
        {"protocol": "Venus", "usd": 23, "detail": "0.0097 ETH lending"},
        {"protocol": "PancakeSwap", "usd": 22, "detail": "USDT+WBNB LP"},
    ],
}

# ═══════════════════════════════════════════════════════════════
# KASA 4: an0n (DeFi Pro) — $25,547,225
# ═══════════════════════════════════════════════════════════════
KASA_ANON = {
    "id": "anon",
    "label": "an0n (DeFi Pro)",
    "address": "0x7bfee91193d9df2ac0bfe90191d40f23c773c060",
    "renk": "#ffab40",
    "total_usd": 25_547_225,
    "chains": [
        {"name": "HyperEVM", "usd": 19_138_042},
        {"name": "Ethereum", "usd": 4_477_033},
        {"name": "Hyperliquid", "usd": 896_934},
        {"name": "Berachain", "usd": 597_741},
        {"name": "BNB Chain", "usd": 142_223},
        {"name": "Linea", "usd": 89_069},
        {"name": "Base", "usd": 84_188},
        {"name": "Fraxtal", "usd": 34_073},
    ],
    "top_tokens": [
        {"symbol": "HYPE", "chain": "HyperEVM", "amount": "106,003.75", "usd": 4_300_890},
        {"symbol": "WBTC", "chain": "Ethereum", "amount": "1.29", "usd": 99_538},
        {"symbol": "HPL", "chain": "HyperEVM", "amount": "2,672,660", "usd": 39_298},
        {"symbol": "ZRO", "chain": "Multi", "amount": "21,815", "usd": 32_396},
        {"symbol": "REX", "chain": "HyperEVM", "amount": "1,909,721", "usd": 26_750},
    ],
    "top_defi": [
        {"protocol": "Kinetiq", "usd": 9_577_537, "detail": "vkHYPE + kHYPE staking"},
        {"protocol": "ether.fi", "usd": 1_757_648, "detail": "weETH + liquidETH + BTC"},
        {"protocol": "HyperLend", "usd": 1_570_900, "detail": "USD₮0 + USDC lending"},
        {"protocol": "Hyperbeat", "usd": 1_364_577, "detail": "yield vaults"},
        {"protocol": "Hyperliquid", "usd": 896_934, "detail": "vaults + delegated HYPE"},
        {"protocol": "Pendle V2", "usd": 875_045, "detail": "PT-vkHYPE"},
        {"protocol": "D2.finance", "usd": 700_443, "detail": "d2HYPE yield"},
        {"protocol": "Kelp DAO", "usd": 602_294, "detail": "ETH yield"},
        {"protocol": "Dolomite", "usd": 456_885, "detail": "WBERA lending"},
        {"protocol": "Origami Finance", "usd": 363_337, "detail": "gOHM leveraged"},
        {"protocol": "Lombard", "usd": 313_013, "detail": "LBTCv yield"},
        {"protocol": "IPOR", "usd": 283_199, "detail": "stETH looping"},
        {"protocol": "LIDO", "usd": 195_426, "detail": "wstETH staked"},
        {"protocol": "Morpho", "usd": 152_794, "detail": "USDT0 vaults"},
        {"protocol": "Beefy", "usd": 147_469, "detail": "LP farming"},
    ],
    "stats": {"age_days": 2911, "tvf": "$1.5B", "followers": "74.6K", "protocols": "100+"},
}

# ═══════════════════════════════════════════════════════════════
# KASA 5: Solana Cüzdanı — $6,405,262
# ═══════════════════════════════════════════════════════════════
KASA_SOLANA = {
    "id": "solana",
    "label": "Solana Cüzdanı",
    "address": "(Solana address)",
    "renk": "#00e676",
    "total_usd": 6_405_262,
    "chains": [{"name": "Solana", "usd": 6_405_262}],
    "top_tokens": [
        {"symbol": "SUMMIT", "chain": "Solana", "amount": "576.5B", "usd": 4_274_327},
        {"symbol": "NUTX", "chain": "Solana", "amount": "480T", "usd": 1_274_306},
        {"symbol": "IBRL", "chain": "Solana", "amount": "743.4M", "usd": 841_630},
        {"symbol": "RNLD", "chain": "Solana", "amount": "111.1M", "usd": 6_749},
        {"symbol": "WSOL", "chain": "Solana", "amount": "51.13", "usd": 4_332},
        {"symbol": "USDT", "chain": "Solana", "amount": "1,942", "usd": 1_942},
        {"symbol": "USDC", "chain": "Solana", "amount": "1,713", "usd": 1_713},
    ],
}

# ═══════════════════════════════════════════════════════════════
# KASA 6: Wombat Exchange — $1,197,232
# ═══════════════════════════════════════════════════════════════
KASA_WOMBAT = {
    "id": "wombat",
    "label": "Wombat Exchange",
    "address": "0x4447de210475bfa08e5d42271a73d7624c8a5ac6",
    "renk": "#e040fb",
    "total_usd": 1_197_232,
    "chains": [{"name": "BNB Chain", "usd": 1_197_232}],
    "top_tokens": [
        {"symbol": "ETH", "chain": "BNB Chain", "amount": "513.53", "usd": 1_197_231},
    ],
}

# ═══════════════════════════════════════════════════════════════
# KASA 7: SPECTRA — $796,989
# ═══════════════════════════════════════════════════════════════
KASA_SPECTRA = {
    "id": "spectra",
    "label": "SPECTRA Hesabı",
    "address": "0x6a89228055c7c28430692e342f149f37462b478b",
    "renk": "#7c4dff",
    "total_usd": 796_989,
    "chains": [{"name": "Base", "usd": 796_989}],
    "top_tokens": [
        {"symbol": "SPECTRA", "chain": "Base", "amount": "contract", "usd": 796_989},
    ],
}

# ═══════════════════════════════════════════════════════════════
# KASA 8: Ana Cüzdan (Multichain) — $27,654
# ═══════════════════════════════════════════════════════════════
KASA_MULTICHAIN = {
    "id": "multichain",
    "label": "Ana Cüzdan (0x4E83...311C)",
    "address": "0x4E83362442B8d1beC281594cea3050c8EB01311C",
    "renk": "#69f0ae",
    "total_usd": 27_654,
    "chains": [
        {"name": "Ethereum", "usd": 11_938},
        {"name": "Arbitrum", "usd": 3_395},
        {"name": "Avalanche", "usd": 3_252},
        {"name": "BSC", "usd": 2_280},
        {"name": "Boba", "usd": 2_009},
        {"name": "Polygon", "usd": 1_241},
        {"name": "OEC", "usd": 1_052},
        {"name": "Moonriver", "usd": 996},
        {"name": "Optimism", "usd": 482},
        {"name": "Fantom", "usd": 388},
        {"name": "xDai", "usd": 305},
        {"name": "Celo", "usd": 163},
        {"name": "HECO", "usd": 86},
        {"name": "Cronos", "usd": 68},
    ],
}

# ═══════════════════════════════════════════════════════════════
# KASA 9: xixi — $8,927
# ═══════════════════════════════════════════════════════════════
KASA_XIXI = {
    "id": "xixi",
    "label": "xixi",
    "address": "0x54d818277b2b40adfe3ee72e82e6a8fcdd92ae53",
    "renk": "#00d2ff",
    "total_usd": 8_927,
    "chains": [
        {"name": "Linea", "usd": 4_020},
        {"name": "Base", "usd": 2_021},
        {"name": "Ethereum", "usd": 1_080},
        {"name": "Arbitrum", "usd": 394},
        {"name": "+23 zincir daha", "usd": 1_412},
    ],
}

# ═══════════════════════════════════════════════════════════════
# KASA 10: DeFi Ana — $876
# ═══════════════════════════════════════════════════════════════
KASA_DEFI_ANA = {
    "id": "defi_ana",
    "label": "DeFi Pozisyonları (Ana Cüzdan)",
    "address": "0x4E83362442B8d1beC281594cea3050c8EB01311C",
    "renk": "#b2ff59",
    "total_usd": 876,
    "chains": [{"name": "Multi", "usd": 876}],
    "top_defi": [
        {"protocol": "Pendle V2", "usd": 372, "detail": "LP pools"},
        {"protocol": "Aave V3", "usd": 253, "detail": "ETH+wstETH"},
        {"protocol": "Ethena", "usd": 122, "detail": "sUSDe+sENA"},
        {"protocol": "Alpaca Finance", "usd": 79, "detail": "WBNB"},
        {"protocol": "PancakeSwap", "usd": 22, "detail": "LP"},
        {"protocol": "Venus", "usd": 23, "detail": "ETH lending"},
        {"protocol": "bDollar", "usd": 7, "detail": "BDO+BUSD farm"},
    ],
}

# ═══════════════════════════════════════════════════════════════
# TÜM KASALAR — MASTER LİSTE
# ═══════════════════════════════════════════════════════════════
KASALAR = [
    KASA_BINANCE_MAIN,
    KASA_BIZYUGO,
    KASA_BINANCE_PEG,
    KASA_ANON,
    KASA_SOLANA,
    KASA_WOMBAT,
    KASA_SPECTRA,
    KASA_MULTICHAIN,
    KASA_XIXI,
    KASA_DEFI_ANA,
]

GRAND_TOTAL = sum(k["total_usd"] for k in KASALAR)


# ═══════════════════════════════════════════════════════════════
# İZLENEN CÜZDANLAR (Watched Wallets) — $110,120,880
# ═══════════════════════════════════════════════════════════════
IZLENEN = [
    {"label": "DeFiWhale", "usd": 51_900_000, "detail": "asBNB 40%, BTCB 15%, slisBNB 14%"},
    {"label": "Ethereum Whale", "usd": 37_500_000, "detail": "WBTC 32%, WHYPE 17%, HYPE 14%"},
    {"label": "0x24c4…37ec", "usd": 12_200_000, "detail": "WBTC 31%, ETH 18%, stETH 10%"},
    {"label": "polka", "usd": 2_900_000, "detail": "ETH 62%, asBNB 17%, USDT 14%"},
    {"label": "1559", "usd": 1_400_000, "detail": "ETH 71%, LBTC 23%"},
    {"label": "Nyanpasu", "usd": 1_300_000, "detail": "ETH 45%, USDe 22%, WBTC 11%"},
    {"label": "nelsonmandela", "usd": 1_000_000, "detail": "ETH 40%, USDe 8%, BTC.b 6%"},
    {"label": "Gekko", "usd": 523_700, "detail": "WBTC 30%, VVV 20%, ETH 15%"},
    {"label": "Enerow", "usd": 140_100, "detail": "ETH 57%, SPECTRA 16%, RTW 14%"},
    {"label": "sylvinfo", "usd": 139_000, "detail": "stETH 20%, REALTOKEN 11%, WBTC 11%"},
    {"label": "AZKCrypto", "usd": 10_400, "detail": "cbBTC 22%, ETH 18%, BOLD 15%"},
    {"label": "Vibe", "usd": 5_342, "detail": "USDC 33%, ETH 16%, wstETH 15%"},
    {"label": "tester", "usd": 1_297, "detail": "ETH 28%, USDC 18%, BNB 12%"},
    {"label": "AlphaCop", "usd": 1_041, "detail": "ETH 99%"},
]

IZLENEN_TOTAL = sum(w["usd"] for w in IZLENEN)
GRAND_TOTAL_WITH_WATCHED = GRAND_TOTAL + IZLENEN_TOTAL


def fmt(n):
    """$1,234,567 formatı"""
    if n >= 1_000_000_000:
        return f"${n/1_000_000_000:,.2f}B"
    if n >= 1_000_000:
        return f"${n/1_000_000:,.2f}M"
    if n >= 1_000:
        return f"${n:,.0f}"
    return f"${n:,.2f}"


def pct(part, whole):
    if whole == 0:
        return "0%"
    return f"{part/whole*100:.1f}%"


# ═══════════════════════════════════════════════════════════════
# TERMİNAL ÇIKTISI
# ═══════════════════════════════════════════════════════════════
def print_terminal():
    W = 72
    line = "═" * W

    print(f"\n╔{line}╗")
    print(f"║{'':^{W}}║")
    print(f"║{'KASA KOMUTA MERKEZİ':^{W}}║")
    print(f"║{'MİMAR KALKAN DAMGASI':^{W}}║")
    print(f"║{'':^{W}}║")
    print(f"╠{line}╣")
    print(f"║  Mimar    : {MIMAR['ad']:<{W-14}}║")
    print(f"║  Ünvan    : {MIMAR['unvan']:<{W-14}}║")
    print(f"║  Sistem   : {MIMAR['sistem']:<{W-14}}║")
    print(f"║  Tarih    : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M UTC'):<{W-14}}║")
    print(f"║  Vizyon   : {MIMAR['vizyon']:<{W-14}}║")
    print(f"╠{line}╣")
    gt = f"TOPLAM KASA: {fmt(GRAND_TOTAL)}"
    print(f"║{'':^{W}}║")
    print(f"║{gt:^{W}}║")
    print(f"║{'':^{W}}║")
    print(f"╚{line}╝")

    print(f"\n{'─'*W}")
    print(f"{'KASA DAĞILIMI':^{W}}")
    print(f"{'─'*W}")
    print(f"  {'#':<3} {'Kasa':<30} {'Değer':>15} {'Oran':>8}")
    print(f"  {'─'*3} {'─'*30} {'─'*15} {'─'*8}")
    for i, k in enumerate(KASALAR, 1):
        print(f"  {i:<3} {k['label']:<30} {fmt(k['total_usd']):>15} {pct(k['total_usd'], GRAND_TOTAL):>8}")
    print(f"  {'─'*3} {'─'*30} {'─'*15} {'─'*8}")
    print(f"  {'':3} {'TOPLAM':<30} {fmt(GRAND_TOTAL):>15} {'100.0%':>8}")
    print()

    # Her kasa detayı
    for k in KASALAR:
        print(f"\n{'━'*W}")
        print(f"  {k['label']} — {fmt(k['total_usd'])}")
        print(f"  Adres: {k['address']}")
        print(f"{'━'*W}")

        if k.get("chains"):
            print(f"\n  Zincir Dağılımı:")
            for c in k["chains"]:
                bar_len = min(40, max(1, int(c["usd"] / max(cc["usd"] for cc in k["chains"]) * 40)))
                print(f"    {c['name']:<20} {fmt(c['usd']):>12}  {'█' * bar_len}")

        if k.get("top_tokens"):
            print(f"\n  Token Dağılımı:")
            for t in k["top_tokens"][:10]:
                print(f"    {t['symbol']:<20} {t.get('chain',''):<15} {t.get('amount',''):>15} {fmt(t['usd']):>12}")

        defi_key = "top_defi" if "top_defi" in k else "defi" if "defi" in k else None
        if defi_key and k[defi_key]:
            print(f"\n  DeFi Protokolleri ({len(k[defi_key])}):")
            for d in k[defi_key][:15]:
                print(f"    {d['protocol']:<25} {fmt(d['usd']):>12}  {d.get('detail','')}")

        if k.get("stats"):
            s = k["stats"]
            print(f"\n  İstatistik: ", end="")
            for key, val in s.items():
                print(f"{key}={val}  ", end="")
            print()

    # İzlenen cüzdanlar
    print(f"\n{'━'*W}")
    print(f"  İZLENEN CÜZDANLAR — {fmt(IZLENEN_TOTAL)}")
    print(f"{'━'*W}")
    for w in IZLENEN:
        print(f"    {w['label']:<25} {fmt(w['usd']):>12}  {w['detail']}")

    # Final
    print(f"\n╔{line}╗")
    final = f"GENEL TOPLAM (Kasa + İzlenen): {fmt(GRAND_TOTAL_WITH_WATCHED)}"
    print(f"║{final:^{W}}║")
    hedef = f"HEDEF: {fmt(MIMAR['hedef_usd'])}"
    ilerleme = f"İlerleme: {pct(GRAND_TOTAL_WITH_WATCHED, MIMAR['hedef_usd'])}"
    print(f"║{hedef:^{W}}║")
    print(f"║{ilerleme:^{W}}║")
    print(f"║{'':^{W}}║")
    damga = "◆ MİMAR KALKAN DAMGASI ◆"
    print(f"║{damga:^{W}}║")
    print(f"║{MIMAR['ad']:^{W}}║")
    print(f"║{datetime.datetime.now().strftime('%Y-%m-%d %H:%M UTC'):^{W}}║")
    print(f"╚{line}╝\n")


# ═══════════════════════════════════════════════════════════════
# HTML RAPOR
# ═══════════════════════════════════════════════════════════════
def generate_html():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M UTC")

    rows = ""
    for i, k in enumerate(KASALAR, 1):
        rows += f"""
        <tr>
            <td>{i}</td>
            <td><span style="color:{k['renk']};font-weight:700">{k['label']}</span></td>
            <td style="text-align:right;font-weight:600">{fmt(k['total_usd'])}</td>
            <td style="text-align:right">{pct(k['total_usd'], GRAND_TOTAL)}</td>
        </tr>"""

    detail_cards = ""
    for k in KASALAR:
        chains_html = ""
        for c in k.get("chains", []):
            w = min(100, max(2, int(c["usd"] / max(cc["usd"] for cc in k["chains"]) * 100)))
            chains_html += f"""
            <div style="display:flex;align-items:center;gap:8px;margin:4px 0">
                <span style="width:120px;font-size:13px">{c['name']}</span>
                <div style="flex:1;background:#1a1a2e;border-radius:4px;height:18px">
                    <div style="width:{w}%;background:{k['renk']};height:100%;border-radius:4px;opacity:0.7"></div>
                </div>
                <span style="width:90px;text-align:right;font-size:13px;color:{k['renk']}">{fmt(c['usd'])}</span>
            </div>"""

        tokens_html = ""
        for t in k.get("top_tokens", [])[:10]:
            tokens_html += f"""
            <div style="display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid #1a1a2e">
                <span style="font-weight:600">{t['symbol']}</span>
                <span style="color:#888">{t.get('chain','')}</span>
                <span style="color:{k['renk']}">{fmt(t['usd'])}</span>
            </div>"""

        defi_key = "top_defi" if "top_defi" in k else "defi" if "defi" in k else None
        defi_html = ""
        if defi_key and k[defi_key]:
            for d in k[defi_key][:15]:
                defi_html += f"""
                <div style="display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid #1a1a2e;font-size:13px">
                    <span style="font-weight:600;min-width:150px">{d['protocol']}</span>
                    <span style="color:#888;flex:1;padding:0 8px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{d.get('detail','')}</span>
                    <span style="color:{k['renk']};font-weight:600">{fmt(d['usd'])}</span>
                </div>"""

        detail_cards += f"""
        <div style="background:#0d1117;border:2px solid {k['renk']};border-radius:12px;padding:20px;margin:16px 0">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
                <h3 style="color:{k['renk']};margin:0">{k['label']}</h3>
                <span style="font-size:24px;font-weight:700;color:{k['renk']}">{fmt(k['total_usd'])}</span>
            </div>
            <div style="font-size:12px;color:#666;margin-bottom:12px">
                {k['address']}
            </div>
            <div style="margin-bottom:16px">
                <div style="font-weight:600;margin-bottom:6px;color:#ccc">Zincir Dağılımı</div>
                {chains_html}
            </div>
            {"<div style='margin-bottom:16px'><div style=font-weight:600;margin-bottom:6px;color:#ccc>Token Dağılımı</div>" + tokens_html + "</div>" if tokens_html else ""}
            {"<div><div style=font-weight:600;margin-bottom:6px;color:#ccc>DeFi Protokolleri</div>" + defi_html + "</div>" if defi_html else ""}
        </div>"""

    watched_html = ""
    for w in IZLENEN:
        watched_html += f"""
        <div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #1a1a2e">
            <span style="font-weight:600">{w['label']}</span>
            <span style="color:#888">{w['detail']}</span>
            <span style="color:#69f0ae">{fmt(w['usd'])}</span>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>KASA KOMUTA MERKEZİ — MİMAR KALKAN DAMGASI</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#0a0a1a; color:#e0e0e0; font-family:'Segoe UI',system-ui,sans-serif; padding:20px; }}
.header {{ text-align:center; padding:40px 20px; border:3px solid #ffd740; border-radius:16px; margin-bottom:30px; background:linear-gradient(180deg,#0d1117 0%,#0a0a1a 100%); }}
.header h1 {{ font-size:32px; color:#ffd740; letter-spacing:4px; }}
.header .damga {{ font-size:14px; color:#888; margin-top:8px; letter-spacing:2px; }}
.header .total {{ font-size:48px; font-weight:800; color:#00e676; margin:20px 0; }}
.header .mimar {{ color:#ffd740; font-size:16px; font-weight:600; }}
.header .vizyon {{ color:#888; font-style:italic; margin-top:4px; }}
table {{ width:100%; border-collapse:collapse; margin:20px 0; }}
th {{ background:#1a1a2e; padding:10px; text-align:left; color:#ffd740; }}
td {{ padding:8px 10px; border-bottom:1px solid #1a1a2e; }}
tr:hover {{ background:#111122; }}
.section {{ margin:30px 0; }}
.section h2 {{ color:#ffd740; border-bottom:2px solid #ffd740; padding-bottom:8px; margin-bottom:16px; }}
.footer {{ text-align:center; margin-top:40px; padding:30px; border:2px solid #ffd740; border-radius:12px; }}
.footer .stamp {{ font-size:20px; color:#ffd740; font-weight:700; letter-spacing:3px; }}
</style>
</head>
<body>

<div class="header">
    <div class="damga">◆ MİMAR KALKAN DAMGASI ◆</div>
    <h1>KASA KOMUTA MERKEZİ</h1>
    <div class="total">{fmt(GRAND_TOTAL)}</div>
    <div class="mimar">{MIMAR['ad']} — {MIMAR['unvan']}</div>
    <div class="vizyon">"{MIMAR['vizyon']}"</div>
    <div style="color:#666;margin-top:8px">{now}</div>
    <div style="margin-top:12px;color:#888">
        Hedef: {fmt(MIMAR['hedef_usd'])} | İlerleme: {pct(GRAND_TOTAL_WITH_WATCHED, MIMAR['hedef_usd'])}
    </div>
</div>

<div class="section">
    <h2>KASA DAĞILIMI</h2>
    <table>
        <tr><th>#</th><th>Kasa</th><th style="text-align:right">Değer</th><th style="text-align:right">Oran</th></tr>
        {rows}
        <tr style="font-weight:700;border-top:2px solid #ffd740">
            <td></td><td>TOPLAM</td>
            <td style="text-align:right;color:#00e676">{fmt(GRAND_TOTAL)}</td>
            <td style="text-align:right">100.0%</td>
        </tr>
    </table>
</div>

<div class="section">
    <h2>KASA DETAYLARI</h2>
    {detail_cards}
</div>

<div class="section">
    <h2>İZLENEN CÜZDANLAR — {fmt(IZLENEN_TOTAL)}</h2>
    {watched_html}
</div>

<div class="footer">
    <div class="stamp">◆ MİMAR KALKAN DAMGASI ◆</div>
    <div style="margin-top:8px;color:#ccc">{MIMAR['ad']}</div>
    <div style="color:#888">{MIMAR['sistem']}</div>
    <div style="color:#666;margin-top:4px">{now}</div>
    <div style="margin-top:12px;color:#00e676;font-size:18px;font-weight:700">
        GENEL TOPLAM: {fmt(GRAND_TOTAL_WITH_WATCHED)}
    </div>
</div>

</body>
</html>"""
    return html


# ═══════════════════════════════════════════════════════════════
# JSON ÇIKTI
# ═══════════════════════════════════════════════════════════════
def generate_json():
    return json.dumps({
        "damga": "MİMAR KALKAN",
        "mimar": MIMAR,
        "tarih": datetime.datetime.now().isoformat(),
        "grand_total": GRAND_TOTAL,
        "grand_total_with_watched": GRAND_TOTAL_WITH_WATCHED,
        "kasalar": KASALAR,
        "izlenen_cuzdanlar": IZLENEN,
        "izlenen_total": IZLENEN_TOTAL,
    }, indent=2, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    args = sys.argv[1:]

    if "--help" in args or "-h" in args:
        print(__doc__)
        sys.exit(0)

    do_html = "--html" in args or "--all" in args
    do_json = "--json" in args or "--all" in args
    do_terminal = not args or "--terminal" in args or "--all" in args

    if do_terminal:
        print_terminal()

    if do_html:
        html = generate_html()
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kasa_rapor.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\n[HTML] Rapor kaydedildi: {path}")

    if do_json:
        j = generate_json()
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kasa_rapor.json")
        with open(path, "w", encoding="utf-8") as f:
            f.write(j)
        print(f"\n[JSON] Rapor kaydedildi: {path}")

    if not (do_terminal or do_html or do_json):
        print_terminal()
