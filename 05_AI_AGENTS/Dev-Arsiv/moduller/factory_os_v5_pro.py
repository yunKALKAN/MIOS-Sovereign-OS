#!/usr/bin/env python3
import http.server
import socketserver
import webbrowser
import time
import random

PORT = 8000

print(f"→ http://factory.mucizexis.shop:{PORT} • çalışıyor...")
webbrowser.open(f"http://factory.mucizexis.shop:{PORT}")

with socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
    print("Sunucu aktif. Tarayıcıda açılıyor...")
    httpd.serve_forever()
