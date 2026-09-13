import os
import csv
import hashlib
from web3 import Web3
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from rich.console import Console

console = Console()
CSV_FILE = "output/bloklar.csv"
PDF_FILE = "output/bloklar.pdf"

# Web3 Bağlantısı
w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{os.environ.get('INFURA_API_KEY')}"))
if not w3.is_connected():
    console.print("❌ Bağlantı kurulamadı! Key veya interneti kontrol edin.")
    exit()
console.print("✅ Başkomutanım, Ethereum Mainnet’e bağlandık!")
console.print(f"Son blok numarası: {w3.eth.block_number}")

# Son 10 blok
son_blok = w3.eth.block_number
bloklar = []

for n in range(son_blok, son_blok - 10, -1):
    b = w3.eth.get_block(n, full_transactions=False)
    bloklar.append({
        "number": b.number,
        "hash": b.hash.hex(),
        "timestamp": datetime.utcfromtimestamp(b.timestamp).strftime('%Y-%m-%d %H:%M:%S')
    })

# SHA256 ve zincirleme hash
onceki_hash = "0"*64
for b in bloklar:
    b_hash = hashlib.sha256(b["hash"].encode()).hexdigest()
    zincir_hash = hashlib.sha256((onceki_hash + b_hash).encode()).hexdigest()
    b["sha256"] = b_hash
    b["zincir"] = zincir_hash
    onceki_hash = b_hash

# CSV Oluştur
os.makedirs("output", exist_ok=True)
with open(CSV_FILE, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["number", "hash", "timestamp", "sha256", "zincir"])
    writer.writeheader()
    for b in bloklar:
        writer.writerow(b)

# PDF Oluştur
c = canvas.Canvas(PDF_FILE, pagesize=A4)
c.setFont("Helvetica-Bold", 12)
y = 800
c.drawString(50, y, "🛡️ Black Blok Operasyonu - Son 10 Blok Raporu")
y -= 40
for b in bloklar:
    c.drawString(50, y, f"Blok {b['number']} | Hash: {b['hash']}")
    c.drawString(50, y-15, f"Timestamp: {b['timestamp']} | SHA256: {b['sha256']} | Zincir: {b['zincir']}")
    y -= 50
c.save()

# Hash kontrolü
with open(CSV_FILE, "rb") as f:
    csv_hash = hashlib.sha256(f.read()).hexdigest()
with open(PDF_FILE, "rb") as f:
    pdf_hash = hashlib.sha256(f.read()).hexdigest()

console.print(f"✅ Operasyon Tamamlandı!")
console.print(f"[yellow]CSV hash: {csv_hash}[/yellow]")
console.print(f"[yellow]PDF hash: {pdf_hash}[/yellow]")

