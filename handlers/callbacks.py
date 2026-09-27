import asyncio

from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.enums import ChatAction

from state import user_joke_cache
from services.keyboards import get_joke_keyboard
from utils.helpers import send_joke, send_meme
from filters import RetryJokeCD, RetryMemeCD, ToggleLangCD

router = Router()


@router.callback_query(RetryJokeCD.filter())
async def cb_retry_joke(callback: CallbackQuery):
    await callback.answer()
    await send_joke(callback.message, is_callback=True)


@router.callback_query(ToggleLangCD.filter())
async def cb_toggle_lang(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    chat_id = callback.message.chat.id

    if user_id not in user_joke_cache:
        await callback.message.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        await asyncio.sleep(0.3)
        await callback.message.edit_text("Кэш очищен. Запрашиваю новую шутку...")
        await send_joke(callback.message, is_callback=True)
        return

    cache = user_joke_cache[user_id]

    await callback.message.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await asyncio.sleep(0.3)

    if cache["current"] == "ru":
        cache["current"] = "en"
        await callback.message.edit_text(
            text=f"🇬 *Original:*\n\n{cache['en']}",
            parse_mode="Markdown",
            reply_markup=get_joke_keyboard(user_id)
        )
    else:
        cache["current"] = "ru"
        await callback.message.edit_text(
            text=cache["ru"],
            reply_markup=get_joke_keyboard(user_id)
        )


@router.callback_query(RetryMemeCD.filter())
async def cb_retry_meme(callback: CallbackQuery, callback_data: RetryMemeCD):
    await callback.answer()
    await send_meme(callback.message, callback_data.topic)