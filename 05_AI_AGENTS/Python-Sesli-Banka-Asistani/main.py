from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
import re

app = FastAPI(title="Sesli Banka API (Premium)", description="Ücretli Bankacılık Yapay Zeka Servisi")

API_KEYS = {
    "ucretsiz_deneme": "free_key_123",
    "premium_uyelik": "gold_key_999"
}

class KomutIstegi(BaseModel):
    kullanici_id: str
    ses_metni: str

class IslemCevabi(BaseModel):
    sonuc: str
    islem_tipi: str
    bakiye: float

hesaplar = {"ahmet": 5000, "mehmet": 3000, "demo": 10000}

async def api_key_kontrol(x_api_key: str = Header(...)):
    if x_api_key not in API_KEYS.values():
        raise HTTPException(status_code=403, detail="Geçersiz API Anahtarı!")
    return x_api_key

@app.get("/")
def ana_sayfa():
    return {"durum": "aktif", "mesaj": "Banka AI Servisine Hoşgeldiniz."}

@app.post("/islem-yap", response_model=IslemCevabi)
def komut_isles(istek: KomutIstegi, api_key: str = Depends(api_key_kontrol)):
    metin = istek.ses_metni.lower()
    bakiye = hesaplar.get(istek.kullanici_id, 0)
    
    if "bakiye" in metin:
        return {"sonuc": f"Bakiyeniz {bakiye} TL.", "islem_tipi": "bakiye", "bakiye": bakiye}
    elif "gönder" in metin:
        tutar_bul = re.search(r'(\d+)', metin)
        if tutar_bul:
            miktar = int(tutar_bul.group(1))
            if bakiye >= miktar:
                hesaplar[istek.kullanici_id] -= miktar
                return {"sonuc": f"Başarılı! {miktar} TL gönderildi.", "islem_tipi": "transfer", "bakiye": hesaplar[istek.kullanici_id]}
            else:
                return {"sonuc": "Yetersiz Bakiye!", "islem_tipi": "hata", "bakiye": bakiye}
    
    return {"sonuc": "Anlaşılamadı.", "islem_tipi": "hata", "bakiye": bakiye}
