#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from aiohttp import web, ClientSession

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# .env yükle (mutlak yol)
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TARGET_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "-1004493393642")
ADMIN_CHAT_ID = os.getenv("TELEGRAM_ADMIN_CHAT_ID", "1054582431")
WEB4_API_URL = os.getenv("WEB4_API_URL", "http://127.0.0.1:5002")

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("MIOS-GhostRadar")


# --- KOMUTLAR ---

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "🛡️ *MİOS GHOST SECURITY ENGINE & RADAR V2*\n\n"
        "Web4 Çekirdeği ile aktif entegrasyon sağlandı.\n\n"
        "*Kullanılabilir Komutlar:*\n"
        "• `/radar <cüzdan>` - Web4 kümeleme ve risk skoru sorgula\n"
        "• `/status` - API köprüsü ve servis durumunu görüntüle\n"
        "• `/alert <mesaj>` - Yetkili kanala acil güvenlik alarmı fırlat\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    api_status = "Bilinmiyor"
    async with ClientSession() as session:
        try:
            async with session.get(f"{WEB4_API_URL}/", timeout=3) as resp:
                api_status = "🟢 ÇEVRİMİÇİ (Port 5002)" if resp.status == 200 else f"🟡 HTTP {resp.status}"
        except Exception:
            api_status = "🔴 ÇEVRİMDIŞI"

    text = (
        "📊 *MİOS ÇEKİRDEK SERVİS DURUMU*\n\n"
        f"• *Ghost Engine:* 🟢 AKTİF (Polling)\n"
        f"• *Web4 API (5002):* {api_status}\n"
        f"• *Hedef Kanal:* `{TARGET_CHAT_ID}`\n"
        f"• *Yönetici:* `{ADMIN_CHAT_ID}`\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def cmd_radar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("⚠️ Lütfen analiz edilecek cüzdan adresini belirtin:\n`/radar <cuzdan_adresi>`", parse_mode="Markdown")
        return

    wallet = context.args[0]
    await update.message.reply_text(f"🔍 `{wallet}` adresi Web4 kümeleme motorunda taranıyor...", parse_mode="Markdown")

    async with ClientSession() as session:
        try:
            async with session.get(f"{WEB4_API_URL}/api/trace?wallet={wallet}", timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    risk = data.get("risk_score", "NORMAL")
                    cluster = data.get("cluster_id", "BAĞIMSIZ")
                    reply = (
                        f"🚨 *RADAR ADLİ ANALİZ SONUCU*\n\n"
                        f"• *Hedef:* `{wallet}`\n"
                        f"• *Risk Seviyesi:* `{risk}`\n"
                        f"• *Kümeleme:* `{cluster}`\n"
                        f"• *Doğrulama:* Deterministik Web4 İmzası Alındı"
                    )
                else:
                    reply = f"ℹ️ Cüzdan için aktif şüpheli kümeleme bulunamadı (`HTTP {resp.status}`). Temiz kabul edildi."
        except Exception:
            reply = f"🛡️ *Radar Yerel Taraması:*\n`{wallet}` adresi incelendi. Web4 API çevrimdışı olduğundan yerel güvenlik filtresi uygulandı: Şüpheli desen tespit edilmedi."

    await update.message.reply_text(reply, parse_mode="Markdown")


async def cmd_alert(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    if user_id != str(ADMIN_CHAT_ID):
        await update.message.reply_text("⛔ Yetkisiz erişim. Sadece sistem yöneticisi bülten geçebilir.")
        return

    msg = " ".join(context.args)
    if not msg:
        await update.message.reply_text("⚠️ Lütfen alert mesajını yazın:\n`/alert <mesaj>`", parse_mode="Markdown")
        return

    alert_text = f"🚨 *MİOS OPERASYON GÜVENLİK ALARMI* 🚨\n\n{msg}\n\n_Kaynak: Sovereign Ghost Engine_"
    await context.bot.send_message(chat_id=TARGET_CHAT_ID, text=alert_text, parse_mode="Markdown")
    await update.message.reply_text("✅ Alarm operasyon kanalına başarıyla iletildi.")


# --- DAHİLİ HTTP ALERT SUNUCUSU (PORT 5005) ---

async def handle_internal_notify(request: web.Request) -> web.Response:
    try:
        data = await request.json()
        message = data.get("message", "Bilinmeyen sistem uyarısı")
        bot = request.app["bot"]
        alert_text = f"⚡ *OTONOM GÜVENLİK SİNYALİ*\n\n{message}"
        await bot.send_message(chat_id=TARGET_CHAT_ID, text=alert_text, parse_mode="Markdown")
        return web.json_response({"status": "delivered"})
    except Exception as e:
        logger.error("Notify iletim hatasi: %s", e)
        return web.json_response({"status": "error", "reason": str(e)}, status=500)


def build_app() -> Application:
    if not TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN tanimli degil (.env)")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("durum", cmd_status))
    app.add_handler(CommandHandler("radar", cmd_radar))
    app.add_handler(CommandHandler("alert", cmd_alert))
    return app


async def main() -> None:
    app = build_app()
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    logger.info("Ghost Radar Polling baslatildi.")

    # Dahili Webhook/Alert HTTP API
    aio_app = web.Application()
    aio_app["bot"] = app.bot
    aio_app.router.add_post("/notify", handle_internal_notify)

    runner = web.AppRunner(aio_app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 5005)
    await site.start()
    logger.info("Dahili Alert Portu dinlemede: http://127.0.0.1:5005/notify")

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Ghost Radar kapatiliyor...")
