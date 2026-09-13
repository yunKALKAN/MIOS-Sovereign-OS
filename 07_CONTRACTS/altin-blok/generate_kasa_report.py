#!/usr/bin/env python3
"""Kasa Özeti PDF Rapor Oluşturucu — Tüm cüzdanlar, DeFi, zincirler."""

import os
import json
import httpx
from datetime import datetime, timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
)

ETHERSCAN_KEY = os.environ.get("ETHERSCAN_API_KEY", "")
DEBANK_KEY = os.environ.get("DEBANK_API_KEY", "")
ETH_PRICE_USD = 2335.0  # fallback

WALLETS = {
    "Ana Cüzdan": "0x4E83362442B8d1beC281594cea3050c8EB01311C",
    "Ek Cüzdan 1": "0x65e65Ae6b2C77e4E95E84e869B135EAee0164258",
    "Ek Cüzdan 2": "0xE81cBBD77f62509C15BbFd12aAD57D0262e313d9",
    "Ek Cüzdan 3": "0x232B8637f9905628b3C278e72f70D26c2B15599b",
    "Ek Cüzdan 4": "0xdDafD55B1d3CF49BDB00e5c6B40440b27B85d13F",
    "Ek Cüzdan 5": "0xb0d17E129290FD81b0B3d91D2Bd7b79D78c205a5",
    "Ek Cüzdan 6": "0xA9487a4a6A98722d26d6B9B0D0f5a0aC32497198",
    "Ek Cüzdan 7": "0x16849c6834BA5b6570858575b7Dd35c97FA75942",
    "Ek Cüzdan 8": "0xF7bB2ea845b9e56aaDE9f1dd5dbEd04C35B8ca40",
}

SPECTRA = {
    "address": "0x6a89228055c7c28430692e342f149f37462b478b",
    "label": "SPECTRA Hesabı",
    "chain": "Base",
    "total_usd": 796989,
    "token": "SPECTRA",
    "tvl": 167512.20,
}

XIXI = {
    "address": "0x54d818277b2b40adfe3ee72e82e6a8fcdd92ae53",
    "total_usd": 8927,
    "chains": 27,
    "defi_protocols": 41,
    "top_defi": [
        ("ZeroLend", 3470), ("Silo", 585), ("SoSoValue", 533),
        ("ether.fi", 338), ("Pendle V2", 373), ("Aave V3", 253),
        ("Ethena", 122), ("Stader", 99), ("SyncSwap", 89), ("Karak", 86),
    ],
}

BINANCE_PEG = {
    "address": "0x2170ed0880ac9a755fd29b2688956bd959f933f8",
    "total_usd": 72820155,
    "chains": {"BNB Chain": 72274762, "Ethereum": 512543},
    "top_tokens": [
        ("ETH (BNB)", 31023.43, 72129486),
        ("ETH (ETH)", 216.55, 503477),
        ("BUSD", 72969.48, 72957),
        ("USDT", 36527.23, 36517),
        ("BTCB", 0.2178, 16823),
        ("DOGE", 81406.39, 8278),
        ("SHIB", 254397249.67, 1583),
        ("AXS", 1317.68, 2008),
    ],
}

WOMBAT = {
    "address": "0x4447de210475bfa08e5d42271a73d7624c8a5ac6",
    "total_usd": 1197232,
    "chain": "BNB Chain",
    "tokens": [("ETH", 513.53, 1197231)],
}

SOLANA = {
    "total_usd": 6428035,
    "token_accounts": 5000,
    "sol_balance": 104.44,
    "tokens": [
        ("SUMMIT", 576498199010.9, 4312219),
        ("NUTX", 480000000000000, 1265813),
        ("IBRL", 743433700.09, 843252),
        ("WSOL", 51.13, 4339),
        ("USDT", 1941.98, 1942),
        ("USDC", 1713.15, 1713),
        ("RNLD", 111128356.43, 6776),
        ("CR", 9000000, 155),
        ("GOLDINU", 177325, 106),
    ],
}

DEFI_MAIN = [
    ("Pendle V2", "Ethereum", 372.44),
    ("Aave V3", "Ethereum", 253.08),
    ("Ethena", "Ethereum", 122.41),
    ("Alpaca Finance", "BSC", 78.60),
    ("Venus", "BSC", 22.65),
    ("PancakeSwap", "BSC", 22.18),
    ("bDollar", "BSC", 6.91),
    ("Superfluid", "Polygon", 0.01),
]

MULTICHAIN = [
    ("Ethereum", 11938), ("Arbitrum", 3395), ("Avalanche", 3252),
    ("BSC", 2280), ("Boba", 2009), ("Polygon", 1241),
    ("OEC", 1052), ("Moonriver", 996.32), ("Optimism", 481.66),
    ("Fantom", 388.45), ("xDai", 305.39), ("Celo", 162.94),
    ("HECO", 85.54), ("Cronos", 67.64),
]


def fmt(val):
    if val >= 1_000_000:
        return f"${val:,.0f}"
    elif val >= 1000:
        return f"${val:,.2f}"
    else:
        return f"${val:.2f}"


def fetch_eth_balance(address: str) -> float:
    if not ETHERSCAN_KEY:
        return 0.0
    try:
        r = httpx.get(
            "https://api.etherscan.io/v2/api",
            params={
                "chainid": 1, "module": "account", "action": "balance",
                "address": address, "tag": "latest", "apikey": ETHERSCAN_KEY,
            },
            timeout=10,
        )
        d = r.json()
        if d.get("status") == "1":
            return int(d["result"]) / 1e18
    except Exception:
        pass
    return 0.0


def fetch_eth_price() -> float:
    try:
        r = httpx.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "ethereum", "vs_currencies": "usd"},
            timeout=10,
        )
        return r.json()["ethereum"]["usd"]
    except Exception:
        return ETH_PRICE_USD


def generate_report():
    now = datetime.now(timezone.utc)
    eth_price = fetch_eth_price()
    print(f"ETH Fiyat: ${eth_price:,.2f}")

    wallet_balances = {}
    total_wallet_usd = 0
    for label, addr in WALLETS.items():
        bal = fetch_eth_balance(addr)
        usd = bal * eth_price
        wallet_balances[label] = {"eth": bal, "usd": usd, "address": addr}
        total_wallet_usd += usd
        print(f"  {label}: {bal:.6f} ETH = {fmt(usd)}")

    multichain_total = sum(v for _, v in MULTICHAIN)
    defi_main_total = sum(v for _, _, v in DEFI_MAIN)
    xixi_total = XIXI["total_usd"]
    binance_total = BINANCE_PEG["total_usd"]
    wombat_total = WOMBAT["total_usd"]
    solana_total = SOLANA["total_usd"]
    spectra_total = SPECTRA["total_usd"]

    grand_total = (
        multichain_total + defi_main_total + xixi_total +
        binance_total + wombat_total + solana_total + spectra_total
    )

    hot_wallets = total_wallet_usd
    investments = defi_main_total + xixi_total
    daily_estimate = grand_total * 0.0001  # ~0.01% estimate

    out = "/home/ubuntu/repos/altin_blok/KASA_RAPORU.pdf"
    doc = SimpleDocTemplate(out, pagesize=A4, topMargin=15*mm, bottomMargin=15*mm)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("Title2", parent=styles["Title"], fontSize=22,
                                  textColor=colors.HexColor("#1a237e"), spaceAfter=6)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=14,
                         textColor=colors.HexColor("#0d47a1"), spaceBefore=12, spaceAfter=6)
    normal = styles["Normal"]
    small = ParagraphStyle("Small", parent=normal, fontSize=8, textColor=colors.grey)

    elements = []

    elements.append(Paragraph("KASA TOPLAM RAPORU", title_style))
    elements.append(Paragraph(f"Tarih: {now.strftime('%Y-%m-%d %H:%M UTC')} | ETH: ${eth_price:,.2f}", small))
    elements.append(Spacer(1, 6*mm))

    summary_data = [
        ["Kategori", "Değer (USD)", "Detay"],
        ["TOPLAM KASA", fmt(grand_total), "Tüm cüzdanlar + DeFi"],
        ["Binance-Peg ETH", fmt(binance_total), "31K ETH — BNB Chain kontrat"],
        ["Solana Cüzdanı", fmt(solana_total), f"{SOLANA['token_accounts']} token hesabı"],
        ["Wombat Exchange", fmt(wombat_total), "513 ETH — BNB Chain"],
        ["SPECTRA", fmt(spectra_total), f"Base — TVL: {fmt(SPECTRA['tvl'])}"],
        ["Multi-Chain Varlıklar", fmt(multichain_total), f"{len(MULTICHAIN)} zincir"],
        ["xixi DeFi", fmt(xixi_total), f"{XIXI['chains']} zincir, {XIXI['defi_protocols']} protokol"],
        ["DeFi (Ana Cüzdan)", fmt(defi_main_total), f"{len(DEFI_MAIN)} protokol"],
        ["", "", ""],
        ["SICAK CÜZDANLAR", fmt(hot_wallets), f"{len(WALLETS)} Ethereum cüzdanı"],
        ["YATIRIMLAR (DeFi)", fmt(investments), "DeFi pozisyonları toplamı"],
        ["GÜNLÜK KAZANÇ (tahmini)", fmt(daily_estimate), "~%0.01 günlük oran"],
    ]

    t = Table(summary_data, colWidths=[140, 120, 200])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a237e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#e8eaf6")),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#90a4ae")),
        ("ROWBACKGROUNDS", (0, 2), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 8*mm))

    elements.append(Paragraph("Ethereum Cüzdan Bakiyeleri (Canlı)", h2))
    w_data = [["Cüzdan", "Adres", "ETH Bakiye", "USD Değeri"]]
    for label, info in wallet_balances.items():
        short = info["address"][:8] + "..." + info["address"][-4:]
        w_data.append([label, short, f"{info['eth']:.6f}", fmt(info["usd"])])
    w_data.append(["TOPLAM", "", "", fmt(total_wallet_usd)])

    wt = Table(w_data, colWidths=[100, 110, 80, 100])
    wt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d47a1")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#90a4ae")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#e3f2fd")]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e8eaf6")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elements.append(wt)
    elements.append(Spacer(1, 6*mm))

    elements.append(Paragraph("Multi-Chain Dagitimi", h2))
    mc_data = [["Zincir", "USD Degeri", "Yuzde"]]
    for chain, val in MULTICHAIN:
        pct = val / multichain_total * 100
        mc_data.append([chain, fmt(val), f"%{pct:.1f}"])
    mc_data.append(["TOPLAM", fmt(multichain_total), "%100"])

    mct = Table(mc_data, colWidths=[120, 120, 80])
    mct.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1b5e20")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#90a4ae")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#e8f5e9")]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#c8e6c9")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elements.append(mct)
    elements.append(Spacer(1, 6*mm))

    elements.append(Paragraph("DeFi Pozisyonlari (Ana Cuzdan)", h2))
    defi_data = [["Protokol", "Zincir", "USD Degeri"]]
    for proto, chain, val in DEFI_MAIN:
        defi_data.append([proto, chain, fmt(val)])
    defi_data.append(["TOPLAM", "", fmt(defi_main_total)])

    dt = Table(defi_data, colWidths=[140, 100, 100])
    dt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4a148c")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (2, 0), (2, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#90a4ae")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f3e5f5")]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e1bee7")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elements.append(dt)
    elements.append(Spacer(1, 6*mm))

    elements.append(Paragraph("xixi DeFi - Top 10 Protokol", h2))
    xi_data = [["Protokol", "USD Degeri"]]
    for proto, val in XIXI["top_defi"]:
        xi_data.append([proto, fmt(val)])
    xi_data.append(["TOPLAM (41 protokol)", fmt(xixi_total)])

    xit = Table(xi_data, colWidths=[200, 120])
    xit.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#00695c")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#90a4ae")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#e0f2f1")]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#b2dfdb")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elements.append(xit)
    elements.append(Spacer(1, 6*mm))

    elements.append(Paragraph("Solana Cuzdani - Top Tokenler", h2))
    sol_data = [["Token", "Miktar", "USD Degeri", "Yuzde"]]
    for sym, amt, usd in SOLANA["tokens"]:
        pct = usd / solana_total * 100
        if amt > 1_000_000:
            amt_str = f"{amt:,.0f}"
        else:
            amt_str = f"{amt:,.2f}"
        sol_data.append([sym, amt_str, fmt(usd), f"%{pct:.1f}"])
    sol_data.append(["TOPLAM", f"{SOLANA['token_accounts']} hesap", fmt(solana_total), "%100"])

    st = Table(sol_data, colWidths=[80, 130, 100, 60])
    st.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e65100")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#90a4ae")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#fff3e0")]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#ffe0b2")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elements.append(st)
    elements.append(Spacer(1, 6*mm))

    elements.append(Paragraph("Binance-Peg ETH - Token Dagilimi", h2))
    bp_data = [["Token", "Miktar", "USD Degeri"]]
    for sym, amt, usd in BINANCE_PEG["top_tokens"]:
        if amt > 1_000_000:
            amt_str = f"{amt:,.0f}"
        else:
            amt_str = f"{amt:,.4f}"
        bp_data.append([sym, amt_str, fmt(usd)])
    bp_data.append(["TOPLAM", "", fmt(binance_total)])

    bpt = Table(bp_data, colWidths=[120, 130, 120])
    bpt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f57f17")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#90a4ae")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#fffde7")]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#fff9c4")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elements.append(bpt)
    elements.append(Spacer(1, 4*mm))

    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1a237e")))
    elements.append(Spacer(1, 3*mm))
    elements.append(Paragraph(
        f"Rapor: {now.strftime('%Y-%m-%d %H:%M UTC')} | "
        f"Etherscan API: Aktif | DeBank API: Bakiye 0 (sarj gerekli) | "
        f"Kaynak: altin_blok Dashboard",
        small
    ))

    doc.build(elements)
    print(f"\nRapor olusturuldu: {out}")
    return out


if __name__ == "__main__":
    generate_report()
