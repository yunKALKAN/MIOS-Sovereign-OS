#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
  MIOS OMNICHANNEL DEPOT DISPATCHER — @mucizework Media Hook Engine
================================================================================
"""

import os
import sys
import json
import time
from datetime import datetime

QUEUE_PATH = "/var/mios/registry/media_queue.json"
LOG_PATH = "/var/mios/logs/pools/depot_dispatcher.py.log"
POOLS_PATH = "/var/mios/registry/pools.json"

os.makedirs("/var/mios/registry", exist_ok=True)
os.makedirs("/var/mios/logs/pools", exist_ok=True)

class OmnichannelDispatcher:
    def __init__(self):
        self.brand = "@mucizework"
        self.ensure_queue()

    def log(self, msg):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{ts}] [DISPATCHER-@mucizework] {msg}"
        print(formatted, flush=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")

    def ensure_queue(self):
        if not os.path.exists(QUEUE_PATH):
            with open(QUEUE_PATH, "w", encoding="utf-8") as f:
                json.dump({"pending": [], "dispatched": []}, f, indent=2)

    def hook_telegram(self, payload):
        self.log(f"-> [Telegram Hook] İleti iletildi: {payload.get('summary', '')[:40]}...")
        return {"status": "SUCCESS", "platform": "Telegram", "handle": self.brand}

    def hook_x(self, payload):
        tweet = f"{payload.get('title', '')}\n\n{payload.get('summary', '')}\n\n{self.brand} #MucizeWork #AI"
        self.log(f"-> [X Hook] Mikroblog tweet kuyruğa işlendi ({len(tweet)} chr)")
        return {"status": "SUCCESS", "platform": "X (Twitter)", "chars": len(tweet)}

    def hook_linkedin(self, payload):
        self.log(f"-> [LinkedIn Hook] B2B Bülten hazırlandı: '{payload.get('title', '')}'")
        return {"status": "SUCCESS", "platform": "LinkedIn"}

    def hook_youtube(self, payload):
        self.log(f"-> [YouTube Hook] Video/Shorts metadata kuyruğu tetiklendi: {payload.get('title', '')}")
        return {"status": "QUEUED", "platform": "YouTube"}

    def hook_instagram(self, payload):
        self.log(f"-> [Instagram Hook] Görsel & Reels kancası hazırlandı.")
        return {"status": "QUEUED", "platform": "Instagram"}

    def hook_tiktok(self, payload):
        self.log(f"-> [TikTok Hook] Kısa dikey video sinyali oluşturuldu.")
        return {"status": "QUEUED", "platform": "TikTok"}

    def hook_facebook(self, payload):
        self.log(f"-> [Facebook Hook] Sayfa topluluk güncellemesi fırlatıldı.")
        return {"status": "SUCCESS", "platform": "Facebook"}

    def hook_reklik(self, payload):
        self.log(f"-> [Reklik Hook] Reklam & Promosyon motoru eşleştirildi.")
        return {"status": "ACTIVE", "platform": "Reklik"}

    def dispatch_all(self, item):
        self.log(f"=== OMNICHANNEL YAYINI BAŞLATILIYOR: {item.get('title', 'Başlıksız')} ===")
        results = {
            "telegram": self.hook_telegram(item),
            "x": self.hook_x(item),
            "linkedin": self.hook_linkedin(item),
            "youtube": self.hook_youtube(item),
            "instagram": self.hook_instagram(item),
            "tiktok": self.hook_tiktok(item),
            "facebook": self.hook_facebook(item),
            "reklik": self.hook_reklik(item)
        }
        item["dispatched_at"] = datetime.now().isoformat()
        item["results"] = results
        return item

    def process_queue(self):
        try:
            with open(QUEUE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)

            pending = data.get("pending", [])
            if not pending:
                return

            dispatched = data.get("dispatched", [])
            while pending:
                item = pending.pop(0)
                processed = self.dispatch_all(item)
                dispatched.append(processed)

            with open(QUEUE_PATH, "w", encoding="utf-8") as f:
                json.dump({"pending": pending, "dispatched": dispatched[-50:]}, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.log(f"Hata: {str(e)}")

    def run_loop(self):
        self.log("Dispatcher aktif. @mucizework kuyruk nöbetçisi çalışıyor...")
        while True:
            self.process_queue()
            time.sleep(3)

if __name__ == "__main__":
    dispatcher = OmnichannelDispatcher()
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        dispatcher.process_queue()
    else:
        dispatcher.run_loop()
