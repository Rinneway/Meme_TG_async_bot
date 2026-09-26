import asyncio
import random
import aiohttp
import logging
from urllib.parse import quote

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ChatAction
from aiogram.types import Message, URLInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.filters.callback_data import CallbackData

from config import BOT_TOKEN

dp = Dispatcher()


# Callback данные для inline кнопок
class RetryMemeCD(CallbackData, prefix="rm"):
    topic: str


class RetryJokeCD(CallbackData, prefix="rj"):
    pass


class ToggleLangCD(CallbackData, prefix="tl"):
    pass


# Глобальная сессия для оптимизации скорости
session: aiohttp.ClientSession | None = None

# Кэш для хранения последней шутки пользователя: {user_id: {"en": "...", "ru": "...", "current": "ru"}}
user_joke_cache = {}

MEME_KEYWORDS = {
    "cats": ["кот", "кошк", "котик", "котэ", "cat", "кис", "мяу"],
    "programming": ["программ", "код", "developer", "разработ", "python",
                    "питон", "прог", "it", "ит", "баг", "дедлайн"],
    "other": ["друг", "разн", "мем", "мемасик", "прикол", "other"],
}

TOPIC_NAMES = {
    "cats": "коты",
    "programming": "программирование",
    "other": "другое",
}

SUBREDDITS = {
    "cats": ["catmemes", "CatHumor", "FunnyCats"],
    "programming": ["ProgrammerHumor", "ProgrammerDadJokes", "codingmemes"],
    "other": ["memes", "dankmemes", "funny"],
}


async def get_meme_from_api(topic: str):
    subreddits = SUBREDDITS.get(topic, SUBREDDITS["other"])
    subreddit = random.choice(subreddits)
    url = f"https://meme-api.com/gimme/{subreddit}"

    try:
        async with session.get(url, timeout=5) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            return {
                "url": data.get("url"),
                "subreddit": data.get("subreddit", subreddit)
            }
    except Exception as e:
        logging.error(f"Meme fetch error: {e}")
        return None


def find_topic(text: str):
    text_lower = text.lower()
    for topic, keywords in MEME_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return topic
    return None


async def get_joke_from_api():
    url = "https://v2.jokeapi.dev/joke/Any?lang=en&blacklistFlags=nsfw,religious,political,racist,sexist,explicit"
    try:
        async with session.get(url, timeout=5) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            if data.get("error"):
                return None

            if data.get("type") == "single":
                return data.get("joke")
            elif data.get("type") == "twopart":
                return f"{data.get('setup')}\n\n{data.get('delivery')}"
            return None
    except Exception as e:
        logging.error(f"Joke fetch error: {e}")
        return None


async def translate_text(text: str):
    encoded_text = quote(text)
    url = f"https://api.mymemory.translated.net/get?q={encoded_text}&langpair=en|ru"
    try:
        async with session.get(url, timeout=5) as resp:
            if resp.status != 200:
                return text
            data = await resp.json()
            translated = data.get("responseData", {}).get("translatedText")
            return translated if translated else text
    except Exception as e:
        logging.error(f"Translate error: {e}")
        return text


def get_joke_keyboard(user_id: int):
    buttons = []

    if user_id in user_joke_cache:
        current_lang = user_joke_cache[user_id]["current"]
        if current_lang == "ru":
            buttons.append([InlineKeyboardButton(text="🇬🇧 English", callback_data=ToggleLangCD().pack())])
        else:
            buttons.append([InlineKeyboardButton(text="🇷🇺 Русский", callback_data=ToggleLangCD().pack())])

    buttons.append([InlineKeyboardButton(text="🔄 Еще шутку", callback_data=RetryJokeCD().pack())])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_meme_keyboard(topic: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Еще мем", callback_data=RetryMemeCD(topic=topic).pack())]
    ])


async def send_joke(message: Message, is_callback: bool = False):
    user_id = message.from_user.id
    chat_id = message.chat.id

    for _ in range(3):
        joke_en = await get_joke_from_api()
        if joke_en:
            joke_ru = await translate_text(joke_en)

            user_joke_cache[user_id] = {
                "en": joke_en,
                "ru": joke_ru,
                "current": "ru"
            }

            await message.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
            await asyncio.sleep(0.3)
            await message.answer(joke_ru, reply_markup=get_joke_keyboard(user_id))
            return

    await message.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await asyncio.sleep(0.3)

    kb = get_joke_keyboard(user_id) if is_callback else InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Повторить", callback_data=RetryJokeCD().pack())]
    ])
    await message.answer("😕 Не удалось получить шутку. Попробуй ещё раз!", reply_markup=kb)


async def send_meme(message: Message, topic: str, is_callback: bool = False):
    chat_id = message.chat.id

    for _ in range(3):
        meme_data = await get_meme_from_api(topic)
        if meme_data and meme_data.get("url"):
            try:
                await message.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)
                await asyncio.sleep(0.3)

                await message.answer_photo(
                    photo=URLInputFile(url=meme_data["url"]),
                    caption=f"Мем по теме: {TOPIC_NAMES[topic]}",
                    reply_markup=get_meme_keyboard(topic)
                )
                return
            except Exception as e:
                logging.error(f"Meme send error: {e}")
                continue

    await message.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await asyncio.sleep(0.3)

    kb = get_meme_keyboard(topic) if is_callback else InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Повторить", callback_data=RetryMemeCD(topic=topic).pack())]
    ])
    await message.answer(f"😕 Не удалось загрузить мем. Попробуй ещё раз!", reply_markup=kb)


@dp.message(CommandStart(deep_link=True))
async def cmd_start(message: Message, command: CommandObject):
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    await asyncio.sleep(0.3)
    await message.answer(
        f"Привет! Ты пришел от @{command.args}. \n"
        "Я показываю мемы и шутки. Напиши: «мем про программирование», «коты» или «шутка»."
    )


@dp.message(CommandStart())
async def cmd_start_default(message: Message):
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    await asyncio.sleep(0.3)
    await message.answer(
        "Привет! Я показываю мемы и шутки. \n"
        "Напиши: «мем про программирование», «коты» или «шутка»."
    )


@dp.message(Command("help"))
async def cmd_help(message: Message):
    topics = ", ".join(TOPIC_NAMES.values())
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    await asyncio.sleep(0.3)
    await message.answer(
        f"Привет, {message.from_user.full_name}!\n"
        f"Доступные тематики мемов: {topics}.\n"
        "Также можно написать «шутка», «прикол» или «анекдот»."
    )


@dp.message(F.text)
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


@dp.callback_query(RetryJokeCD.filter())
async def cb_retry_joke(callback: CallbackQuery):
    await callback.answer()
    await send_joke(callback.message, is_callback=True)


@dp.callback_query(ToggleLangCD.filter())
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

    if cache["current"] == "ru":
        cache["current"] = "en"
        await callback.message.edit_text(
            text=f"🇬🇧 *Original:*\n\n{cache['en']}",
            parse_mode="Markdown",
            reply_markup=get_joke_keyboard(user_id)
        )
    else:
        cache["current"] = "ru"
        await callback.message.edit_text(
            text=cache["ru"],
            reply_markup=get_joke_keyboard(user_id)
        )


@dp.callback_query(RetryMemeCD.filter())
async def cb_retry_meme(callback: CallbackQuery, callback_data: RetryMemeCD):
    await callback.answer()
    await send_meme(callback.message, callback_data.topic, is_callback=True)


async def main():
    global session
    bot = Bot(token=BOT_TOKEN)

    async with aiohttp.ClientSession() as session:
        logging.info("Bot started successfully with session")
        await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Shutting down successfully")