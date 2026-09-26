from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import commands_router, messages_router, callbacks_router

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(commands_router)
dp.include_router(messages_router)
dp.include_router(callbacks_router)