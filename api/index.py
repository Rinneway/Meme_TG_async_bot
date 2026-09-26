import os
import sys
import logging
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from aiogram.types import Update

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from config import BOT_TOKEN
from handlers import commands_router, messages_router, callbacks_router
from databases.databases import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)  
dp = Dispatcher()

dp.include_router(commands_router)
dp.include_router(messages_router)
dp.include_router(callbacks_router)

app = FastAPI()


@app.on_event("startup")
async def startup():
    """Инициализация БД при запуске."""
    await init_db()
    logger.info("Database initialized with SQLAlchemy")


@app.get("/")
async def health_check():
    return {"status": "ok", "message": "Bot is running on Vercel!"}


@app.post("/")
async def webhook(request: Request):
    try:
        data = await request.json()
        update = Update.model_validate(data, context={"bot": bot})
        await dp.feed_webhook_update(bot, update)
        return {"ok": True}
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}