import asyncio
import logging

from aiogram.types import Message, URLInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ChatAction

from services.api import get_meme_from_api, get_joke_from_api, translate_text
from services.keyboards import get_joke_keyboard, get_meme_keyboard
from filters import RetryJokeCD
from state import user_joke_cache

logger = logging.getLogger(__name__)


async def send_joke(message: Message, is_callback: bool = False):
    """Отправляет шутку пользователю."""
    chat_id = message.chat.id
    user_id = message.from_user.id

    for attempt in range(3):
        await message.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

        joke_en = await get_joke_from_api()
        if joke_en:
            joke_ru = await translate_text(joke_en)

            user_joke_cache[user_id] = {
                "en": joke_en,
                "ru": joke_ru,
                "current": "ru"
            }

            await asyncio.sleep(0.3)
            await message.answer(joke_ru, reply_markup=get_joke_keyboard(user_id))
            return

    await asyncio.sleep(0.3)
    kb = get_joke_keyboard(user_id) if is_callback else InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" Повторить", callback_data=RetryJokeCD().pack())]
    ])
    await message.answer("😕 Не удалось получить шутку. Попробуй ещё раз!", reply_markup=kb)


async def send_meme(message: Message, text: str):
    """Отправляет мем по тексту (категория определяется через БД)."""
    chat_id = message.chat.id

    for attempt in range(3):
        await message.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)

        meme_data = await get_meme_from_api(text)
        if meme_data and meme_data.get("url"):
            try:
                await asyncio.sleep(0.3)
                await message.answer_photo(
                    photo=URLInputFile(url=meme_data["url"]),
                    caption=f"Мем по теме: {meme_data['category_name']}",
                    reply_markup=get_meme_keyboard(meme_data['subreddit'])
                )
                return
            except Exception as e:
                logger.error(f"Meme send error: {e}")
                continue

    await asyncio.sleep(0.3)
    await message.answer("😕 Не удалось загрузить мем. Попробуй ещё раз!")
