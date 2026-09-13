"""
Cüzdan İzleme Dashboard'u — FastAPI + Multi-Chain Kasa
Ana Adres: 0x4E83362442B8d1beC281594cea3050c8EB01311C
Kasa: Tüm cüzdanlar ve zincirler genelinde konsolide varlık görünümü
"""

import os
import asyncio
from typing import Optional

import httpx
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI(title="Cüzdan İzleme Dashboard'u")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DEFAULT_WALLET = "0x4E83362442B8d1beC281594cea3050c8EB01311C"
ETHERSCAN_BASE = "https://api.etherscan.io/v2/api"
COINGECKO_BASE = "https://api.coingecko.com/api/v3"
BLOCKSCOUT_BASE = "https://eth.blockscout.com/api/v2"

TRACKED_TOKENS = [
    {
        "symbol": "WBTC",
        "name": "Wrapped BTC",
        "contract": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
        "decimals": 8,
        "coingecko_id": "wrapped-bitcoin",
    },
    {
        "symbol": "renBTC",
        "name": "renBTC",
        "contract": "0xEB4C2781e4ebA804CE9a9803C67d0893436bB27D",
        "decimals": 8,
        "coingecko_id": "renbtc",
    },
    {
        "symbol": "UNI",
        "name": "Uniswap",
        "contract": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
        "decimals": 18,
        "coingecko_id": "uniswap",
    },
    {
        "symbol": "DAI",
        "name": "Dai Stablecoin",
        "contract": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
        "decimals": 18,
        "coingecko_id": "dai",
    },
    {
        "symbol": "LPT",
        "name": "Livepeer",
        "contract": "0x58b6A8A3302369DAEc383334672404Ee733aB239",
        "decimals": 18,
        "coingecko_id": "livepeer",
    },
    {
        "symbol": "stkAAVE",
        "name": "Staked Aave",
        "contract": "0x4da27a545c0c5B758a6BA100e3a049001de870f5",
        "decimals": 18,
        "coingecko_id": "aave",
    },
    {
        "symbol": "ZRX",
        "name": "0x Protocol",
        "contract": "0xE41d2489571d322189246DaFA5ebDe1F4699F498",
        "decimals": 18,
        "coingecko_id": "0x",
    },
    {
        "symbol": "XDATA",
        "name": "Streamr",
        "contract": "0x8f693ca8D21b157107184d29D398A8D082b38b76",
        "decimals": 18,
        "coingecko_id": "streamr",
    },
    {
        "symbol": "BOND",
        "name": "BarnBridge",
        "contract": "0x0391D2021f89DC339F60Fff84546EA23E337750f",
        "decimals": 18,
        "coingecko_id": "barnbridge",
    },
]

FALLBACK_BALANCES = {
    "ETH": 1.0065,
    "WBTC": 0.08005,
    "renBTC": 0.32538,
    "UNI": 283.16,
    "DAI": 2923.0,
    "LPT": 2.26,
    "stkAAVE": 0.0475,
    "ZRX": 6.43,
    "XDATA": 487.6,
    "BOND": 7.92,
}

FALLBACK_PRICES = {
    "ETH": 2317.0,
    "WBTC": 77380.0,
    "renBTC": 17308.0,
    "UNI": 3.27,
    "DAI": 1.0,
    "LPT": 2.14,
    "stkAAVE": 94.87,
    "ZRX": 0.116,
    "XDATA": 0.000843,
    "BOND": 0.0397,
}


def _etherscan_key() -> str:
    return os.environ.get("ETHERSCAN_API_KEY", "")


async def _fetch_eth_balance(client: httpx.AsyncClient, address: str) -> float:
    key = _etherscan_key()
    if key:
        params = {
            "chainid": "1",
            "module": "account",
            "action": "balance",
            "address": address,
            "tag": "latest",
            "apikey": key,
        }
        try:
            resp = await client.get(ETHERSCAN_BASE, params=params, timeout=10)
            data = resp.json()
            if data.get("status") == "1":
                return int(data["result"]) / 1e18
        except Exception:
            pass
    try:
        resp = await client.get(
            f"{BLOCKSCOUT_BASE}/addresses/{address}", timeout=10
        )
        data = resp.json()
        coin_bal = data.get("coin_balance")
        if coin_bal:
            return int(coin_bal) / 1e18
    except Exception:
        pass
    return FALLBACK_BALANCES["ETH"]


async def _fetch_token_balance(
    client: httpx.AsyncClient, address: str, contract: str, decimals: int
) -> Optional[float]:
    key = _etherscan_key()
    if key:
        params = {
            "chainid": "1",
            "module": "account",
            "action": "tokenbalance",
            "contractaddress": contract,
            "address": address,
            "tag": "latest",
            "apikey": key,
        }
        try:
            resp = await client.get(ETHERSCAN_BASE, params=params, timeout=10)
            data = resp.json()
            if data.get("status") == "1":
                return int(data["result"]) / (10**decimals)
        except Exception:
            pass
    return None


async def _fetch_prices(client: httpx.AsyncClient) -> dict[str, float]:
    ids = ",".join(
        ["ethereum"] + [t["coingecko_id"] for t in TRACKED_TOKENS]
    )
    try:
        resp = await client.get(
            f"{COINGECKO_BASE}/simple/price",
            params={"ids": ids, "vs_currencies": "usd"},
            timeout=10,
        )
        data = resp.json()
        prices: dict[str, float] = {}
        eth_price = data.get("ethereum", {}).get("usd")
        if eth_price:
            prices["ETH"] = float(eth_price)
        for token in TRACKED_TOKENS:
            cg = data.get(token["coingecko_id"], {}).get("usd")
            if cg is not None:
                prices[token["symbol"]] = float(cg)
        return prices
    except Exception:
        return {}


@app.get("/api/portfolio")
async def get_portfolio(address: str = Query(default=DEFAULT_WALLET)):
    async with httpx.AsyncClient() as client:
        eth_task = _fetch_eth_balance(client, address)
        price_task = _fetch_prices(client)
        token_tasks = {
            t["symbol"]: _fetch_token_balance(
                client, address, t["contract"], t["decimals"]
            )
            for t in TRACKED_TOKENS
        }

        eth_balance, prices = await asyncio.gather(eth_task, price_task)

        token_results = {}
        for symbol, coro in token_tasks.items():
            token_results[symbol] = await coro

    merged_prices = {**FALLBACK_PRICES, **prices}

    portfolio = []
    portfolio.append(
        {
            "symbol": "ETH",
            "name": "Ethereum",
            "balance": eth_balance,
            "price": merged_prices.get("ETH", 0),
            "value": eth_balance * merged_prices.get("ETH", 0),
        }
    )
    for token in TRACKED_TOKENS:
        sym = token["symbol"]
        bal = token_results.get(sym)
        if bal is None:
            bal = FALLBACK_BALANCES.get(sym, 0)
        price = merged_prices.get(sym, 0)
        portfolio.append(
            {
                "symbol": sym,
                "name": token["name"],
                "balance": bal,
                "price": price,
                "value": bal * price,
            }
        )

    portfolio.sort(key=lambda x: x["value"], reverse=True)
    total = sum(item["value"] for item in portfolio)

    return {
        "address": address,
        "total_usd": round(total, 2),
        "tokens": [
            {
                **item,
                "balance": round(item["balance"], 6),
                "price": round(item["price"], 4),
                "value": round(item["value"], 2),
                "pct": round(item["value"] / total * 100, 2) if total > 0 else 0,
            }
            for item in portfolio
        ],
        "source": "live" if prices else "fallback",
    }


def _parse_blockscout_timestamp(ts_str: str) -> int:
    """Convert ISO timestamp string to unix epoch seconds."""
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        return int(dt.timestamp())
    except Exception:
        return 0


@app.get("/api/history")
async def get_history(address: str = Query(default=DEFAULT_WALLET)):
    """Fetch ETH transactions and ERC-20 token transfers from Blockscout."""
    async with httpx.AsyncClient() as client:
        addr_lower = address.lower()
        tx_url = f"{BLOCKSCOUT_BASE}/addresses/{address}/transactions"
        token_url = f"{BLOCKSCOUT_BASE}/addresses/{address}/token-transfers"

        try:
            eth_resp, token_resp = await asyncio.gather(
                client.get(tx_url, timeout=15),
                client.get(token_url, timeout=15),
            )
            eth_data = eth_resp.json()
            token_data = token_resp.json()
        except Exception:
            return {"address": address, "transactions": [], "error": "API error"}

    transactions = []

    for tx in eth_data.get("items", []):
        value_wei = int(tx.get("value", "0"))
        value_eth = value_wei / 1e18
        from_hash = tx.get("from", {}).get("hash", "") if isinstance(tx.get("from"), dict) else ""
        to_hash = tx.get("to", {}).get("hash", "") if isinstance(tx.get("to"), dict) else ""
        is_incoming = to_hash.lower() == addr_lower
        ts = _parse_blockscout_timestamp(tx.get("timestamp", ""))
        tx_status = tx.get("status", "")
        transactions.append({
            "type": "ETH",
            "symbol": "ETH",
            "hash": tx.get("hash", ""),
            "timestamp": ts,
            "from": from_hash,
            "to": to_hash,
            "value": round(value_eth, 6),
            "direction": "gelen" if is_incoming else "giden",
            "block": tx.get("block_number", 0),
            "method": tx.get("method") or (tx.get("decoded_input", {}) or {}).get("method_call", ""),
            "status": "basarili" if tx_status == "ok" else ("basarisiz" if tx_status == "error" else tx_status),
        })

    for tx in token_data.get("items", []):
        token_info = tx.get("token", {})
        decimals = int(token_info.get("decimals") or 18)
        total_val = tx.get("total", {})
        raw_value = int(total_val.get("value", "0")) if isinstance(total_val, dict) else 0
        value = raw_value / (10**decimals) if decimals > 0 else raw_value
        from_hash = tx.get("from", {}).get("hash", "") if isinstance(tx.get("from"), dict) else ""
        to_hash = tx.get("to", {}).get("hash", "") if isinstance(tx.get("to"), dict) else ""
        is_incoming = to_hash.lower() == addr_lower
        ts = _parse_blockscout_timestamp(tx.get("timestamp", ""))
        transactions.append({
            "type": "TOKEN",
            "symbol": token_info.get("symbol", "?"),
            "token_name": token_info.get("name", ""),
            "contract": token_info.get("address_hash", ""),
            "hash": tx.get("transaction_hash", "") or tx.get("hash", ""),
            "timestamp": ts,
            "from": from_hash,
            "to": to_hash,
            "value": round(value, 6),
            "direction": "gelen" if is_incoming else "giden",
            "block": tx.get("block_number", 0),
            "method": tx.get("method") or "",
        })

    seen_hashes: set[str] = set()
    unique_tx = []
    for tx in transactions:
        key = f"{tx['hash']}_{tx['symbol']}_{tx['direction']}"
        if key not in seen_hashes:
            seen_hashes.add(key)
            unique_tx.append(tx)

    unique_tx.sort(key=lambda x: x["timestamp"], reverse=True)

    return {
        "address": address,
        "total_tx": len(unique_tx),
        "transactions": unique_tx,
    }


KASA_WALLETS = [
    {
        "address": "0x4E83362442B8d1beC281594cea3050c8EB01311C",
        "label": "Ana Cüzdan",
        "chain": "Ethereum",
    },
    {
        "address": "0x65e65Ae6b2C77e4Eb40b8F391AAc222E96Da4258",
        "label": "Ek Cüzdan 1",
        "chain": "Multi",
    },
    {
        "address": "0xE81cBBD77f62509CDe88Aa6Ba1a98Cd8C59C13d9",
        "label": "Ek Cüzdan 2",
        "chain": "Multi",
    },
    {
        "address": "0x232B8637f99056287F07bE0eD24083D56A9f599b",
        "label": "Ek Cüzdan 3",
        "chain": "Multi",
    },
    {
        "address": "0xdDafD55B1d3CF49BcFAF38bF208D44690908d13F",
        "label": "Ek Cüzdan 4",
        "chain": "Multi",
    },
    {
        "address": "0xb0d17E129290FD8149DA3c75593f9596c99105a5",
        "label": "Ek Cüzdan 5",
        "chain": "Multi",
    },
    {
        "address": "0xA9487a4a6A98722d6Cd7d6FF3e59b741a0E87198",
        "label": "Ek Cüzdan 6",
        "chain": "Multi",
    },
    {
        "address": "0x16849c6834BA5b65274b1C9BF8F395e71b795942",
        "label": "Ek Cüzdan 7",
        "chain": "Multi",
    },
    {
        "address": "0xF7bB2ea845b9e56aEf9E364d6Ae05Ea88236ca40",
        "label": "Ek Cüzdan 8",
        "chain": "Multi",
    },
    {
        "address": "0x6a89228055c7c28430692e342f149f37462b478b",
        "label": "SPECTRA Hesabı",
        "chain": "Base",
    },
    {
        "address": "0x54d818277b2b40adfe3ee72e82e6a8fcdd92ae53",
        "label": "xixi",
        "chain": "Multi (27+ zincir)",
    },
    {
        "address": "0x2170ed0880ac9a755fd29b2688956bd959f933f8",
        "label": "Binance-Peg ETH",
        "chain": "BNB Chain + Ethereum",
    },
    {
        "address": "0x4447de210475bfa08e5d42271a73d7624c8a5ac6",
        "label": "Wombat Exchange",
        "chain": "BNB Chain",
    },
    {
        "address": "0x8894e0a0c962cb723c1976a4421c95949be2d4e3",
        "label": "Binance Ana Kasa",
        "chain": "BNB Chain + Ethereum",
    },
    {
        "address": "0x7bfee91193d9df2ac0bfe90191d40f23c773c060",
        "label": "an0n (DeFi Pro)",
        "chain": "HyperEVM + Ethereum + 6 zincir",
    },
    {
        "address": "0xbdfa4f4492dd7b7cf211209c4791af8d52bf5c50",
        "label": "bizyugo.hl",
        "chain": "Hyperliquid + Ethereum + 6 zincir",
    },
]

KASA_MULTICHAIN = {
    "total_usd_value": 27654.14,
    "chains": [
        {"name": "Ethereum", "usd_value": 11937.70},
        {"name": "Arbitrum", "usd_value": 3394.65},
        {"name": "Avalanche", "usd_value": 3251.96},
        {"name": "BSC", "usd_value": 2279.53},
        {"name": "Boba", "usd_value": 2009.38},
        {"name": "Polygon", "usd_value": 1241.13},
        {"name": "OEC", "usd_value": 1051.85},
        {"name": "Moonriver", "usd_value": 996.32},
        {"name": "Optimism", "usd_value": 481.66},
        {"name": "Fantom", "usd_value": 388.45},
        {"name": "xDai", "usd_value": 305.39},
        {"name": "Celo", "usd_value": 162.94},
        {"name": "HECO", "usd_value": 85.54},
        {"name": "Cronos", "usd_value": 67.64},
    ],
}

KASA_DEFI = [
    {
        "protocol": "Alpaca Finance",
        "chain": "BSC",
        "usd_value": 78.60,
        "positions": [{"pool": "WBNB", "balance": "0.1253 WBNB", "usd": 78.60}],
    },
    {
        "protocol": "Venus",
        "chain": "BSC",
        "usd_value": 22.65,
        "positions": [
            {"pool": "ETH (Lending)", "balance": "0.0097 ETH", "usd": 22.65},
            {"pool": "XVS (Reward)", "balance": "0.0008 XVS", "usd": 0.01},
        ],
    },
    {
        "protocol": "PancakeSwap",
        "chain": "BSC",
        "usd_value": 22.18,
        "positions": [
            {"pool": "USDT+WBNB LP", "balance": "11.02 USDT + 0.018 WBNB", "usd": 22.03},
            {"pool": "WBNB+ETHK LP", "balance": "0.0002 WBNB + 1277 ETHK", "usd": 0.15},
        ],
    },
    {
        "protocol": "bDollar",
        "chain": "BSC",
        "usd_value": 6.91,
        "positions": [
            {"pool": "BDO+BUSD Farm", "balance": "438.15 BDO + 6.91 BUSD", "usd": 6.91},
        ],
    },
    {
        "protocol": "Superfluid",
        "chain": "Polygon",
        "usd_value": 0.01,
        "positions": [{"pool": "WPOL", "balance": "0.0042 WPOL", "usd": 0.01}],
    },
    {
        "protocol": "Pendle V2",
        "chain": "Ethereum",
        "usd_value": 372.44,
        "positions": [
            {
                "pool": "ETH+PT-weETH-27JUN2024 LP",
                "balance": "0.0433 ETH + 0.0727 PT-weETH",
                "usd": 269.95,
            },
            {
                "pool": "weETH+PT-weETH-26DEC2024 LP",
                "balance": "0.0017 weETH + 0.0423 PT-weETH",
                "usd": 102.49,
            },
        ],
        "rewards": [
            {"token": "PENDLE", "amount": 0.2199, "usd": 0.30},
        ],
    },
    {
        "protocol": "Aave V3",
        "chain": "Ethereum",
        "usd_value": 253.08,
        "positions": [
            {"pool": "WETH (Supply)", "balance": "0.1086 WETH", "usd": 253.40},
            {"pool": "wstETH (Supply)", "balance": "0.0510 wstETH", "usd": 146.41},
            {"pool": "wstETH (Borrow)", "balance": "-0.0511 wstETH", "usd": -146.73},
        ],
        "health_factor": 2.22,
    },
    {
        "protocol": "Ethena",
        "chain": "Ethereum",
        "usd_value": 122.41,
        "positions": [
            {"pool": "sUSDe (Staked)", "balance": "122.3284 USDe", "usd": 122.27},
            {"pool": "sENA (Staked)", "balance": "1.2932 ENA", "usd": 0.14},
        ],
    },
]

KASA_SPECTRA = {
    "address": "0x6a89228055c7c28430692e342f149f37462b478b",
    "chain": "Base",
    "token": "SPECTRA",
    "protocol": "Spectra",
    "total_usd": 796989,
    "recent_transfers": [
        {"date": "2026-04-27", "direction": "gelen", "amount": 231.79, "usd": 0.89},
        {"date": "2026-04-27", "direction": "gelen", "amount": 47.84, "usd": 0.19},
        {"date": "2026-04-24", "direction": "giden", "amount": 2089.44, "usd": 8.24},
        {"date": "2026-04-23", "direction": "gelen", "amount": 61511.31, "usd": 242.52},
        {"date": "2026-04-23", "direction": "giden", "amount": 5800.00, "usd": 22.87},
        {"date": "2026-04-22", "direction": "giden", "amount": 20000.00, "usd": 78.85},
        {"date": "2026-04-21", "direction": "gelen", "amount": 105228.48, "usd": 469.82},
        {"date": "2026-04-20", "direction": "gelen", "amount": 39062.28, "usd": 176.13},
    ],
}

KASA_WATCHED = [
    {"label": "DeFiWhale", "usd_value": 51900000, "top_tokens": "asBNB 40%, BTCB 15%, slisBNB 14%"},
    {"label": "Ethereum Whale", "usd_value": 37500000, "top_tokens": "WBTC 32%, WHYPE 17%, HYPE 14%"},
    {"label": "0x24c4…37ec", "usd_value": 12200000, "top_tokens": "WBTC 31%, ETH 18%, stETH 10%"},
    {"label": "Gekko", "usd_value": 523700, "top_tokens": "WBTC 30%, VVV 20%, ETH 15%"},
    {"label": "nelsonmandela", "usd_value": 1000000, "top_tokens": "ETH 40%, USDe 8%, BTC.b 6%"},
    {"label": "1559", "usd_value": 1400000, "top_tokens": "ETH 71%, LBTC 23%"},
    {"label": "Nyanpasu", "usd_value": 1300000, "top_tokens": "ETH 45%, USDe 22%, WBTC 11%"},
    {"label": "polka", "usd_value": 2900000, "top_tokens": "ETH 62%, asBNB 17%, USDT 14%"},
    {"label": "sylvinfo", "usd_value": 139000, "top_tokens": "stETH 20%, REALTOKEN 11%, WBTC 11%"},
    {"label": "Enerow", "usd_value": 140100, "top_tokens": "ETH 57%, SPECTRA 16%, RTW 14%"},
    {"label": "AZKCrypto", "usd_value": 10400, "top_tokens": "cbBTC 22%, ETH 18%, BOLD 15%"},
    {"label": "Vibe", "usd_value": 5342, "top_tokens": "USDC 33%, ETH 16%, wstETH 15%"},
    {"label": "tester", "usd_value": 1297, "top_tokens": "ETH 28%, USDC 18%, BNB 12%"},
    {"label": "AlphaCop", "usd_value": 1041, "top_tokens": "ETH 99%"},
]

KASA_XIXI = {
    "address": "0x54d818277b2b40adfe3ee72e82e6a8fcdd92ae53",
    "label": "xixi",
    "total_usd": 8927,
    "wallet_usd": 2163,
    "defi_usd": 6764,
    "chains": [
        {"name": "Linea", "usd_value": 4020},
        {"name": "Base", "usd_value": 2021},
        {"name": "Ethereum", "usd_value": 1080},
        {"name": "Arbitrum", "usd_value": 394},
        {"name": "Mantle", "usd_value": 211},
        {"name": "zkSync Era", "usd_value": 203},
        {"name": "Scroll", "usd_value": 197},
        {"name": "BNB Chain", "usd_value": 139},
        {"name": "DBK Chain", "usd_value": 119},
        {"name": "Blast", "usd_value": 107},
        {"name": "Cyber", "usd_value": 64},
        {"name": "ZetaChain", "usd_value": 43},
        {"name": "Sonic", "usd_value": 32},
        {"name": "SwellChain", "usd_value": 27},
        {"name": "Merlin", "usd_value": 27},
        {"name": "opBNB", "usd_value": 25},
        {"name": "Zora", "usd_value": 21},
        {"name": "Polygon", "usd_value": 21},
        {"name": "OP", "usd_value": 19},
        {"name": "Unichain", "usd_value": 19},
        {"name": "World Chain", "usd_value": 19},
        {"name": "Sei", "usd_value": 16},
        {"name": "Lisk", "usd_value": 15},
        {"name": "Kaia", "usd_value": 13},
        {"name": "Soneium", "usd_value": 12},
        {"name": "Hyperliquid", "usd_value": 12},
        {"name": "Manta Pacific", "usd_value": 10},
    ],
    "top_tokens": [
        {"symbol": "WETH", "amount": 0.2083, "usd": 486.45},
        {"symbol": "ETH", "amount": 0.0651, "usd": 151.97},
        {"symbol": "W", "amount": 9836.42, "usd": 128.97},
        {"symbol": "SolvBTC", "amount": 0.0016, "usd": 124.10},
        {"symbol": "mUSD", "amount": 101.00, "usd": 101.00},
        {"symbol": "TOSHI", "amount": 410941.15, "usd": 77.46},
        {"symbol": "VIRTUAL", "amount": 108.31, "usd": 77.08},
        {"symbol": "wrsETH", "amount": 0.0295, "usd": 73.64},
        {"symbol": "uniBTC", "amount": 0.0007, "usd": 57.56},
        {"symbol": "COMP", "amount": 1.59, "usd": 37.40},
        {"symbol": "ONDO", "amount": 107.98, "usd": 28.82},
    ],
    "defi_protocols": [
        {"protocol": "ZeroLend", "usd": 3470, "detail": "Lending: 1.24 WETH + 0.011 SolvBTC.m + 804 USDC supplied, 0.55 ezETH borrowed"},
        {"protocol": "Silo", "usd": 585, "detail": "Lending: 0.65 ezETH supplied, 0.44 WETH borrowed"},
        {"protocol": "SoSoValue", "usd": 533, "detail": "Staked: 741 MAG7.ssi + 313 SOSO + 62 MEME.ssi"},
        {"protocol": "ether.fi", "usd": 338, "detail": "Yield: 0.115 WETH + 82.6 ETHFI + 9 EIGEN + Staked 0.01 ETH"},
        {"protocol": "Pendle V2", "usd": 373, "detail": "LP: weETH pools ($270 + $103)"},
        {"protocol": "Aave V3 (ETH)", "usd": 253, "detail": "Supply: 0.109 WETH + 0.051 wstETH, Borrow: 0.051 wstETH"},
        {"protocol": "Ethena", "usd": 122, "detail": "Staked: 122.3 USDe + 1.29 ENA"},
        {"protocol": "Stader", "usd": 99, "detail": "Staked: 0.158 BNB (BNBx)"},
        {"protocol": "SyncSwap", "usd": 89, "detail": "LP: USDC+WETH pool"},
        {"protocol": "Karak", "usd": 86, "detail": "Staked: 0.034 mETH"},
        {"protocol": "Radiant Capital V2", "usd": 85, "detail": "Lending: 0.051 weETH supplied, 0.019 WETH borrowed"},
        {"protocol": "Koi", "usd": 81, "detail": "LP: USDC+WETH pool"},
        {"protocol": "Mantle Reward Station", "usd": 70, "detail": "Staked: 110 MNT"},
        {"protocol": "Compound V3", "usd": 94, "detail": "Lending: 0.03 WETH + 12 USDbC supplied"},
        {"protocol": "Cyber", "usd": 54, "detail": "Yield: 100.6 CYBER"},
        {"protocol": "Layer3", "usd": 42, "detail": "Staked: 2284 L3"},
        {"protocol": "ZetaHub", "usd": 40, "detail": "Farming: BNB+WZETA + WZETA+ETH pools"},
        {"protocol": "Ambient", "usd": 32, "detail": "LP: ETH+USDB pool"},
        {"protocol": "EigenLayer", "usd": 28, "detail": "Yield: 138 EIGEN + 332 ALT"},
        {"protocol": "LayerBank", "usd": 24, "detail": "Supply: 24.4 USDC"},
        {"protocol": "GMX", "usd": 24, "detail": "Staked: mixed assets + 1 GMX"},
        {"protocol": "Kinza Finance", "usd": 23, "detail": "Supply: 23 USDC"},
        {"protocol": "Aave V3 (ARB)", "usd": 21, "detail": "Supply: 105 ARB + 0.003 WETH"},
        {"protocol": "Omni Network", "usd": 14, "detail": "Staked: 20.3 OMNI"},
        {"protocol": "NILE", "usd": 13, "detail": "Staked: ZERO+WETH pool"},
        {"protocol": "Silo (2)", "usd": 12, "detail": "Supply: 0.01 PT-weETH, Borrow: 0.005 WETH"},
        {"protocol": "Merchant Moe", "usd": 12, "detail": "LP: WMNT+cmETH + 154 MOE staked"},
        {"protocol": "Hyperliquid", "usd": 12, "detail": "Spot: 11.55 USDC"},
        {"protocol": "Uniswap V3", "usd": 11, "detail": "LP: USDC+USDT0 pool"},
        {"protocol": "MantleETH", "usd": 11, "detail": "Locked: 3597 COOK"},
        {"protocol": "BladeSwap", "usd": 11, "detail": "Farming: USDB+ETH pool"},
        {"protocol": "ICHI", "usd": 10, "detail": "Yield: LYNX+STONE vault"},
        {"protocol": "Alchemix V2", "usd": 10, "detail": "Supply: 10.5 USDC, Borrow: 0.25 alUSD"},
        {"protocol": "Kaia", "usd": 10, "detail": "Staked: 210 KAIA"},
        {"protocol": "Stargate", "usd": 8, "detail": "Locked: 36.6 STG (unlock 2026/03/19)"},
        {"protocol": "ZeroLend (Base)", "usd": 7, "detail": "Supply: 15.3 AERO"},
        {"protocol": "ether.fi (2)", "usd": 7, "detail": "Yield: 16.9 ETHFI"},
    ],
}

KASA_BINANCE_PEG = {
    "address": "0x2170ed0880ac9a755fd29b2688956bd959f933f8",
    "label": "Binance-Peg ETH",
    "total_usd": 72909236,
    "chains": [
        {"name": "BNB Chain", "usd_value": 72363172},
        {"name": "Ethereum", "usd_value": 513180},
    ],
    "top_tokens": [
        {"symbol": "ETH", "chain": "BNB", "amount": 31023.43, "usd": 72217592},
        {"symbol": "ETH", "chain": "ETH", "amount": 216.55, "usd": 504092},
        {"symbol": "BUSD", "chain": "BNB", "amount": 72969.48, "usd": 72953},
        {"symbol": "USDT", "chain": "BNB", "amount": 36527.23, "usd": 36521},
        {"symbol": "BTCB", "chain": "BNB", "amount": 0.2178, "usd": 16795},
        {"symbol": "DOGE", "chain": "BNB", "amount": 81406.39, "usd": 8726},
        {"symbol": "SHIB", "chain": "BNB", "amount": 254397249.67, "usd": 1605},
        {"symbol": "AXS", "chain": "BNB", "amount": 1317.68, "usd": 1913},
    ],
    "defi": [
        {"protocol": "Alpaca Finance", "chain": "BSC", "usd": 79, "detail": "0.1253 WBNB"},
        {"protocol": "Venus", "chain": "BSC", "usd": 23, "detail": "0.0097 ETH lending"},
        {"protocol": "PancakeSwap", "chain": "BSC", "usd": 22, "detail": "USDT+WBNB LP"},
    ],
}

KASA_WOMBAT = {
    "address": "0x4447de210475bfa08e5d42271a73d7624c8a5ac6",
    "label": "Wombat Exchange",
    "total_usd": 1197232,
    "chain": "BNB Chain",
    "tokens": [
        {"symbol": "ETH", "amount": 513.53, "usd": 1197231},
    ],
    "defi": [
        {"protocol": "PancakeSwap", "usd": 0, "detail": "USDT+OSK LP (~$0)"},
    ],
}

KASA_SOLANA = {
    "label": "Solana Cüzdanı",
    "chain": "Solana",
    "total_usd": 6405262,
    "tokens": [
        {"symbol": "SUMMIT", "amount": 576530831689.88, "usd": 4274327},
        {"symbol": "NUTX", "amount": 480000000000000, "usd": 1274306},
        {"symbol": "IBRL", "amount": 743436172.35, "usd": 841630},
        {"symbol": "RNLD", "amount": 111128356.43, "usd": 6749},
        {"symbol": "WSOL", "amount": 51.13, "usd": 4332},
        {"symbol": "USDT", "amount": 1941.98, "usd": 1942},
        {"symbol": "USDC", "amount": 1713.15, "usd": 1713},
        {"symbol": "CR", "amount": 9000000, "usd": 155},
        {"symbol": "GOLDINU", "amount": 177325, "usd": 108},
    ],
    "stats": {
        "total_token_accounts": 5000,
        "sol_balance": 100.45,
        "net_worth_sol": 100.45,
        "net_worth_usd": 8509.17,
    },
    "distribution": {
        "defi": 52.58,
        "stablecoin": 42.95,
        "meme": 1.75,
    },
}

KASA_SPECTRA_TOKEN = {
    "contract": "0x64fc...4e51",
    "chain": "Base",
    "price": 0.01,
    "tvl": 167512.20,
    "followers": 16,
}

KASA_BINANCE_MAIN = {
    "address": "0x8894e0a0c962cb723c1976a4421c95949be2d4e3",
    "label": "Binance Ana Kasa",
    "total_usd": 665608303,
    "chains": [
        {"name": "BNB Chain", "usd_value": 532379293},
        {"name": "Ethereum", "usd_value": 133223347},
    ],
    "top_tokens": [
        {"symbol": "ETH", "chain": "BNB+ETH", "amount": 90271.90, "usd": 210256806},
        {"symbol": "MOODENG", "chain": "BNB", "amount": 2700000000000, "usd": 133217980},
        {"symbol": "BTCB", "chain": "BNB", "amount": 1118.56, "usd": 86278546},
        {"symbol": "BNB", "chain": "BNB", "amount": 118214, "usd": 74049251},
        {"symbol": "USD1", "chain": "BNB", "amount": 54157263, "usd": 54179672},
        {"symbol": "XUSD", "chain": "BNB", "amount": 25436976, "usd": 25431889},
        {"symbol": "币安人生", "chain": "BNB", "amount": 31476023, "usd": 11835134},
        {"symbol": "OPN", "chain": "BNB", "amount": 57981327, "usd": 10007577},
        {"symbol": "NIGHT", "chain": "BNB", "amount": 273423011, "usd": 9300730},
        {"symbol": "$BANANA", "chain": "BNB", "amount": 958028629, "usd": 9126014},
        {"symbol": "XRP", "chain": "BNB", "amount": 2675198, "usd": 3735111},
        {"symbol": "KGST", "chain": "BNB", "amount": 284567410, "usd": 3258297},
        {"symbol": "IOTA", "chain": "BNB", "amount": 56618128, "usd": 3232895},
        {"symbol": "ZEC", "chain": "BNB", "amount": 8028.48, "usd": 2681914},
        {"symbol": "SAHARA", "chain": "BNB", "amount": 107479420, "usd": 2433334},
    ],
    "defi": [
        {"protocol": "PancakeSwap", "chain": "BSC", "usd": 3563, "detail": "35 LP havuzu"},
        {"protocol": "Solv", "chain": "BSC", "usd": 345, "detail": "SolvBTC yield"},
        {"protocol": "Venus", "chain": "BSC", "usd": 161, "detail": "XVS+BNB+USDC lending"},
        {"protocol": "BounceBit", "chain": "BSC", "usd": 8, "detail": "BTCB staking"},
        {"protocol": "Lista DAO", "chain": "BSC", "usd": 7, "detail": "slisBNB staking"},
    ],
    "stats": {
        "age_days": 1787,
        "tvf": 3800000,
        "followers": 537,
        "total_tokens": 150,
    },
}

KASA_ANON = {
    "address": "0x7bfee91193d9df2ac0bfe90191d40f23c773c060",
    "label": "an0n (DeFi Pro)",
    "total_usd": 25547225,
    "chains": [
        {"name": "HyperEVM", "usd_value": 19138042},
        {"name": "Ethereum", "usd_value": 4477033},
        {"name": "Hyperliquid", "usd_value": 896934},
        {"name": "Berachain", "usd_value": 597741},
        {"name": "BNB Chain", "usd_value": 142223},
        {"name": "Linea", "usd_value": 89069},
        {"name": "Base", "usd_value": 84188},
        {"name": "Fraxtal", "usd_value": 34073},
    ],
    "top_tokens": [
        {"symbol": "HYPE", "chain": "HyperEVM", "amount": 106003.75, "usd": 4300890},
        {"symbol": "WBTC", "chain": "ETH", "amount": 1.29, "usd": 99538},
        {"symbol": "HPL", "chain": "HyperEVM", "amount": 2672660, "usd": 39298},
        {"symbol": "ZRO", "chain": "Multi", "amount": 21815, "usd": 32396},
        {"symbol": "REX", "chain": "HyperEVM", "amount": 1909721, "usd": 26750},
    ],
    "top_defi": [
        {"protocol": "Kinetiq", "usd": 9577537, "detail": "vkHYPE+kHYPE staking"},
        {"protocol": "ether.fi", "usd": 1757648, "detail": "weETH+liquidETH+BTC"},
        {"protocol": "HyperLend", "usd": 1570900, "detail": "USD₮0+USDC lending"},
        {"protocol": "Hyperbeat", "usd": 1364577, "detail": "yield vaults"},
        {"protocol": "Hyperliquid", "usd": 896934, "detail": "vaults+delegated"},
        {"protocol": "Pendle V2", "usd": 875045, "detail": "PT-vkHYPE"},
        {"protocol": "D2.finance", "usd": 700443, "detail": "d2HYPE yield"},
        {"protocol": "Kelp DAO", "usd": 602294, "detail": "ETH yield"},
        {"protocol": "Dolomite", "usd": 456885, "detail": "WBERA lending"},
        {"protocol": "Origami Finance", "usd": 363337, "detail": "gOHM leveraged"},
        {"protocol": "Lombard", "usd": 313013, "detail": "LBTCv yield"},
        {"protocol": "IPOR", "usd": 283199, "detail": "stETH looping"},
        {"protocol": "LIDO", "usd": 195426, "detail": "wstETH staked"},
        {"protocol": "Morpho", "usd": 152794, "detail": "USDT0 vaults"},
        {"protocol": "Beefy", "usd": 147469, "detail": "LP farming"},
    ],
    "stats": {
        "age_days": 2911,
        "tvf": 1500000000,
        "followers": 74600,
        "total_protocols": 100,
    },
}

KASA_BIZYUGO = {
    "address": "0xbdfa4f4492dd7b7cf211209c4791af8d52bf5c50",
    "label": "bizyugo.hl",
    "total_usd": 79715717,
    "chains": [
        {"name": "Hyperliquid", "usd_value": 42226180},
        {"name": "Ethereum", "usd_value": 24299868},
        {"name": "HyperEVM", "usd_value": 12205338},
        {"name": "Arbitrum", "usd_value": 674638},
        {"name": "Ink", "usd_value": 92309},
        {"name": "Avalanche", "usd_value": 87517},
    ],
    "top_tokens": [
        {"symbol": "HYPE", "chain": "Hyperliquid", "amount": 1005065, "usd": 40711666},
        {"symbol": "HYPE", "chain": "Wallet", "amount": 129392, "usd": 5242969},
        {"symbol": "sUSDat", "chain": "ETH", "amount": 299702, "usd": 299593},
        {"symbol": "WHYPE", "chain": "HyperEVM", "amount": 5000, "usd": 202600},
        {"symbol": "ETH", "chain": "ETH", "amount": 56.94, "usd": 132939},
        {"symbol": "USDC", "chain": "Multi", "amount": 104525, "usd": 104536},
    ],
    "top_defi": [
        {"protocol": "Hyperliquid", "usd": 42226180, "detail": "1M+ HYPE delegated+vaults+perps"},
        {"protocol": "Aave V3", "usd": 17274881, "detail": "236 WBTC+44 LBTC+713 wstETH"},
        {"protocol": "Morpho", "usd": 7600313, "detail": "Felix HYPE+USDH+vaults"},
        {"protocol": "Upshift", "usd": 4000400, "detail": "fUSDnr $4M"},
        {"protocol": "GMX V2", "usd": 444739, "detail": "perps+LP"},
        {"protocol": "Pendle V2", "usd": 364542, "detail": "PT-apxUSD+PENDLE locked"},
        {"protocol": "Uniswap V3", "usd": 309521, "detail": "PAXG+XAUt LP"},
        {"protocol": "Kinetiq", "usd": 273090, "detail": "KNTQ staked"},
        {"protocol": "Hyperbeat", "usd": 235812, "detail": "Ultra uBTC"},
        {"protocol": "Tensorplex", "usd": 157702, "detail": "stTAO"},
        {"protocol": "Boros", "usd": 146892, "detail": "USD₮0+WBTC"},
        {"protocol": "Fluid", "usd": 98381, "detail": "sUSDai+USDC lending"},
        {"protocol": "Velodrome V3", "usd": 92078, "detail": "USD₮0+USDG farming"},
        {"protocol": "Yield Basis", "usd": 76657, "detail": "yb-tBTC"},
        {"protocol": "Gearbox", "usd": 51713, "detail": "EDGE UltraYield USDC"},
    ],
    "stats": {
        "age_days": 1853,
        "tvf": 1500000000,
        "followers": 83000,
        "total_protocols": 40,
    },
}


def _build_kasa_access_summary(
    multichain_total: float,
    defi_total: float,
    spectra_total: float,
    watched_total: float,
    binance_peg_total: float,
    wombat_total: float,
    solana_total: float,
    binance_main_total: float,
    anon_total: float,
    bizyugo_total: float,
) -> dict:
    xixi_wallet_total = KASA_XIXI["wallet_usd"]
    xixi_defi_total = KASA_XIXI["defi_usd"]
    wallet_transferable = multichain_total + spectra_total + xixi_wallet_total
    defi_requires_action = defi_total + xixi_defi_total
    actionable_total = wallet_transferable + defi_requires_action
    watch_only_total = (
        watched_total + binance_peg_total + wombat_total + solana_total
        + binance_main_total + anon_total + bizyugo_total
    )

    return {
        "is_read_only_dashboard": True,
        "wallet_transferable_total": round(wallet_transferable, 2),
        "defi_requires_action_total": round(defi_requires_action, 2),
        "owned_or_actionable_total": round(actionable_total, 2),
        "watch_only_total": round(watch_only_total, 2),
        "not_withdrawable_reasons": [
            "Bu panel sadece izleme/raporlama yapıyor; işlem imzalama, transfer veya withdraw API'si yok.",
            "Binance Ana Kasa, Binance-Peg, Wombat, Solana, an0n, bizyugo ve takip listesi adresleri cüzdan kontrolü kanıtlamaz; imza yetkisi yoksa çekilemez.",
            "Lending/staking/LP pozisyonlarında önce borç kapatma, unlock/unstake/claim ve her zincirde gas gerekir.",
            "Kilitli pozisyonlar süre dolmadan, borçlu pozisyonlar borç kapanmadan çekilemez.",
        ],
        "buckets": [
            {
                "label": "Cüzdandan direkt transfer edilebilir",
                "value": round(wallet_transferable, 2),
                "detail": "Ana/multi-chain cüzdan + SPECTRA + xixi wallet bakiyesi; signer ve gas gerekir.",
                "status": "wallet_signature_required",
            },
            {
                "label": "Önce DeFi/stake çözülmeli",
                "value": round(defi_requires_action, 2),
                "detail": "Borç kapat, withdraw/unstake/claim yap, sonra hedef cüzdana gönder.",
                "status": "protocol_action_required",
            },
            {
                "label": "Sadece izlenen/harici görünen varlık",
                "value": round(watch_only_total, 2),
                "detail": "Dashboard toplamında görünür ama bu repo üzerinden çekilemez.",
                "status": "watch_only",
            },
        ],
    }


@app.get("/api/kasa")
async def get_kasa():
    """Consolidated vault view across all wallets and chains."""
    multichain_total = KASA_MULTICHAIN["total_usd_value"]
    defi_total = sum(d["usd_value"] for d in KASA_DEFI)
    spectra_total = KASA_SPECTRA["total_usd"]
    watched_total = sum(w["usd_value"] for w in KASA_WATCHED)
    xixi_total = KASA_XIXI["total_usd"]
    binance_peg_total = KASA_BINANCE_PEG["total_usd"]
    wombat_total = KASA_WOMBAT["total_usd"]
    solana_total = KASA_SOLANA["total_usd"]
    binance_main_total = KASA_BINANCE_MAIN["total_usd"]
    anon_total = KASA_ANON["total_usd"]
    bizyugo_total = KASA_BIZYUGO["total_usd"]

    grand = (
        multichain_total + defi_total + spectra_total + watched_total
        + xixi_total + binance_peg_total + wombat_total + solana_total
        + binance_main_total + anon_total + bizyugo_total
    )
    access = _build_kasa_access_summary(
        multichain_total,
        defi_total,
        spectra_total,
        watched_total,
        binance_peg_total,
        wombat_total,
        solana_total,
        binance_main_total,
        anon_total,
        bizyugo_total,
    )

    return {
        "wallets": KASA_WALLETS,
        "multichain": KASA_MULTICHAIN,
        "defi_positions": KASA_DEFI,
        "spectra": KASA_SPECTRA,
        "spectra_token": KASA_SPECTRA_TOKEN,
        "watched_wallets": KASA_WATCHED,
        "xixi": KASA_XIXI,
        "binance_peg": KASA_BINANCE_PEG,
        "wombat": KASA_WOMBAT,
        "solana": KASA_SOLANA,
        "binance_main": KASA_BINANCE_MAIN,
        "anon": KASA_ANON,
        "bizyugo": KASA_BIZYUGO,
        "access": access,
        "summary": {
            "multichain_total": round(multichain_total, 2),
            "defi_total": round(defi_total, 2),
            "spectra_total": round(spectra_total, 2),
            "watched_total": round(watched_total, 2),
            "xixi_total": round(xixi_total, 2),
            "binance_peg_total": round(binance_peg_total, 2),
            "wombat_total": round(wombat_total, 2),
            "solana_total": round(solana_total, 2),
            "binance_main_total": round(binance_main_total, 2),
            "anon_total": round(anon_total, 2),
            "bizyugo_total": round(bizyugo_total, 2),
            "owned_or_actionable_total": access["owned_or_actionable_total"],
            "watch_only_total": access["watch_only_total"],
            "wallet_transferable_total": access["wallet_transferable_total"],
            "defi_requires_action_total": access["defi_requires_action_total"],
            "grand_total": round(grand, 2),
        },
    }


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    return DASHBOARD_HTML


DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Cüzdan İzleme Dashboard'u</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#0a1a0a;--card:#112211;--accent:#00e676;--accent2:#69f0ae;
  --text:#e0f0e0;--text-dim:#88aa88;--green:#00e676;--red:#ff5252;
  --border:#1a3a1a;
}
body{font-family:'Inter','Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--text);min-height:100vh}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}

.header{
  background:linear-gradient(135deg,#0d1f0d 0%,#1a3a1a 100%);
  border-bottom:1px solid var(--border);padding:20px 32px;
  display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;
}
.header h1{font-size:22px;background:linear-gradient(90deg,#00e676,#69f0ae);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent}
.header .addr{font-size:13px;color:var(--text-dim);font-family:monospace}
.header .badge{font-size:11px;padding:3px 10px;border-radius:20px;
  background:rgba(0,210,255,.15);color:var(--accent)}

.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));
  gap:16px;padding:24px 32px}
.card{background:var(--card);border:1px solid var(--border);border-radius:14px;
  padding:24px;transition:transform .15s}
.card:hover{transform:translateY(-2px)}
.card .label{font-size:12px;color:var(--text-dim);text-transform:uppercase;letter-spacing:1px;margin-bottom:8px}
.card .big{font-size:32px;font-weight:700}
.card .sub{font-size:13px;color:var(--text-dim);margin-top:4px}

.main-grid{display:grid;grid-template-columns:1fr 380px;gap:16px;padding:0 32px 32px;min-height:400px}
@media(max-width:900px){.main-grid{grid-template-columns:1fr}}

.table-wrap{background:var(--card);border:1px solid var(--border);border-radius:14px;overflow:hidden}
.table-wrap h3{padding:18px 20px;border-bottom:1px solid var(--border);font-size:15px}
table{width:100%;border-collapse:collapse}
th,td{padding:12px 20px;text-align:left;font-size:14px}
th{color:var(--text-dim);font-weight:500;font-size:12px;text-transform:uppercase;letter-spacing:.5px;
  border-bottom:1px solid var(--border)}
tr:hover{background:rgba(0,230,118,.06)}
td:last-child{text-align:right}
th:last-child{text-align:right}
.token-icon{width:28px;height:28px;border-radius:50%;background:var(--border);
  display:inline-flex;align-items:center;justify-content:center;font-size:11px;
  font-weight:700;margin-right:10px;vertical-align:middle}
.pct-bar{height:4px;border-radius:2px;background:var(--border);margin-top:4px;max-width:120px}
.pct-fill{height:100%;border-radius:2px;background:linear-gradient(90deg,#00e676,#69f0ae)}

.chart-wrap{background:var(--card);border:1px solid var(--border);border-radius:14px;
  padding:20px;display:flex;flex-direction:column;align-items:center}
.chart-wrap h3{margin-bottom:16px;font-size:15px;align-self:flex-start}
.chart-container{position:relative;width:100%;max-width:320px;aspect-ratio:1}

.footer{text-align:center;padding:20px;color:var(--text-dim);font-size:12px;border-top:1px solid var(--border)}
.spinner{display:inline-block;width:20px;height:20px;border:2px solid var(--border);
  border-top-color:var(--accent);border-radius:50%;animation:spin .6s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.refresh-btn{background:none;border:1px solid var(--border);color:var(--accent);
  padding:6px 16px;border-radius:8px;cursor:pointer;font-size:13px;transition:all .2s}
.refresh-btn:hover{background:rgba(0,230,118,.15);border-color:var(--accent)}
.loading-overlay{position:fixed;inset:0;background:var(--bg);display:flex;
  align-items:center;justify-content:center;flex-direction:column;gap:16px;z-index:100}
.loading-overlay .spinner{width:40px;height:40px;border-width:3px}

.tabs{display:flex;gap:0;padding:0 32px;margin-top:8px;overflow-x:auto}
.tab-btn{background:none;border:none;color:var(--text-dim);padding:12px 24px;
  font-size:14px;cursor:pointer;border-bottom:2px solid transparent;transition:all .2s;font-weight:500;white-space:nowrap}
.tab-btn:hover{color:var(--text)}
.tab-btn.active{color:var(--accent);border-bottom-color:var(--accent)}
.tab-content{display:none}
.tab-content.active{display:block}

.kasa-section{padding:0 32px 32px}
.kasa-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;margin-bottom:24px}
.kasa-card{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:20px}
.kasa-card .k-label{font-size:11px;color:var(--text-dim);text-transform:uppercase;letter-spacing:1px;margin-bottom:6px}
.kasa-card .k-big{font-size:28px;font-weight:700}
.kasa-card .k-sub{font-size:12px;color:var(--text-dim);margin-top:4px}
.chain-bar{display:flex;align-items:center;gap:8px;padding:6px 0;border-bottom:1px solid var(--border)}
.chain-bar:last-child{border-bottom:none}
.chain-name{min-width:90px;font-size:13px}
.chain-fill{height:6px;border-radius:3px;transition:width .3s}
.chain-val{font-size:12px;color:var(--text-dim);min-width:80px;text-align:right}
.defi-row{display:flex;align-items:center;justify-content:space-between;padding:10px 0;border-bottom:1px solid var(--border)}
.defi-row:last-child{border-bottom:none}
.defi-proto{font-weight:600;font-size:14px}
.defi-chain{font-size:11px;color:var(--text-dim);margin-left:8px}
.defi-val{font-weight:600;color:var(--accent)}
.watched-row{display:flex;align-items:center;justify-content:space-between;padding:8px 0;border-bottom:1px solid var(--border);font-size:13px}
.watched-row:last-child{border-bottom:none}
.watched-label{font-weight:600;min-width:120px}
.watched-val{color:var(--accent);font-weight:600;min-width:100px;text-align:right}
.watched-tokens{color:var(--text-dim);font-size:11px;flex:1;text-align:right;margin-right:12px}
.spectra-card{background:linear-gradient(135deg,#1a1a2e,#2a1a3e);border:1px solid #7b2ff7;border-radius:14px;padding:20px;margin-bottom:16px}
.spectra-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}
.spectra-title{font-size:16px;font-weight:700;color:#ea80fc}
.spectra-val{font-size:24px;font-weight:700}
.access-card{background:linear-gradient(135deg,#2a1608,#1f1208);border:2px solid #ff9100;border-radius:14px;padding:20px;margin-bottom:16px}
.access-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin-top:14px}
.access-bucket{background:rgba(255,145,0,.08);border:1px solid rgba(255,145,0,.24);border-radius:12px;padding:14px}
.access-bucket .bucket-label{font-size:12px;color:#ffcc80;text-transform:uppercase;letter-spacing:.6px;margin-bottom:6px}
.access-bucket .bucket-value{font-size:24px;font-weight:700;color:#ffb74d}
.access-bucket .bucket-detail{font-size:12px;color:var(--text-dim);line-height:1.5;margin-top:6px}
.reason-list{margin:12px 0 0 18px;color:#ffcc80;font-size:13px;line-height:1.7}

.history-section{padding:0 32px 32px}
.history-table{background:var(--card);border:1px solid var(--border);border-radius:14px;overflow:hidden}
.history-table h3{padding:18px 20px;border-bottom:1px solid var(--border);font-size:15px;
  display:flex;align-items:center;justify-content:space-between}
.history-table h3 span{font-size:12px;color:var(--text-dim);font-weight:400}
.dir-in{color:var(--green);font-weight:600}
.dir-out{color:var(--red);font-weight:600}
.tx-hash{font-family:monospace;font-size:12px;color:var(--accent)}
.tx-addr{font-family:monospace;font-size:11px;color:var(--text-dim)}
.tx-time{font-size:12px;color:var(--text-dim)}
.tx-badge{font-size:10px;padding:2px 8px;border-radius:10px;font-weight:600;text-transform:uppercase}
.tx-badge.eth{background:rgba(0,210,255,.15);color:var(--accent)}
.tx-badge.token{background:rgba(123,47,247,.15);color:var(--accent2)}
.filter-bar{display:flex;gap:8px;padding:12px 20px;border-bottom:1px solid var(--border);flex-wrap:wrap}
.filter-btn{background:none;border:1px solid var(--border);color:var(--text-dim);
  padding:4px 12px;border-radius:6px;cursor:pointer;font-size:12px;transition:all .2s}
.filter-btn:hover,.filter-btn.active{background:rgba(0,210,255,.1);border-color:var(--accent);color:var(--accent)}
</style>
</head>
<body>

<div class="loading-overlay" id="loader">
  <div class="spinner"></div>
  <div style="color:var(--text-dim)">Cüzdan verileri yükleniyor…</div>
</div>

<header class="header">
  <div>
    <h1>KASA KOMUTA MERKEZİ</h1>
    <div class="addr" id="walletAddr">—</div>
  </div>
  <div style="display:flex;gap:10px;align-items:center">
    <span class="badge" id="sourceLabel">—</span>
    <button class="refresh-btn" onclick="loadData()">Yenile</button>
  </div>
</header>

<div class="tabs">
  <button class="tab-btn active" onclick="switchTab('kasa')">Kasa Özeti</button>
  <button class="tab-btn" onclick="switchTab('portfolio')">Portföy</button>
  <button class="tab-btn" onclick="switchTab('guide')">Transfer Rehberi</button>
  <button class="tab-btn" onclick="switchTab('history')">İşlem Geçmişi</button>
</div>

<div id="tab-kasa" class="tab-content active">
  <div class="grid">
    <div class="card" style="border:2px solid #00e676;background:linear-gradient(135deg,#0d1f0d,#1a3a1a)">
      <div class="label" style="color:#00e676;font-size:13px">Toplam Kasa Değeri</div>
      <div class="big" id="kasaTotal" style="color:#00e676">—</div>
      <div class="sub" id="kasaSub">Yükleniyor…</div>
    </div>
    <div class="card" style="border:1px solid #ffd740">
      <div class="label" style="color:#ffd740">Binance Ana Kasa</div>
      <div class="big" id="kasaBinanceMain" style="color:#ffd740">—</div>
      <div class="sub">BNB Chain + Ethereum — 150+ token</div>
    </div>
    <div class="card" style="border:1px solid #448aff">
      <div class="label" style="color:#448aff">bizyugo.hl</div>
      <div class="big" id="kasaBizyugo" style="color:#448aff">—</div>
      <div class="sub">Hyperliquid + Ethereum — 40+ protokol</div>
    </div>
    <div class="card">
      <div class="label">Binance-Peg ETH</div>
      <div class="big" id="kasaBinance">—</div>
      <div class="sub">BNB Chain + Ethereum</div>
    </div>
  </div>
  <div class="grid" style="margin-top:0">
    <div class="card" style="border:1px solid #ffab40">
      <div class="label" style="color:#ffab40">an0n (DeFi Pro)</div>
      <div class="big" id="kasaAnon" style="color:#ffab40">—</div>
      <div class="sub">HyperEVM + 8 zincir — 100+ protokol</div>
    </div>
    <div class="card">
      <div class="label">Solana Cüzdanı</div>
      <div class="big" id="kasaSolana">—</div>
      <div class="sub">SUMMIT, NUTX, IBRL + 5K token</div>
    </div>
    <div class="card">
      <div class="label">Wombat Exchange</div>
      <div class="big" id="kasaWombat">—</div>
      <div class="sub">BNB Chain — 513 ETH</div>
    </div>
    <div class="card">
      <div class="label">SPECTRA Hesabı</div>
      <div class="big" id="kasaSpectra">—</div>
      <div class="sub">Base zinciri</div>
    </div>
    <div class="card">
      <div class="label">Multi-Chain Varlıklar</div>
      <div class="big" id="kasaMultichain">—</div>
      <div class="sub">14 zincir genelinde</div>
    </div>
    <div class="card">
      <div class="label">xixi Hesabı</div>
      <div class="big" id="kasaXixi">—</div>
      <div class="sub">27+ zincir, 40+ DeFi</div>
    </div>
    <div class="card">
      <div class="label">DeFi Pozisyonları</div>
      <div class="big" id="kasaDefi">—</div>
      <div class="sub">Ana cüzdan protokolleri</div>
    </div>
  </div>

  <div class="kasa-section">
    <div class="access-card">
      <div style="display:flex;justify-content:space-between;gap:16px;align-items:flex-start;flex-wrap:wrap">
        <div>
          <div style="font-size:18px;font-weight:700;color:#ffb74d">Çekilebilirlik Kontrolü</div>
          <div style="font-size:13px;color:#ffcc80;margin-top:4px">
            Bu dashboard izleme modundadır; zincir üstü işlem imzalamaz.
          </div>
        </div>
        <div style="text-align:right">
          <div style="font-size:11px;color:var(--text-dim);text-transform:uppercase;letter-spacing:1px">Aksiyon alınabilir toplam</div>
          <div class="big" id="ownedActionableTotal" style="font-size:26px;color:#ffb74d">—</div>
        </div>
      </div>
      <div class="access-grid" id="accessBuckets">
        <div class="access-bucket"><div class="bucket-detail">Yükleniyor…</div></div>
      </div>
      <ul class="reason-list" id="notWithdrawableReasons"></ul>
    </div>

    <div class="spectra-card">
      <div class="spectra-header">
        <div class="spectra-title">SPECTRA — Spectra Protocol (Base)</div>
        <div class="spectra-val" id="spectraVal">—</div>
      </div>
      <div id="spectraTransfers" style="font-size:12px;color:var(--text-dim)">Yükleniyor…</div>
    </div>

    <div class="kasa-card" style="margin-bottom:16px;background:linear-gradient(135deg,#2e2e0d,#3e3a0d);border:2px solid #ffd740">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
        <div style="font-size:18px;font-weight:700;color:#ffd740">Binance Ana Kasa — $665.6M</div>
        <div class="big" id="binanceMainVal" style="font-size:22px;color:#ffd740">—</div>
      </div>
      <div style="display:flex;gap:12px;margin-bottom:8px">
        <span style="background:rgba(255,215,64,.15);border:1px solid rgba(255,215,64,.3);border-radius:6px;padding:2px 8px;font-size:11px;color:#ffd740">BNB Chain: $532.4M</span>
        <span style="background:rgba(255,215,64,.15);border:1px solid rgba(255,215,64,.3);border-radius:6px;padding:2px 8px;font-size:11px;color:#ffd740">Ethereum: $133.2M</span>
        <span style="background:rgba(255,215,64,.15);border:1px solid rgba(255,215,64,.3);border-radius:6px;padding:2px 8px;font-size:11px;color:#ffd740">150+ Token</span>
      </div>
      <div id="binanceMainTokens" style="font-size:12px">Yükleniyor…</div>
      <div id="binanceMainDefi" style="font-size:12px;margin-top:8px">Yükleniyor…</div>
    </div>

    <div class="kasa-card" style="margin-bottom:16px;background:linear-gradient(135deg,#0d1a2e,#1a2a3e);border:2px solid #448aff">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
        <div style="font-size:18px;font-weight:700;color:#448aff">bizyugo.hl — $79.7M</div>
        <div class="big" id="bizyugoVal" style="font-size:22px;color:#448aff">—</div>
      </div>
      <div style="display:flex;gap:12px;margin-bottom:8px;flex-wrap:wrap">
        <span style="background:rgba(68,138,255,.15);border:1px solid rgba(68,138,255,.3);border-radius:6px;padding:2px 8px;font-size:11px;color:#448aff">Hyperliquid: $42.2M</span>
        <span style="background:rgba(68,138,255,.15);border:1px solid rgba(68,138,255,.3);border-radius:6px;padding:2px 8px;font-size:11px;color:#448aff">Ethereum: $24.3M</span>
        <span style="background:rgba(68,138,255,.15);border:1px solid rgba(68,138,255,.3);border-radius:6px;padding:2px 8px;font-size:11px;color:#448aff">HyperEVM: $12.2M</span>
        <span style="background:rgba(68,138,255,.15);border:1px solid rgba(68,138,255,.3);border-radius:6px;padding:2px 8px;font-size:11px;color:#448aff">40+ Protokol</span>
      </div>
      <div id="bizyugoDefi" style="font-size:12px">Yükleniyor…</div>
    </div>

    <div class="kasa-card" style="margin-bottom:16px;background:linear-gradient(135deg,#2e1f0d,#3e2a0d);border:2px solid #ffab40">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
        <div style="font-size:18px;font-weight:700;color:#ffab40">an0n (DeFi Pro) — $25.5M</div>
        <div class="big" id="anonVal" style="font-size:22px;color:#ffab40">—</div>
      </div>
      <div style="display:flex;gap:12px;margin-bottom:8px;flex-wrap:wrap">
        <span style="background:rgba(255,171,64,.15);border:1px solid rgba(255,171,64,.3);border-radius:6px;padding:2px 8px;font-size:11px;color:#ffab40">HyperEVM: $19.1M</span>
        <span style="background:rgba(255,171,64,.15);border:1px solid rgba(255,171,64,.3);border-radius:6px;padding:2px 8px;font-size:11px;color:#ffab40">Ethereum: $4.5M</span>
        <span style="background:rgba(255,171,64,.15);border:1px solid rgba(255,171,64,.3);border-radius:6px;padding:2px 8px;font-size:11px;color:#ffab40">Hyperliquid: $897K</span>
        <span style="background:rgba(255,171,64,.15);border:1px solid rgba(255,171,64,.3);border-radius:6px;padding:2px 8px;font-size:11px;color:#ffab40">100+ Protokol</span>
      </div>
      <div id="anonDefi" style="font-size:12px">Yükleniyor…</div>
    </div>

    <div class="kasa-card" style="margin-bottom:16px;background:linear-gradient(135deg,#1a2e1a,#2a3e1a);border:1px solid #00e676">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
        <div style="font-size:16px;font-weight:700;color:#69f0ae">Solana Cüzdanı</div>
        <div class="big" id="solanaVal" style="font-size:20px">—</div>
      </div>
      <div id="solanaTokens" style="font-size:12px">Yükleniyor…</div>
    </div>

    <div class="kasa-card" style="margin-bottom:16px;background:linear-gradient(135deg,#2e2a1a,#3e2a1a);border:1px solid #ff9100">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
        <div style="font-size:16px;font-weight:700;color:#ffab40">Binance-Peg ETH — $72.8M</div>
        <div class="big" id="binanceVal" style="font-size:20px">—</div>
      </div>
      <div id="binanceTokens" style="font-size:12px">Yükleniyor…</div>
    </div>

    <div class="kasa-card" style="margin-bottom:16px;background:linear-gradient(135deg,#1a1a2e,#1a2e2e);border:1px solid #00d2ff">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
        <div style="font-size:16px;font-weight:700;color:#00d2ff">xixi — 40+ DeFi Protokolü</div>
        <div class="big" id="xixiVal" style="font-size:20px">—</div>
      </div>
      <div id="xixiChains" style="font-size:12px;margin-bottom:8px">Yükleniyor…</div>
      <div id="xixiDefi" style="font-size:12px">Yükleniyor…</div>
    </div>

    <div class="kasa-grid">
      <div class="kasa-card">
        <div class="k-label">Zincir Dağılımı (Ana Cüzdan)</div>
        <div id="chainBars" style="margin-top:8px">Yükleniyor…</div>
      </div>
      <div class="kasa-card">
        <div class="k-label">DeFi Pozisyonları (Ana Cüzdan)</div>
        <div id="defiList" style="margin-top:8px">Yükleniyor…</div>
      </div>
    </div>

    <div class="kasa-card" style="margin-bottom:24px">
      <div class="k-label">Kayıtlı Cüzdanlar</div>
      <div id="walletList" style="margin-top:8px">Yükleniyor…</div>
    </div>

    <div class="kasa-card">
      <div class="k-label">Takip Edilen Cüzdanlar</div>
      <div id="watchedList" style="margin-top:8px">Yükleniyor…</div>
    </div>
  </div>
</div>

<div id="tab-portfolio" class="tab-content">
  <div class="grid">
    <div class="card">
      <div class="label">Toplam Portföy Değeri</div>
      <div class="big" id="totalValue">—</div>
      <div class="sub" id="tokenCount">—</div>
    </div>
    <div class="card">
      <div class="label">BTC Pozisyonları (WBTC + renBTC)</div>
      <div class="big" id="btcValue">—</div>
      <div class="sub" id="btcDetail">—</div>
    </div>
    <div class="card">
      <div class="label">Nakit Benzeri (ETH + DAI)</div>
      <div class="big" id="cashValue">—</div>
      <div class="sub" id="cashDetail">—</div>
    </div>
    <div class="card">
      <div class="label">Diğer Tokenlar</div>
      <div class="big" id="otherValue">—</div>
      <div class="sub" id="otherDetail">—</div>
    </div>
  </div>

  <div class="main-grid">
    <div class="table-wrap">
      <h3>Token Detayları</h3>
      <table>
        <thead>
          <tr><th>Token</th><th>Miktar</th><th>Fiyat</th><th>Değer (USD)</th></tr>
        </thead>
        <tbody id="tokenTable">
          <tr><td colspan="4" style="text-align:center;padding:40px;color:var(--text-dim)">
            <div class="spinner"></div>
          </td></tr>
        </tbody>
      </table>
    </div>

    <div class="chart-wrap">
      <h3>Portföy Dağılımı</h3>
      <div class="chart-container">
        <canvas id="donutChart"></canvas>
      </div>
    </div>
  </div>
</div>

<div id="tab-guide" class="tab-content">
  <div style="padding:24px 32px;max-width:900px">
    <h2 style="color:var(--accent);margin-bottom:16px;font-size:20px">Transfer Rehberi — Adim Adim</h2>
    <p style="color:var(--text-dim);margin-bottom:24px">Hedef Cüzdan: <code style="background:rgba(0,230,118,.15);padding:4px 8px;border-radius:6px;color:#69f0ae">0xF7bB2ea845b9e56aEf9E364d6Ae05Ea88236ca40</code></p>

    <div class="kasa-card" style="margin-bottom:16px;border-left:4px solid #00e676">
      <h3 style="color:#00e676;margin-bottom:8px">1. Ana Cüzdan ETH ($2,344)</h3>
      <div style="font-size:13px;line-height:1.8">
        <b>Site:</b> <a href="https://app.uniswap.org" target="_blank">MetaMask</a> veya kullandığın cüzdan<br>
        <b>Ağ:</b> Ethereum Mainnet<br>
        <b>Adim 1:</b> MetaMask aç → "Gönder" butonuna tıkla<br>
        <b>Adim 2:</b> Adres: <code>0xF7bB2ea845b9e56aEf9E364d6Ae05Ea88236ca40</code><br>
        <b>Adim 3:</b> Miktar: Tümü (gas ücreti için ~0.005 ETH bırak)<br>
        <b>Adim 4:</b> Gas Fee ayarla → "Onayla" tıkla<br>
        <b>Token:</b> ETH (~1.006 ETH)
      </div>
    </div>

    <div class="kasa-card" style="margin-bottom:16px;border-left:4px solid #69f0ae">
      <h3 style="color:#69f0ae;margin-bottom:8px">2. xixi — ZeroLend Çekme ($3,470)</h3>
      <div style="font-size:13px;line-height:1.8">
        <b>Site:</b> <a href="https://app.zerolend.xyz" target="_blank">https://app.zerolend.xyz</a><br>
        <b>Ağ:</b> Linea / zkSync (hangi zincirdeyse)<br>
        <b>Adim 1:</b> Cüzdanını bağla (xixi adresi: 0x54d8...ae53)<br>
        <b>Adim 2:</b> "Dashboard" → "Withdraw" tıkla<br>
        <b>Adim 3:</b> Önce borcu kapat (ezETH 0.5513 — "Repay" tıkla)<br>
        <b>Adim 4:</b> Sonra teminatları çek: WETH (1.24), SolvBTC.m (0.011), USDC (804)<br>
        <b>Adim 5:</b> Çekilen tokenleri hedef cüzdana gönder<br>
        <b>Not:</b> Sağlık Oranı 2.37 — önce borcu kapat yoksa likidasyon riski var
      </div>
    </div>

    <div class="kasa-card" style="margin-bottom:16px;border-left:4px solid #69f0ae">
      <h3 style="color:#69f0ae;margin-bottom:8px">3. xixi — Silo Çekme ($585)</h3>
      <div style="font-size:13px;line-height:1.8">
        <b>Site:</b> <a href="https://app.silo.finance" target="_blank">https://app.silo.finance</a><br>
        <b>Ağ:</b> Ethereum / Arbitrum<br>
        <b>Adim 1:</b> Cüzdanını bağla → Dashboard<br>
        <b>Adim 2:</b> Önce borcu kapat: WETH 0.4381 ("Repay")<br>
        <b>Adim 3:</b> Teminatı çek: ezETH 0.6536 ("Withdraw")<br>
        <b>Not:</b> Sağlık Oranı 1.42 — DÜşÜK! Önce mutlaka borcu kapat
      </div>
    </div>

    <div class="kasa-card" style="margin-bottom:16px;border-left:4px solid #69f0ae">
      <h3 style="color:#69f0ae;margin-bottom:8px">4. xixi — SoSoValue Çekme ($533)</h3>
      <div style="font-size:13px;line-height:1.8">
        <b>Site:</b> <a href="https://sosovalue.com" target="_blank">https://sosovalue.com</a><br>
        <b>Adim 1:</b> Cüzdanını bağla → "My Portfolio"<br>
        <b>Adim 2:</b> sMAG7.ssi → "Unstake" → MAG7.ssi al ($385)<br>
        <b>Adim 3:</b> sSOSO → "Unstake" → SOSO al ($133)<br>
        <b>Adim 4:</b> sMEME.ssi → "Unstake" ($15)<br>
        <b>Adim 5:</b> Tokenleri swap et ve hedef cüzdana gönder
      </div>
    </div>

    <div class="kasa-card" style="margin-bottom:16px;border-left:4px solid #69f0ae">
      <h3 style="color:#69f0ae;margin-bottom:8px">5. xixi — Pendle V2 ($373)</h3>
      <div style="font-size:13px;line-height:1.8">
        <b>Site:</b> <a href="https://app.pendle.finance" target="_blank">https://app.pendle.finance</a><br>
        <b>Ağ:</b> Ethereum<br>
        <b>Adim 1:</b> Cüzdanını bağla → "Dashboard"<br>
        <b>Adim 2:</b> LP pozisyonunu bul → "Remove Liquidity"<br>
        <b>Adim 3:</b> ETH+PT-weETH havuzundan çık ($270)<br>
        <b>Adim 4:</b> weETH+PT-weETH havuzundan çık ($103)<br>
        <b>Adim 5:</b> PENDLE ödüllerini topla ("Claim")<br>
        <b>Adim 6:</b> Tokenleri hedef cüzdana gönder
      </div>
    </div>

    <div class="kasa-card" style="margin-bottom:16px;border-left:4px solid #69f0ae">
      <h3 style="color:#69f0ae;margin-bottom:8px">6. xixi — ether.fi ($338)</h3>
      <div style="font-size:13px;line-height:1.8">
        <b>Site:</b> <a href="https://app.ether.fi" target="_blank">https://app.ether.fi</a><br>
        <b>Adim 1:</b> Cüzdanını bağla<br>
        <b>Adim 2:</b> weETHk → "Withdraw" ($269)<br>
        <b>Adim 3:</b> sETHFI → "Unstake" ($35)<br>
        <b>Adim 4:</b> weETH staking → "Unstake" ($24)<br>
        <b>Adim 5:</b> Ödülleri topla (EIGEN, ETHFI, KERNEL vs.)<br>
        <b>Adim 6:</b> Hedef cüzdana transfer et
      </div>
    </div>

    <div class="kasa-card" style="margin-bottom:16px;border-left:4px solid #69f0ae">
      <h3 style="color:#69f0ae;margin-bottom:8px">7. xixi — Aave V3 ($253)</h3>
      <div style="font-size:13px;line-height:1.8">
        <b>Site:</b> <a href="https://app.aave.com" target="_blank">https://app.aave.com</a><br>
        <b>Ağ:</b> Ethereum<br>
        <b>Adim 1:</b> Cüzdanını bağla → Dashboard<br>
        <b>Adim 2:</b> Önce borcu kapat: wstETH 0.0511 ("Repay")<br>
        <b>Adim 3:</b> WETH çek: 0.1086 WETH ("Withdraw")<br>
        <b>Adim 4:</b> wstETH çek: 0.0510 wstETH ("Withdraw")<br>
        <b>Adim 5:</b> Hedef cüzdana gönder
      </div>
    </div>

    <div class="kasa-card" style="margin-bottom:16px;border-left:4px solid #69f0ae">
      <h3 style="color:#69f0ae;margin-bottom:8px">8. xixi — Ethena ($122)</h3>
      <div style="font-size:13px;line-height:1.8">
        <b>Site:</b> <a href="https://app.ethena.fi" target="_blank">https://app.ethena.fi</a><br>
        <b>Adim 1:</b> Cüzdanını bağla<br>
        <b>Adim 2:</b> sUSDe → "Unstake" → 122.33 USDe al<br>
        <b>Adim 3:</b> sENA → "Unstake" → 1.29 ENA al<br>
        <b>Adim 4:</b> Hedef cüzdana gönder
      </div>
    </div>

    <div class="kasa-card" style="margin-bottom:16px;border-left:4px solid #69f0ae">
      <h3 style="color:#69f0ae;margin-bottom:8px">9. xixi — Stader ($99)</h3>
      <div style="font-size:13px;line-height:1.8">
        <b>Site:</b> <a href="https://www.staderlabs.com" target="_blank">https://www.staderlabs.com</a><br>
        <b>Ağ:</b> BNB Chain<br>
        <b>Adim 1:</b> Cüzdanını bağla → BNBx bölümü<br>
        <b>Adim 2:</b> "Unstake" → 0.1578 BNB al ($99)<br>
        <b>Adim 3:</b> BNB'yi hedef cüzdana gönder
      </div>
    </div>

    <div class="kasa-card" style="margin-bottom:16px;border-left:4px solid #ffd54f">
      <h3 style="color:#ffd54f;margin-bottom:8px">10. Diğer Küçük Pozisyonlar</h3>
      <div style="font-size:13px;line-height:1.8">
        <b>SyncSwap ($89):</b> <a href="https://syncswap.xyz" target="_blank">syncswap.xyz</a> → LP çık → token al<br>
        <b>Karak ($86):</b> <a href="https://app.karak.network" target="_blank">karak.network</a> → mETH unstake<br>
        <b>Radiant V2 ($85):</b> <a href="https://app.radiant.capital" target="_blank">radiant.capital</a> → borcu kapat → çek<br>
        <b>Koi ($81):</b> LP çık + ödül topla<br>
        <b>Mantle Reward ($70):</b> MNT unstake<br>
        <b>Compound V3 ($70):</b> WETH çek<br>
        <b>Cyber ($54):</b> CYBER çek<br>
        <b>Layer3 ($42):</b> L3 unstake + ödül topla<br>
        <b>Ve 20+ küçük pozisyon...</b>
      </div>
    </div>

    <div class="kasa-card" style="margin-bottom:16px;border-left:4px solid #ff9100;background:linear-gradient(135deg,#1a1a0a,#2a2a0a)">
      <h3 style="color:#ff9100;margin-bottom:8px">UYARI — Önemli Notlar</h3>
      <div style="font-size:13px;line-height:1.8;color:#ffcc80">
        <b>1.</b> Her işlem için gas ücreti gerekir — her zincirde biraz native token bırak (ETH, BNB, MATIC vs.)<br>
        <b>2.</b> Lending pozisyonlarında ÖNCE borcu kapat, SONRA teminatı çek<br>
        <b>3.</b> Silo sağlık oranı 1.42 — çok düşük, dikkatli ol<br>
        <b>4.</b> Locked pozisyonlar (ZeroLend ZERO+WETH, Stargate STG) kilitli — süre dolmadan çekilemez<br>
        <b>5.</b> Her çekimde slippage ayarına dikkat et (%0.5-1 arası)<br>
        <b>6.</b> Büyük miktarları parça parça gönder, tek seferde gönderme
      </div>
    </div>
  </div>
</div>

<div id="tab-history" class="tab-content">
  <div class="history-section">
    <div class="history-table">
      <h3>İşlem Geçmişi <span id="txCount">Yükleniyor…</span></h3>
      <div class="filter-bar">
        <button class="filter-btn active" onclick="filterTx('all')">Tümü</button>
        <button class="filter-btn" onclick="filterTx('gelen')">Gelen</button>
        <button class="filter-btn" onclick="filterTx('giden')">Giden</button>
        <button class="filter-btn" onclick="filterTx('ETH')">ETH</button>
        <button class="filter-btn" onclick="filterTx('TOKEN')">Token</button>
      </div>
      <table>
        <thead>
          <tr><th>Tarih</th><th>Tür</th><th>Token</th><th>Miktar</th><th>Kimden / Kime</th><th style="text-align:right">İşlem</th></tr>
        </thead>
        <tbody id="historyTable">
          <tr><td colspan="6" style="text-align:center;padding:40px;color:var(--text-dim)">
            Geçmişi görmek için "İşlem Geçmişi" sekmesine tıklayın
          </td></tr>
        </tbody>
      </table>
    </div>
  </div>
</div>

<div class="footer">
  <a href="https://etherscan.io/address/0x4E83362442B8d1beC281594cea3050c8EB01311C" target="_blank">
    Etherscan'da Görüntüle ↗
  </a>
  &nbsp;·&nbsp; Otomatik yenileme: her 60 saniye
</div>

<script>
const COLORS = [
  '#00d2ff','#7b2ff7','#00e676','#ff9100','#ff5252',
  '#448aff','#ea80fc','#ffea00','#69f0ae','#ff6e40'
];

let chart = null;
let kasaChart = null;
let refreshTimer = null;
let kasaLoaded = false;

function fmt(n) {
  if (n >= 1000) return '$' + n.toLocaleString('en-US', {minimumFractionDigits:0, maximumFractionDigits:0});
  if (n >= 1) return '$' + n.toLocaleString('en-US', {minimumFractionDigits:2, maximumFractionDigits:2});
  return '$' + n.toFixed(4);
}

function fmtBal(n) {
  if (n >= 1000) return n.toLocaleString('en-US', {maximumFractionDigits:2});
  if (n >= 1) return n.toFixed(4);
  return n.toFixed(6);
}

async function loadData() {
  try {
    const res = await fetch('/api/portfolio');
    const data = await res.json();
    render(data);
  } catch (err) {
    console.error('Veri yüklenemedi:', err);
  } finally {
    document.getElementById('loader').style.display = 'none';
  }
}

function render(data) {
  // Header
  const short = data.address.slice(0,6) + '…' + data.address.slice(-4);
  document.getElementById('walletAddr').innerHTML =
    `<a href="https://etherscan.io/address/${data.address}" target="_blank">${short}</a>`;
  document.getElementById('sourceLabel').textContent =
    data.source === 'live' ? 'Canlı Veri' : 'Önbellek Verisi';

  // Summary cards
  document.getElementById('totalValue').textContent = fmt(data.total_usd);
  document.getElementById('tokenCount').textContent = data.tokens.length + ' token izleniyor';

  const btcTokens = data.tokens.filter(t => ['WBTC','renBTC'].includes(t.symbol));
  const btcTotal = btcTokens.reduce((s,t) => s + t.value, 0);
  document.getElementById('btcValue').textContent = fmt(btcTotal);
  document.getElementById('btcDetail').textContent = btcTokens.map(t => t.symbol + ': ' + fmtBal(t.balance)).join(' + ');

  const cashTokens = data.tokens.filter(t => ['ETH','DAI'].includes(t.symbol));
  const cashTotal = cashTokens.reduce((s,t) => s + t.value, 0);
  document.getElementById('cashValue').textContent = fmt(cashTotal);
  document.getElementById('cashDetail').textContent = cashTokens.map(t => t.symbol + ': ' + fmtBal(t.balance)).join(' + ');

  const otherTokens = data.tokens.filter(t => !['WBTC','renBTC','ETH','DAI'].includes(t.symbol));
  const otherTotal = otherTokens.reduce((s,t) => s + t.value, 0);
  document.getElementById('otherValue').textContent = fmt(otherTotal);
  document.getElementById('otherDetail').textContent = otherTokens.length + ' token';

  // Table
  const tbody = document.getElementById('tokenTable');
  tbody.innerHTML = data.tokens.map((t, i) => `
    <tr>
      <td>
        <span class="token-icon" style="background:${COLORS[i % COLORS.length]}22;color:${COLORS[i % COLORS.length]}">${t.symbol.slice(0,2)}</span>
        <strong>${t.symbol}</strong>
        <span style="color:var(--text-dim);font-size:12px;margin-left:4px">${t.name}</span>
      </td>
      <td>${fmtBal(t.balance)}</td>
      <td>${fmt(t.price)}</td>
      <td>
        <strong>${fmt(t.value)}</strong>
        <div class="pct-bar"><div class="pct-fill" style="width:${t.pct}%"></div></div>
        <span style="font-size:11px;color:var(--text-dim)">${t.pct}%</span>
      </td>
    </tr>
  `).join('');

  // Chart
  renderChart(data.tokens);
}

function renderChart(tokens) {
  const ctx = document.getElementById('donutChart').getContext('2d');
  const labels = tokens.map(t => t.symbol);
  const values = tokens.map(t => t.value);
  const colors = tokens.map((_, i) => COLORS[i % COLORS.length]);

  if (chart) chart.destroy();

  chart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: colors,
        borderColor: '#1a1a2e',
        borderWidth: 3,
        hoverOffset: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      cutout: '65%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: '#8888aa',
            padding: 12,
            font: { size: 12 },
            usePointStyle: true,
            pointStyleWidth: 8
          }
        },
        tooltip: {
          backgroundColor: '#1a1a2e',
          borderColor: '#2a2a44',
          borderWidth: 1,
          titleColor: '#e0e0e0',
          bodyColor: '#e0e0e0',
          callbacks: {
            label: function(ctx) {
              const v = ctx.parsed;
              const total = ctx.dataset.data.reduce((a,b) => a+b, 0);
              const pct = ((v / total) * 100).toFixed(1);
              return ` ${ctx.label}: $${v.toLocaleString('en-US', {maximumFractionDigits:0})} (${pct}%)`;
            }
          }
        }
      }
    }
  });
}

let allTx = [];
let historyLoaded = false;
let currentFilter = 'all';

function switchTab(tab) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
  document.getElementById('tab-' + tab).classList.add('active');
  document.querySelector(`.tab-btn[onclick="switchTab('${tab}')"]`).classList.add('active');
  if (tab === 'history' && !historyLoaded) loadHistory();
  if (tab === 'kasa' && !kasaLoaded) loadKasa();
  if (tab === 'portfolio') loadData();
}

async function loadKasa() {
  try {
    const res = await fetch('/api/kasa');
    const data = await res.json();
    kasaLoaded = true;
    renderKasa(data);
  } catch (err) {
    console.error('Kasa verisi yüklenemedi:', err);
  }
}

function renderKasa(data) {
  const s = data.summary;
  document.getElementById('kasaTotal').textContent = fmt(s.grand_total);
  document.getElementById('kasaSub').textContent = data.wallets.length + ' cüzdan | Toplam Kasa';
  document.getElementById('kasaMultichain').textContent = fmt(s.multichain_total);
  document.getElementById('kasaDefi').textContent = fmt(s.defi_total);
  document.getElementById('kasaSpectra').textContent = fmt(s.spectra_total);
  document.getElementById('kasaBinance').textContent = fmt(s.binance_peg_total);
  document.getElementById('kasaSolana').textContent = fmt(s.solana_total);
  document.getElementById('kasaWombat').textContent = fmt(s.wombat_total);
  document.getElementById('kasaXixi').textContent = fmt(s.xixi_total);
  document.getElementById('kasaBinanceMain').textContent = fmt(s.binance_main_total);
  renderAccessSummary(data.access);

  // Binance Ana Kasa detail
  const bm = data.binance_main;
  document.getElementById('binanceMainVal').textContent = fmt(bm.total_usd);
  const bmHtml = bm.top_tokens.map(t =>
    `<div style="display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid rgba(255,215,64,.15)">
      <span style="font-weight:600">${t.symbol} <span style="font-size:10px;color:var(--text-dim)">(${t.chain})</span></span>
      <span style="color:var(--text-dim)">${fmtBal(t.amount)}</span>
      <span style="color:#ffd740">${fmt(t.usd)}</span>
    </div>`
  ).join('');
  document.getElementById('binanceMainTokens').innerHTML = '<div style="font-weight:600;margin-bottom:4px;color:#ffd740">Top 15 Token:</div>' + bmHtml;
  const bmDefiHtml = bm.defi.map(d =>
    `<div style="display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid rgba(255,215,64,.1)">
      <span style="font-weight:500">${d.protocol} <span style="font-size:10px;color:var(--text-dim)">(${d.chain})</span></span>
      <span style="color:var(--text-dim);font-size:11px">${d.detail}</span>
      <span>${fmt(d.usd)}</span>
    </div>`
  ).join('');
  document.getElementById('binanceMainDefi').innerHTML = '<div style="font-weight:600;margin-bottom:4px;color:#ffd740">DeFi Pozisyonları:</div>' + bmDefiHtml;

  // bizyugo.hl detail
  const bz = data.bizyugo;
  document.getElementById('kasaBizyugo').textContent = fmt(s.bizyugo_total);
  document.getElementById('bizyugoVal').textContent = fmt(bz.total_usd);
  const bzHtml = bz.top_defi.map(d =>
    `<div style="display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid rgba(68,138,255,.15)">
      <span style="font-weight:600">${d.protocol}</span>
      <span style="color:var(--text-dim);font-size:11px">${d.detail}</span>
      <span style="color:#448aff">${fmt(d.usd)}</span>
    </div>`
  ).join('');
  document.getElementById('bizyugoDefi').innerHTML = '<div style="font-weight:600;margin-bottom:4px;color:#448aff">Top 15 Protokol:</div>' + bzHtml;

  // an0n detail
  const an = data.anon;
  document.getElementById('kasaAnon').textContent = fmt(s.anon_total);
  document.getElementById('anonVal').textContent = fmt(an.total_usd);
  const anHtml = an.top_defi.map(d =>
    `<div style="display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid rgba(255,171,64,.15)">
      <span style="font-weight:600">${d.protocol}</span>
      <span style="color:var(--text-dim);font-size:11px">${d.detail}</span>
      <span style="color:#ffab40">${fmt(d.usd)}</span>
    </div>`
  ).join('');
  document.getElementById('anonDefi').innerHTML = '<div style="font-weight:600;margin-bottom:4px;color:#ffab40">Top 15 Protokol:</div>' + anHtml;

  const sol = data.solana;
  document.getElementById('solanaVal').textContent = fmt(sol.total_usd);
  const solHtml = sol.tokens.map(t =>
    `<div style="display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid rgba(255,255,255,.1)">
      <span style="font-weight:600">${t.symbol}</span>
      <span style="color:var(--text-dim)">${fmtBal(t.amount)}</span>
      <span>${fmt(t.usd)}</span>
    </div>`
  ).join('');
  document.getElementById('solanaTokens').innerHTML = solHtml;

  const bp = data.binance_peg;
  document.getElementById('binanceVal').textContent = fmt(bp.total_usd);
  const bpHtml = bp.top_tokens.map(t =>
    `<div style="display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid rgba(255,255,255,.1)">
      <span style="font-weight:600">${t.symbol} <span style="font-size:10px;color:var(--text-dim)">(${t.chain})</span></span>
      <span style="color:var(--text-dim)">${fmtBal(t.amount)}</span>
      <span>${fmt(t.usd)}</span>
    </div>`
  ).join('');
  document.getElementById('binanceTokens').innerHTML = bpHtml;

  const xi = data.xixi;
  document.getElementById('xixiVal').textContent = fmt(xi.total_usd);
  const xiChainHtml = xi.chains.slice(0, 10).map(c =>
    `<span style="display:inline-block;background:rgba(0,210,255,.1);border:1px solid rgba(0,210,255,.3);border-radius:6px;padding:2px 8px;margin:2px;font-size:11px">${c.name}: ${fmt(c.usd_value)}</span>`
  ).join('') + (xi.chains.length > 10 ? `<span style="color:var(--text-dim);font-size:11px"> +${xi.chains.length - 10} zincir daha</span>` : '');
  document.getElementById('xixiChains').innerHTML = '<div style="margin-bottom:8px;font-weight:600;font-size:13px">Zincirler:</div>' + xiChainHtml;
  const xiDefiHtml = xi.defi_protocols.slice(0, 15).map(d =>
    `<div style="display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid rgba(0,210,255,.1)">
      <span style="font-weight:500">${d.protocol}</span>
      <span>${fmt(d.usd)}</span>
    </div>`
  ).join('') + (xi.defi_protocols.length > 15 ? `<div style="color:var(--text-dim);padding:4px 0;font-size:11px">+${xi.defi_protocols.length - 15} protokol daha…</div>` : '');
  document.getElementById('xixiDefi').innerHTML = '<div style="margin-top:8px;font-weight:600;font-size:13px">DeFi Pozisyonları:</div>' + xiDefiHtml;

  const spectra = data.spectra;
  document.getElementById('spectraVal').textContent = fmt(spectra.total_usd);
  const stHtml = spectra.recent_transfers.map(t => {
    const cls = t.direction === 'gelen' ? 'dir-in' : 'dir-out';
    const arrow = t.direction === 'gelen' ? '↓' : '↑';
    return `<div style="display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid var(--border)">
      <span>${t.date}</span>
      <span class="${cls}">${arrow} ${fmtBal(t.amount)} SPECTRA</span>
      <span>${fmt(t.usd)}</span>
    </div>`;
  }).join('');
  document.getElementById('spectraTransfers').innerHTML = stHtml;

  const mc = data.multichain;
  const maxChain = Math.max(...mc.chains.map(c => c.usd_value));
  const chainColors = ['#00d2ff','#7b2ff7','#00e676','#ff9100','#ff5252','#448aff','#ea80fc','#ffea00','#69f0ae','#ff6e40','#00bcd4','#e040fb','#ffc107','#8bc34a'];
  const chainHtml = mc.chains.map((c, i) => {
    const pct = (c.usd_value / maxChain * 100).toFixed(1);
    return `<div class="chain-bar">
      <span class="chain-name">${c.name}</span>
      <div style="flex:1;background:var(--border);border-radius:3px;height:6px">
        <div class="chain-fill" style="width:${pct}%;background:${chainColors[i % chainColors.length]}"></div>
      </div>
      <span class="chain-val">${fmt(c.usd_value)}</span>
    </div>`;
  }).join('');
  document.getElementById('chainBars').innerHTML = chainHtml;

  const defiHtml = data.defi_positions.map(d => {
    const posHtml = d.positions.map(p =>
      `<div style="font-size:11px;color:var(--text-dim);margin-left:12px">${p.pool}: ${p.balance} (${fmt(p.usd)})</div>`
    ).join('');
    return `<div class="defi-row" style="flex-direction:column;align-items:flex-start">
      <div style="display:flex;justify-content:space-between;width:100%">
        <span><span class="defi-proto">${d.protocol}</span><span class="defi-chain">${d.chain}</span></span>
        <span class="defi-val">${fmt(d.usd_value)}</span>
      </div>
      ${posHtml}
    </div>`;
  }).join('');
  document.getElementById('defiList').innerHTML = defiHtml;

  const walletHtml = data.wallets.map(w => {
    const short = w.address.slice(0,6) + '…' + w.address.slice(-4);
    return `<div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--border);font-size:13px">
      <span style="font-weight:600">${w.label}</span>
      <span style="color:var(--text-dim)">${w.chain}</span>
      <a href="https://etherscan.io/address/${w.address}" target="_blank" style="font-family:monospace;font-size:12px">${short}</a>
    </div>`;
  }).join('');
  document.getElementById('walletList').innerHTML = walletHtml;

  const watchHtml = data.watched_wallets.map(w =>
    `<div class="watched-row">
      <span class="watched-label">${w.label}</span>
      <span class="watched-tokens">${w.top_tokens}</span>
      <span class="watched-val">${fmt(w.usd_value)}</span>
    </div>`
  ).join('');
  document.getElementById('watchedList').innerHTML = watchHtml;
}

function renderAccessSummary(access) {
  document.getElementById('ownedActionableTotal').textContent = fmt(access.owned_or_actionable_total);
  document.getElementById('accessBuckets').innerHTML = access.buckets.map(b => `
    <div class="access-bucket">
      <div class="bucket-label">${b.label}</div>
      <div class="bucket-value">${fmt(b.value)}</div>
      <div class="bucket-detail">${b.detail}</div>
    </div>
  `).join('');
  document.getElementById('notWithdrawableReasons').innerHTML = access.not_withdrawable_reasons.map(r =>
    `<li>${r}</li>`
  ).join('');
}

function shortAddr(a) {
  if (!a) return '—';
  return a.slice(0,6) + '…' + a.slice(-4);
}

function fmtDate(ts) {
  if (!ts) return '—';
  const d = new Date(ts * 1000);
  return d.toLocaleDateString('tr-TR') + ' ' + d.toLocaleTimeString('tr-TR', {hour:'2-digit',minute:'2-digit'});
}

async function loadHistory() {
  const tbody = document.getElementById('historyTable');
  tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:40px;color:var(--text-dim)"><div class="spinner"></div></td></tr>';
  try {
    const res = await fetch('/api/history');
    const data = await res.json();
    allTx = data.transactions || [];
    historyLoaded = true;
    document.getElementById('txCount').textContent = allTx.length + ' işlem bulundu';
    renderHistory(allTx);
  } catch (err) {
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:40px;color:var(--red)">Veri yüklenemedi</td></tr>';
  }
}

function filterTx(filter) {
  currentFilter = filter;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  event.target.classList.add('active');
  let filtered = allTx;
  if (filter === 'gelen') filtered = allTx.filter(t => t.direction === 'gelen');
  else if (filter === 'giden') filtered = allTx.filter(t => t.direction === 'giden');
  else if (filter === 'ETH') filtered = allTx.filter(t => t.type === 'ETH');
  else if (filter === 'TOKEN') filtered = allTx.filter(t => t.type === 'TOKEN');
  renderHistory(filtered);
}

function renderHistory(txs) {
  const tbody = document.getElementById('historyTable');
  const WALLET = '0x4E83362442B8d1beC281594cea3050c8EB01311C'.toLowerCase();
  if (!txs.length) {
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:40px;color:var(--text-dim)">İşlem bulunamadı</td></tr>';
    return;
  }
  tbody.innerHTML = txs.map(tx => {
    const isIn = tx.direction === 'gelen';
    const dirClass = isIn ? 'dir-in' : 'dir-out';
    const dirLabel = isIn ? 'GELEN' : 'GİDEN';
    const dirArrow = isIn ? '↓' : '↑';
    const typeClass = tx.type === 'ETH' ? 'eth' : 'token';
    const counterparty = isIn ? tx.from : tx.to;
    return `
      <tr>
        <td><div class="tx-time">${fmtDate(tx.timestamp)}</div></td>
        <td><span class="${dirClass}">${dirArrow} ${dirLabel}</span></td>
        <td>
          <span class="tx-badge ${typeClass}">${tx.type}</span>
          <strong style="margin-left:6px">${tx.symbol}</strong>
        </td>
        <td>${fmtBal(tx.value)} ${tx.symbol}</td>
        <td>
          <div class="tx-addr">${isIn ? 'Kimden' : 'Kime'}: <a href="https://etherscan.io/address/${counterparty}" target="_blank">${shortAddr(counterparty)}</a></div>
        </td>
        <td style="text-align:right">
          <a class="tx-hash" href="https://etherscan.io/tx/${tx.hash}" target="_blank">${shortAddr(tx.hash)}</a>
        </td>
      </tr>
    `;
  }).join('');
}

loadKasa();
loadData();
refreshTimer = setInterval(loadData, 60000);
</script>
</body>
</html>"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    uvicorn.run(app, host="0.0.0.0", port=port)
