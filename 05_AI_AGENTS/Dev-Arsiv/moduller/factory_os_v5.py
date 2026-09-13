import http.server
import socketserver
import webbrowser
import os
import threading
import time

HTML_CONTENT = r'''<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EAI Factory OS v5.0 • Neural Command</title>
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --deep-space: #05070a;
            --neon-cyan: #00f0ff;
            --neon-purple: #c300ff;
            --neon-gold: #ffcc00;
            --panel-glass: rgba(10,15,25,0.45);
            --grid: rgba(0,240,255,0.08);
            --text-dim: #a0c0ff;
            --alert-red: #ff3366;
        }
        * { margin:0; padding:0; box-sizing:border-box; }
        body {
            background: radial-gradient(circle at 30% 20%, #0a0f1a, var(--deep-space) 70%);
            color: #e0f0ff;
            font-family: 'Inter', sans-serif;
            height: 100vh;
            overflow: hidden;
            background-image: 
                linear-gradient(var(--grid) 1px, transparent 1px),
                linear-gradient(90deg, var(--grid) 1px, transparent 1px);
            background-size: 60px 60px;
        }
        .hud-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 40px;
            background: var(--panel-glass);
            backdrop-filter: blur(16px);
            border-bottom: 1px solid rgba(0,240,255,0.15);
            box-shadow: 0 4px 30px rgba(0,0,0,0.6);
            z-index: 100;
        }
        .title {
            font-family: 'Fira Code', monospace;
            font-size: 1.4rem;
            letter-spacing: 3px;
            color: var(--neon-cyan);
            text-shadow: 0 0 10px var(--neon-cyan);
        }
        .status-bar {
            display: flex;
            gap: 28px;
            font-size: 0.9rem;
        }
        .pulse-dot {
            display: inline-block;
            width: 10px; height: 10px;
            background: #00ff44;
            border-radius: 50%;
            box-shadow: 0 0 12px #00ff44, 0 0 24px #00ff44;
            animation: pulse 2s infinite;
            margin-right: 8px;
        }
        @keyframes pulse {
            0%,100% { opacity: 0.6; transform: scale(1); }
            50%     { opacity: 1;   transform: scale(1.4); }
        }
        .main-grid {
            display: grid;
            grid-template-columns: 3fr 380px;
            height: calc(100vh - 64px);
            gap: 1px;
        }
        .twin-core {
            position: relative;
            background: rgba(0,0,0,0.5);
            overflow: hidden;
        }
        .scan-line {
            position: absolute;
            width: 100%;
            height: 2px;
            background: linear-gradient(transparent, var(--neon-cyan), transparent);
            box-shadow: 0 0 20px var(--neon-cyan);
            animation: scan 7s linear infinite;
            pointer-events: none;
        }
        @keyframes scan {
            0% { top: -10%; }
            100% { top: 110%; }
        }
        .feed-container {
            position: absolute;
            bottom: 20px;
            left: 20px;
            right: 20px;
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
        }
        .feed-window {
            height: 140px;
            background: #000;
            border: 1px solid rgba(0,240,255,0.3);
            border-radius: 6px;
            overflow: hidden;
            position: relative;
        }
        .feed-window img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            filter: brightness(0.85) contrast(1.15);
        }
        .feed-label {
            position: absolute;
            top: 8px;
            left: 8px;
            background: rgba(0,0,0,0.7);
            padding: 4px 10px;
            font-size: 0.75rem;
            border-radius: 3px;
            border-left: 3px solid var(--neon-cyan);
        }
        .co-pilot-panel {
            background: var(--panel-glass);
            backdrop-filter: blur(12px);
            border-left: 1px solid rgba(0,240,255,0.15);
            padding: 24px 20px;
            display: flex;
            flex-direction: column;
            gap: 20px;
            overflow-y: auto;
        }
        .co-pilot-header {
            font-family: 'Fira Code', monospace;
            color: var(--neon-gold);
            font-size: 1.1rem;
            border-bottom: 1px solid rgba(255,204,0,0.3);
            padding-bottom: 8px;
        }
        .co-pilot-advice {
            background: rgba(255,204,0,0.08);
            border: 1px solid rgba(255,204,0,0.3);
            padding: 14px;
            border-radius: 6px;
            font-size: 0.92rem;
            line-height: 1.5;
        }
        .co-pilot-advice strong { color: var(--neon-gold); }
        .log-window {
            background: #000;
            border: 1px solid #222;
            padding: 12px;
            font-family: 'Fira Code', monospace;
            font-size: 0.85rem;
            color: #88ffdd;
            height: 240px;
            overflow-y: auto;
        }
        .log-entry { margin-bottom: 4px; }
        .log-time { color: #666; }
        .metrics-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }
        .metric-card {
            background: rgba(0,240,255,0.05);
            border: 1px solid rgba(0,240,255,0.2);
            padding: 12px;
            border-radius: 6px;
            text-align: center;
        }
        .metric-value {
            font-size: 1.4rem;
            font-weight: bold;
            color: var(--neon-cyan);
        }
        .metric-label { font-size: 0.8rem; color: var(--text-dim); margin-top: 4px; }
        footer {
            background: rgba(0,0,0,0.7);
            padding: 10px 40px;
            font-size: 0.8rem;
            color: #888;
            display: flex;
            justify-content: space-between;
            border-top: 1px solid #222;
        }
    </style>
</head>
<body>

<div class="hud-top">
    <div class="title">EAI FACTORY OS v5.0 • NEURAL COMMAND</div>
    <div class="status-bar">
        <span><span class="pulse-dot"></span> HYPER-SECURE LINK ACTIVE</span>
        <span>Latency: 3ms</span>
        <span>Sync: 01:03:28</span>
    </div>
</div>

<div class="main-grid">
    <div class="twin-core">
        <div class="scan-line"></div>
        <img src="https://images.unsplash.com/photo-1581093450021-4a7360e9a6b5?auto=format&fit=crop&w=1800&q=90" 
             style="width:100%;height:100%;object-fit:cover;filter:brightness(0.75) contrast(1.1);">
        
        <div class="feed-container">
            <div class="feed-window">
                <div class="feed-label">CAM_01 • DIGITAL TWIN</div>
                <img src="https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=800&q=80">
            </div>
            <div class="feed-window">
                <div class="feed-label">CAM_02 • NEURAL RECOGNITION</div>
                <img src="https://images.unsplash.com/photo-1581092160560-1c1e428e9d65?auto=format&fit=crop&w=800&q=80">
            </div>
            <div class="feed-window">
                <div class="feed-label">CAM_03 • THERMAL SPECTRUM</div>
                <img src="https://images.unsplash.com/photo-1614850523296-d8c1af93d400?auto=format&fit=crop&w=800&q=80">
            </div>
        </div>
    </div>

    <div class="co-pilot-panel">
        <div class="co-pilot-header">NEURAL CO-PILOT • CONFIDENCE: 98.7%</div>
        
        <div class="co-pilot-advice">
            <strong>AKTİF ANALİZ:</strong> Kol-03 servo yükünde %1.8 artış.<br>
            <strong>ÖNERİ:</strong> Yağlama döngüsü 3 saat içinde başlatılmalı.<br>
            <strong>UYARI:</strong> Reactor çekirdek sıcaklığı kritik eşikte (+184.9°C).<br>
            <strong>OPTİMİZASYON:</strong> Enerji verimliliği %13.4 artırılabilir.
        </div>

        <div class="log-window" id="log">
            <div class="log-entry"><span class="log-time">[23:17:42]</span> Edge node sync completed</div>
            <div class="log-entry"><span class="log-time">[23:17:55]</span> Neural recognition → %99.2 başarı</div>
            <div class="log-entry"><span class="log-time">[23:18:02]</span> Thermal anomaly: +12°C detected</div>
            <div class="log-entry"><span class="log-time">[23:18:10]</span> Quantum gates sync completed</div>
            <div class="log-entry"><span class="log-time">[23:18:18]</span> Batch #9921 → ETO 138s</div>
            <div class="log-entry"><span class="log-time">[23:18:25]</span> Predictive maintenance scheduled: 04:12</div>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">4 ms</div>
                <div class="metric-label">LATENCY</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">14%</div>
                <div class="metric-label">CPU LOAD</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">3.4 GB</div>
                <div class="metric-label">NPU MEMORY</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">99.8%</div>
                <div class="metric-label">STABILITY</div>
            </div>
        </div>

        <button class="glow-btn" style="margin-top:auto;padding:14px;font-size:1rem;">EXECUTE NEURAL OVERRIDE</button>
    </div>
</div>

<footer>
    <div>Aktif Kamera: <strong>3/3</strong> • AI Confidence: <strong>98.7%</strong></div>
    <div>Edge Node 7 • Alpha • Quantum-Ready</div>
</footer>

<script>
    setInterval(() => {
        document.querySelectorAll('.metric-value')[0].textContent = Math.floor(Math.random()*5 + 2) + " ms";
        document.querySelectorAll('.metric-value')[1].textContent = Math.floor(Math.random()*20 + 5) + "%";
        document.querySelectorAll('.metric-value')[2].textContent = (Math.random()*2 + 3.2).toFixed(1) + " GB";
    }, 8000);
</script>
</body>
</html>'''

def create_html_file():
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)
    print("→ index.html oluşturuldu.")

def open_browser():
    time.sleep(1.5)
    webbrowser.open("http://localhost:8000")

if __name__ == "__main__":
    create_html_file()
    
    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler
    
    print(f"\nEAI Factory OS v5.0 • Neural Command Center")
    print(f"Sunucu başlatılıyor... http://localhost:{PORT}\n")
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("Sunucu aktif. Tarayıcıda açılıyor...")
        print("Kapatmak için Ctrl+C tuşlayın.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nSunucu kapatıldı.")
            httpd.server_close()
