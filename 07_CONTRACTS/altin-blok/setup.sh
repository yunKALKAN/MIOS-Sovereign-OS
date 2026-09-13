#!/bin/bash
# setup.sh - Altin Blok Dashboard kurulumu ve çalıştırma

echo "🔹 Sanal ortam kuruluyor..."
python3 -m venv venv

echo "🔹 Sanal ortam aktif ediliyor..."
source venv/bin/activate

echo "🔹 Pip güncelleniyor..."
python3 -m pip install --upgrade pip

echo "🔹 Gerekli paketler yükleniyor..."
python3 -m pip install -r requirements.txt

echo ""
echo "🔹 Cüzdan İzleme Dashboard'unu başlatmak için:"
echo "   python wallet_dashboard.py"
echo "   Ardından http://localhost:8050 adresini açın."
echo ""
echo "🔹 Opsiyonel: Etherscan API anahtarı ayarlayın:"
echo "   export ETHERSCAN_API_KEY=senin_anahtarin"
