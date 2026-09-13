/**
 * 🤖 MZC MUCIZEWORK™ // GHOST ENGINE OS - PRIVY REST API TESTER
 * ── Vantuz Kimlik Doğrulama Katmanı Ön Testi ──
 * Mühür: Yunus Kalkan // Speak and Go Limited
 */

const axios = require('axios');
require('../../config/load-env.cjs');

const PRIVY_APP_ID = process.env.TELEGRAM_PRIVY_APP_ID;
const PRIVY_APP_SECRET = process.env.TELEGRAM_PRIVY_APP_SECRET;

if (!PRIVY_APP_SECRET) {
    console.error("🚨 [CRITICAL] TELEGRAM_PRIVY_APP_SECRET C:\\Users\\enver\\.env dosyasında bulunamadı!");
    process.exit(1);
}

// Privy REST API için Basic Auth kimlik belgesi oluşturuluyor
const authToken = Buffer.from(PRIVY_APP_ID + ':' + PRIVY_APP_SECRET).toString('base64');

async function verifyPrivyConnection() {
    try {
        console.log("📡 Privy REST API ana sunucularına güvenli bağlantı isteği atılıyor...");
        
        // Privy API kullanıcı listesi sorgu ucu (Dokümantasyon Rest API standardı)
        const response = await axios.get('https://auth.privy.io/api/v1/apps/' + PRIVY_APP_ID + '/users', {
            headers: {
                'Authorization': 'Basic ' + authToken,
                'privy-app-id': PRIVY_APP_ID
            }
        });

        console.log("🟢 [SUCCESS] Privy REST API bağlantısı doğrulandı! Vantuz kontrol kalkanı aktif.");
        console.log("📊 Toplam Kayıtlı Kullanıcı Sayısı: " + (response.data.data ? response.data.data.length : 0));
        
    } catch (error) {
        console.error("🚨 [CONNECTION_FAIL] Privy API kimlik doğrulama hatası!");
        if (error.response) {
            console.error("Hata Kodu: " + error.response.status + " | Mesaj: " + JSON.stringify(error.response.data));
        } else {
            console.error("Detay: " + error.message);
        }
    }
}

verifyPrivyConnection();
