from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from state import user_joke_cache
from filters import RetryMemeCD, RetryJokeCD, ToggleLangCD

main_menu_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="мем"), KeyboardButton(text="шутка")]
], resize_keyboard=True, input_field_placeholder="Выберите действие или напишите.")


def get_joke_keyboard(user_id: int):
    buttons = [
        [InlineKeyboardButton(text="🔄 Еще шутку", callback_data=RetryJokeCD().pack())]
    ]

    if user_id in user_joke_cache:
        current_lang = user_joke_cache[user_id]["current"]
        if current_lang == "ru":
            buttons.append([InlineKeyboardButton(text="🇬🇧 English", callback_data=ToggleLangCD().pack())])
        else:
            buttons.append([InlineKeyboardButton(text="🇷🇺 Русский", callback_data=ToggleLangCD().pack())])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_meme_keyboard(topic: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" Еще мем", callback_data=RetryMemeCD(topic=topic).pack())]
    ])