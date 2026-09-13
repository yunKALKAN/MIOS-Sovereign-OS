"""MucizeWork Telegram bot — webhook veya polling."""

import logging
import os
from pathlib import Path

from aiohttp import web
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_PATH)

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("mucizework-telegram")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "").strip().rstrip("/")
PORT = int(os.getenv("TELEGRAM_WEBHOOK_PORT", os.getenv("PORT", "8443")))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "MucizeWork bot aktif. /durum ile baglanti modunu gorebilirsiniz."
    )


async def durum(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    mod = "webhook" if WEBHOOK_URL else "polling"
    await update.message.reply_text(f"Mod: {mod}\nWebhook: {WEBHOOK_URL or '(yok)'}")


def build_app() -> Application:
    if not TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN tanimli degil (.env)")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("durum", durum))
    return app


async def health(_request: web.Request) -> web.Response:
    return web.json_response({"status": "ok", "mod": "webhook" if WEBHOOK_URL else "polling"})


async def run_webhook() -> None:
    app = build_app()
    await app.initialize()
    await app.start()

    webhook_path = "/webhook"
    full_url = f"{WEBHOOK_URL}{webhook_path}"
    await app.bot.set_webhook(
        url=full_url,
        allowed_updates=Update.ALL_TYPES,
    )
    logger.info("Webhook ayarlandi: %s", full_url)

    aio_app = web.Application()
    aio_app.router.add_get("/health", health)
    aio_app.router.add_post(webhook_path, app.webhook_handler())
    runner = web.AppRunner(aio_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info("HTTP dinleniyor: 0.0.0.0:%s", PORT)

    import asyncio

    await asyncio.Event().wait()


def run_polling() -> None:
    logger.info("WEBHOOK_URL yok — polling modunda baslatiliyor")
    app = build_app()
    app.run_polling(allowed_updates=Update.ALL_TYPES)


def main() -> None:
    if WEBHOOK_URL:
        import asyncio

        asyncio.run(run_webhook())
    else:
        run_polling()


if __name__ == "__main__":
    main()