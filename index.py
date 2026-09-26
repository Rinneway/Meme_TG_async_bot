import os
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from aiogram.types import Update
import aiohttp

# Добавляем корень проекта в пути, чтобы импорты работали
sys.path.append(str(os.path.join(str(os.path.dirname(__file__)), '..')))

from config import BOT_TOKEN
from handlers import commands_router, messages_router, callbacks_router
import state

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Подключаем роутеры
dp.include_router(commands_router)
dp.include_router(messages_router)
dp.include_router(callbacks_router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: инициализация при запуске
    state.session = aiohttp.ClientSession()
    logging.info("Aiohttp session created")
    yield
    # Shutdown: очистка при завершении
    if state.session and not state.session.closed:
        await state.session.close()
        logging.info("Aiohttp session closed")


# Создаем FastAPI приложение с lifespan
app = FastAPI(lifespan=lifespan)


@app.post("/")
async def webhook(request: Request):
    """Обработчик входящих обновлений от Telegram"""
    try:
        data = await request.json()
        update = Update.model_validate(data, context=bot)
        await dp.feed_webhook_update(bot, update)
        return {"ok": True}
    except Exception as e:
        logging.error(f"Webhook error: {e}", exc_info=True)
        return {"ok": False}


@app.get("/")
async def health_check():
    """Проверка: если открыть ссылку в браузере, увидим это"""
    return {"status": "ok", "message": "Bot is running on Vercel!"}