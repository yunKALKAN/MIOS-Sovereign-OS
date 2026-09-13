import os
import sys
import time
import multiprocessing
import random
import json

DOSYA_KILIDI = "master.lock"

class MonadCreationAnalyzer:
    def __init__(self):
        self.evm_init_signatures = ["60806040", "60606040"]

    def analiz_et(self, hex_data):
        if not hex_data or hex_data == "0x":
            return {"status": "SKIP", "tip": "Boş Veri"}
        pure_hex = hex_data[2:] if hex_data.startswith("0x") else hex_data
        pure_hex = pure_hex.lower()
        header = pure_hex[:8]
        
        if any(header.startswith(sig) for sig in self.evm_init_signatures):
            return {
                "status": "SUCCESS",
                "tip": "Sözleşme Dağıtım Kodu (Creation Code)",
                "boyut_bytes": len(pure_hex) // 2,
                "kuyruk_hex": f"0x{pure_hex[-128:]}"
            }
        return {"status": "SKIP", "tip": "Normal Transfer / Metot Tetiklemesi"}

def sahte_mempool_ve_api_akisi():
    """Gerçek BlockVision öncesi hem transfer hem de kontrat dağıtım verisi üreten hibrit simülatör"""
    secim = random.choice(["transfer", "deployment"])
    if secim == "transfer":
        return "0x4741544f000000000000000000000000b0403b32f54d0bd752113f4009e8b534c6669f44"
    else:
        # Bizim başarıyla test ettiğimiz o meşhur creation kodu
        return "0x608060400000000000000000000000000000000000000000000000000000000000000001000000000000000000000000b0403b32f54d0bd752113f4009e8b534c6669f44"

def ana_master_gorevi():
    print(f"\n🚀 [MASTER] Birleşik Akıllı Radar Aktif. PID: {os.getpid()}")
    analyzer = MonadCreationAnalyzer()
    
    with open(DOSYA_KILIDI, "w") as f: 
        f.write(str(os.getpid()))

    try:
        while True:
            # Zincirden gelen girdi verisini (Input Data) yakala
            ham_tx_data = sahte_mempool_ve_api_akisi()
            
            # Bytecode analitiğini saniyede bin fersah hızla çalıştır
            analiz_sonucu = analyzer.analiz_et(ham_tx_data)
            
            if analiz_sonucu["status"] == "SUCCESS":
                print(f"🚨 [ALARM] Takip edilen cüzdan YENİ KONTRAT dağıtıyor!")
                print(f"📦 Boyut: {analiz_sonucu['boyut_bytes']} Byte | Kuyruk: {analiz_sonucu['kuyruk_hex'][:40]}...")
            else:
                print(f"ℹ️ [İZLEME] Normal cüzdan hareketi/metot tetiklemesi geçildi.")
                
            os.utime(DOSYA_KILIDI, None)
            time.sleep(1) # Aşırı yükü engellemek için ideal döngü süresi
    except KeyboardInterrupt:
        pass
    finally:
        if os.path.exists(DOSYA_KILIDI):
            try: os.remove(DOSYA_KILIDI)
            except: pass

def gölge_black_master_dinleyici():
    print(f"👁️ [BLACK SHADOW] Birleşik yedek kontrolör pusuda. PID: {os.getpid()}")
    while True:
        time.sleep(1)
        if os.path.exists(DOSYA_KILIDI):
            if (time.time() - os.path.getmtime(DOSYA_KILIDI)) > 3: 
                break
        else: 
            break
    print("\n🚨 [CRITICAL] Ana radar kilitlendi! Black Master kontrolü devralıyor...")
    ana_master_gorevi()

if __name__ == "__main__":
    # Önce bot klasörüne zıplayıp dosyayı oraya yazalım
    os.chdir(r"C:\Users\enver\Desktop\mucizework-telegram-bot")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--shadow": 
        gölge_black_master_dinleyici()
    else:
        multiprocessing.Process(target=gölge_black_master_dinleyici).start()
        ana_master_gorevi()
