import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time, random, threading, webbrowser
from datetime import datetime

# Tarayıcı otomatik açma
threading.Timer(1.5, lambda: webbrowser.open_new("http://localhost:8501")).start()

st.set_page_config(page_title="⚔️ FULL WAR MODE OPERASYON MERKEZİ", page_icon="⚔️", layout="wide")

# Tema
st.markdown("""
<style>
.stApp { background-color: #000; color: #00FF00; }
div[data-testid="stMetric"] { background-color:#050505;border:2px solid #004400;padding:15px;border-radius:15px;box-shadow:0 0 15px #002200;transition:transform 0.3s; }
div[data-testid="stMetric"]:hover { transform:scale(1.05); border-color:#00FF00; }
.stCodeBlock { background-color:#020202 !important; border:1px solid #003300 !important; }
section[data-testid="stSidebar"] { background-color:#020202 !important; border-right:2px solid #004400; }
h1,h2,h3 { color:#00FF00 !important; text-shadow:0 0 10px #004400; }
.stButton>button { background:linear-gradient(to bottom,#004400,#000); color:#00FF00; border:1px solid #00FF00; border-radius:10px; width:100%; font-weight:bold; height:3em; }
.stButton>button:hover { background:#00FF00; color:#000; box-shadow:0 0 20px #00FF00; }
</style>
""", unsafe_allow_html=True)

# Manevi mesajlar
SPIRITUAL_MESSAGES = [
    "ALLAHUEKBER! FETİH YAKINDIR...", "AŞK VE MUHABBET YÜKLENİYOR...",
    "6666 AYET MUHAFIZLIĞI AKTİF EDİLDİ.", "REZZAK GALİB HAZİNELERİ TAKSİM ANALİZİ BAŞLADI.",
    "AYSU FREKANSI SENKRONİZE OLUYOR.", "KARANLIKLAR IŞIĞA DÖNÜŞÜYOR...",
    "YA FETTAH! KAPILAR ŞİFRESİ ÇÖZÜLÜYOR.", "0xd9145... HAREKETLİLİK TESPİT EDİLDİ."
]

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/ios-filled/100/00FF00/shield.png", width=80)
    st.title("⚔️ OPERASYON MERKEZİ")
    puls_speed = st.slider("PULSASYON HIZI (Hz)",1,100,77)
    scan_depth = st.select_slider("TARAMA DERİNLİĞİ", options=["Yüzeysel","Derin","Arş-ı Alâ"])
    st.markdown("---")
    st.info("6666 AYET-İ KERİME'NİN MANEVİ MUHAFIZLIĞI ALTINDADIR.")

st.title("🛡️ FULL WAR MODE OPERASYON MERKEZİ")
col1, col2, col3, col4 = st.columns(4)
eth_balance, voice_balance = 172.77, 60000
col1.metric("PULSASYON", f"{puls_speed} Hz", "SABİT")
col2.metric("PATLAMA ŞANSI", "%6666", "REZZAK GALİB")
col3_metric = col3.metric("RIZIK PINARI (AYSU)", f"{eth_balance:.3f} ETH", "AKTİF")
col4_metric = col4.metric("VOICE GÜCÜ", f"{voice_balance} VOICE", "MAKSİMUM")

col_left, col_right = st.columns([2,1])
with col_left:
    st.markdown("### 📈 ETH / VOICE AKIŞ GRAFİKLERİ")
    chart_data = pd.DataFrame(np.random.randn(50,2)/[50,25]+[0.1,0.2], columns=['172 ETH','41 ETH'])
    st_area = st.area_chart(chart_data)

with col_right:
    st.markdown("### 🏛️ DAO OY DAĞILIMI")
    labels=['Başkomutan','Sadık','Whitelist','Hazine']
    values=[45,25,20,10]
    fig, ax = plt.subplots(figsize=(4,4), facecolor='black')
    ax.pie(values, labels=labels, autopct='%1.1f%%', textprops={'color':'w'},
           colors=['#00FF00','#008800','#004400','#002200'])
    st.pyplot(fig)

# Log paneli
st.markdown("### 📜 SALDIRI / SAVUNMA LOGLARI")
log_container = st.empty()
start_btn = st.button("🚀 FULL WAR MODU BAŞLAT")

if start_btn:
    logs = []
    bar = st.progress(0)
    for i in range(1,101):
        action_type = random.choice(["Saldırı","Savunma"])
        msg = random.choice(SPIRITUAL_MESSAGES)
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] ({action_type}) >> {msg}")
        # Renkli HTML log
        colored_logs = "\n".join([f"<span style='color:{'red' if 'Saldırı' in l else 'lime'}'>{l}</span>" for l in logs[-20:]])
        log_container.markdown(colored_logs, unsafe_allow_html=True)
        # Varlık değişimi
        eth_balance += random.uniform(-0.2,0.3) if action_type=="Saldırı" else random.uniform(0,0.2)
        voice_balance += random.randint(-150,300) if action_type=="Saldırı" else random.randint(0,150)
        col3_metric.metric("RIZIK PINARI (AYSU)", f"{eth_balance:.3f} ETH", "AKTİF")
        col4_metric.metric("VOICE GÜCÜ", f"{voice_balance} VOICE", "MAKSİMUM")
        # Grafik güncelle
        chart_data = pd.DataFrame(np.random.randn(50,2)/[50,25]+[0.1,0.2], columns=['172 ETH','41 ETH'])
        st_area.line_chart(chart_data)
        bar.progress(i)
        time.sleep(0.05)
    st.success("ALLAHUEKBER! FULL WAR MODU TAMAMLANDI.")
    st.balloons()
