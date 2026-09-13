#!/usr/bin/env bash
WALLET="GPFL3KoAZkiArX6e3hogpQQWKFVnQg24tCPvzaD5tukq"
LOG_DIR="$HOME/01_MIOS_CORE/bot_depot"

while true; do
    clear
    echo "=========================================================================================="
    echo " ⚡ MIOS NANO-YIELD 24/7 AUTONOMOUS MONITOR (10 DAKİKALIK RAPOR DÖNGÜSÜ)"
    echo " Zaman: $(date '+%Y-%m-%d %H:%M:%S UTC%z') | Mod: %100 REAL MAINNET"
    echo " Cüzdan: $WALLET"
    echo " Solscan: https://solscan.io/account/$WALLET"
    echo "=========================================================================================="
    
    # Gerçek Zincir Bakiyesi Sorgulama
    RAW_BAL=$(curl -s -X POST -H "Content-Type: application/json" -d \
      "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"getBalance\",\"params\":[\"$WALLET\"]}" \
      https://api.mainnet-beta.solana.com | grep -o '"value":[0-9]*' | cut -d':' -f2)
    
    if [ -n "$RAW_BAL" ]; then
        SOL_BAL=$(awk "BEGIN {printf \"%.6f\", $RAW_BAL / 1000000000}")
        TRY_EST=$(awk "BEGIN {printf \"%.2f\", $SOL_BAL * 4800}")
        echo " 💰 Kasa Serbest Bakiye: $SOL_BAL SOL (~$TRY_EST ₺)"
    else
        echo " 💰 Kasa Serbest Bakiye: RPC Yanıtı Bekleniyor..."
    fi

    echo "------------------------------------------------------------------------------------------"
    echo " 🛡️ CANLI KORUMA KALKANI & BOT GÜNLÜĞÜ (Son Olaylar):"
    echo "------------------------------------------------------------------------------------------"
    if [ -f "$LOG_DIR/nano_yield_live.log" ]; then
        tail -n 12 "$LOG_DIR/nano_yield_live.log"
    else
        echo " [INFO] Sistem stabil döngüde, log dosyası taranıyor..."
    fi
    
    echo "=========================================================================================="
    echo " [OK] 24/7 Otonom Nöbet Aktif. Sonraki konsolide güncelleme 10 dakika sonra (600s)..."
    sleep 600
done
