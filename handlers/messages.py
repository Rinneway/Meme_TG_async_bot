import asyncio

from aiogram import Router, F
from aiogram.types import Message
from aiogram.enums import ChatAction

from utils.helpers import find_topic, send_joke, send_meme

router = Router()


@router.message(F.text)
async def echo(message: Message):
    text = message.text.lower()

    if "шутка" in text or "прикол" in text or "анекдот" in text:
        await send_joke(message)
        return

    topic = find_topic(text)
    if topic:
        await send_meme(message, topic)
        return

    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    await asyncio.sleep(0.3)
    await message.answer("Неизвестная команда. Напиши /help, чтобы узнать, что я умею.")