#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, json, time
from datetime import datetime

QUEUE_PATH = "/var/mios/registry/media_queue.json"
LOG_PATH = "/var/mios/logs/pools/depot_dispatcher.py.log"

os.makedirs("/var/mios/registry", exist_ok=True)
os.makedirs("/var/mios/logs/pools", exist_ok=True)

class OmnichannelDispatcher:
    def __init__(self):
        self.brand = "@mucizework"
        if not os.path.exists(QUEUE_PATH):
            with open(QUEUE_PATH, "w", encoding="utf-8") as f:
                json.dump({"pending": [], "dispatched": []}, f, indent=2)

    def log(self, msg):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] [DISPATCHER-{self.brand}] {msg}"
        print(line, flush=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    def process_queue(self):
        try:
            with open(QUEUE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            pending = data.get("pending", [])
            if pending:
                self.log(f"{len(pending)} adet medya görevi işleniyor...")
                data["dispatched"].extend(pending)
                data["pending"] = []
                with open(QUEUE_PATH, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
        except Exception as e:
            self.log(f"Kuyruk hatası: {e}")

    def run_loop(self):
        self.log("Dispatcher nöbetçi döngüsü devrede (Hostinger Hub).")
        while True:
            self.process_queue()
            time.sleep(3)

if __name__ == "__main__":
    d = OmnichannelDispatcher()
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        d.process_queue()
    else:
        d.run_loop()
