import asyncio

from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.enums import ChatAction

from state import user_joke_cache, clear_user_joke_cache
from services.keyboards import get_joke_keyboard
from utils.helpers import send_meme
from filters import RetryMemeCD, ToggleLangCD

router = Router()


@router.callback_query(ToggleLangCD.filter())
async def cb_toggle_lang(callback: CallbackQuery):
    await callback.answer()
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id

    if message_id not in user_joke_cache:
        await callback.message.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        await asyncio.sleep(0.3)
        await callback.message.edit_text("Кэш был очищен. Запросите новую шутку.")
        clear_user_joke_cache()
        return

    cache = user_joke_cache[message_id]

    await callback.message.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await asyncio.sleep(0.3)

    if cache["current"] == "ru":
        cache["current"] = "en"
        await callback.message.edit_text(
            text=f"🇬 *Original:*\n\n{cache['en']}",
            parse_mode="Markdown",
            reply_markup=get_joke_keyboard(message_id)
        )
    else:
        cache["current"] = "ru"
        await callback.message.edit_text(
            text=cache["ru"],
            reply_markup=get_joke_keyboard(message_id)
        )


@router.callback_query(RetryMemeCD.filter())
async def cb_retry_meme(callback: CallbackQuery, callback_data: RetryMemeCD):
    await callback.answer()
    await send_meme(callback.message, callback_data.topic)
