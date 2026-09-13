import os
import sys
import time
import multiprocessing
import random

DOSYA_KILIDI = "master.lock"

def sahte_blockvision_verisi():
    havuzlar = ["Monad-WETH-USDC", "Monad-Pancake-USDT", "Curve-Monad-BTC"]
    return {"poolId": random.choice(havuzlar), "balance0": round(random.uniform(10, 500), 2), "balance1": round(random.uniform(1000, 50000), 2)}

def ana_master_gorevi():
    print(f"\n🚀 [MASTER] Ana kontrol bloğu aktifleşti. PID: {os.getpid()}")
    with open(DOSYA_KILIDI, "w") as f: f.write(str(os.getpid()))
    try:
        while True:
            v = sahte_blockvision_verisi()
            print(f"⚡ [MASTER] Zincir üstü veri tarandı -> Havuz: {v['poolId']} | Miktarlar: {v['balance0']} / {v['balance1']}")
            os.utime(DOSYA_KILIDI, None)
            time.sleep(0.5)
    except KeyboardInterrupt: pass
    finally:
        if os.path.exists(DOSYA_KILIDI):
            try: os.remove(DOSYA_KILIDI)
            except: pass

def gölge_black_master_dinleyici():
    print(f"👁️ [BLACK SHADOW] Yedek kontrolör pusuda bekliyor. PID: {os.getpid()}")
    while True:
        time.sleep(1)
        if os.path.exists(DOSYA_KILIDI):
            if (time.time() - os.path.getmtime(DOSYA_KILIDI)) > 3: break
        else: break
    ana_master_gorevi()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--shadow": gölge_black_master_dinleyici()
    else:
        multiprocessing.Process(target=gölge_black_master_dinleyici).start()
        ana_master_gorevi()
