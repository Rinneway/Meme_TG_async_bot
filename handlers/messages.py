from aiogram import Router, F
from aiogram.types import Message

from utils.helpers import send_joke, send_meme

router = Router()


@router.message(F.text)
async def echo(message: Message):
    text = message.text.lower()

    if "шутка" in text or "прикол" in text or "анекдот" in text:
        await send_joke(message)
        return

    # БД сама определит категорию по тексту
    await send_meme(message, text)