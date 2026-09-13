#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
  MIOS CORE - NANO-YIELD LIVE COMMAND CENTER & PERFORMANCE REPORTER
  File: /root/MIOS_SOVEREIGN_OS/04_SECURITY_GHOST/legacy_depot/nano_yield_reporter.py
================================================================================
"""

import time
import json
import requests
import os
from datetime import datetime

WALLET = "GPFL3KoAZkiArX6e3hogpQQWKFVnQg24tCPvzaD5tukq"
RPC_URL = "https://api.mainnet-beta.solana.com"
POS_FILE = "/root/MIOS_SOVEREIGN_OS/04_SECURITY_GHOST/legacy_depot/data/nano_yield_active_positions.json"
TRADES_FILE = "/root/MIOS_SOVEREIGN_OS/04_SECURITY_GHOST/legacy_depot/data/nano_yield_trades.jsonl"

def get_sol():
    try:
        r = requests.post(RPC_URL, json={"jsonrpc":"2.0","id":1,"method":"getBalance","params":[WALLET]}, timeout=5)
        return r.json().get("result", {}).get("value", 0) / 1_000_000_000
    except Exception:
        return 0.0

def get_stats():
    total_pnl = 0.0
    trades_count = 0
    wins = 0
    losses = 0
    if os.path.exists(TRADES_FILE):
        try:
            with open(TRADES_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        data = json.loads(line)
                        pnl = float(data.get("NetPnL", data.get("pnl_try", 0.0)))
                        total_pnl += pnl
                        trades_count += 1
                        if pnl > 0:
                            wins += 1
                        elif pnl < 0:
                            losses += 1
        except Exception:
            pass
    return total_pnl, trades_count, wins, losses

def print_report(cycle=1):
    now = datetime.now().strftime("%H:%M:%S")
    sol = get_sol()
    pnl, trades, wins, losses = get_stats()
    win_rate = (wins / trades * 100) if trades > 0 else 0.0

    positions = {}
    if os.path.exists(POS_FILE):
        try:
            with open(POS_FILE, "r", encoding="utf-8") as f:
                positions = json.load(f)
        except Exception:
            pass

    print(f"\n[{now}] 📊 RAPOR #{cycle}")
    print(f"💰 GERÇEK CÜZDAN: {sol:.6f} SOL (~{sol * 4800:.2f} ₺)")
    print(f"📈 TOPLAM PnL: {pnl:+.4f} ₺ | İŞLEMLER: {trades} (Kazanılan: {wins} / Kaybedilen: {losses} | Başarı: %{win_rate:.1f})")
    print(f"🎯 AKTİF POZİSYON SAYISI: {len(positions)}")

    if positions:
        for pid, p in positions.items():
            sym = p.get('token', pid)
            b = p.get('position_size_try', p.get('budget_try', 0.0))
            ep_usd = p.get('entry_price_usd', p.get('entry_price', 'N/A'))
            ep_try = p.get('actual_buy_fill_try', 'N/A')
            conf = p.get('confidence_score', 0.0) * 100
            print(f"   ├─ [{sym}] Bütçe: {b:.2f} ₺ | Giriş: ${ep_usd} ({ep_try:.4f} ₺) | Güven: %{conf:.1f}")
    else:
        print("   └─ Açık pozisyon yok, tarama devam ediyor...")
    print("-" * 75)

if __name__ == "__main__":
    print("=" * 75)
    print("🚀 MIOS CORE KOMUTA MERKEZİ: CANLI PERFORMANS & KAZANÇ RAPORU")
    print("=" * 75)
    cycle = 1
    while True:
        print_report(cycle)
        cycle += 1
        time.sleep(60)
