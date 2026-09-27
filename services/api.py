import re
import random
import logging
import aiohttp
from urllib.parse import quote

from databases.databases import find_category_by_text

logger = logging.getLogger(__name__)


async def get_meme_from_api(text: str):
    """
    Получает мем по тексту сообщения.
    Автоматически определяет категорию через БД.
    """
    try:
        # Ищем категорию в БД
        category = await find_category_by_text(text)

        if not category:
            logger.warning(f"No category found for text: {text}")
            return None

        # Выбираем случайный сабреддит из категории
        subreddit = random.choice(category["subreddits"])
        url = f"https://meme-api.com/gimme/{subreddit}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status != 200:
                    return None

                data = await resp.json()

                if not data or not isinstance(data, dict):
                    return None

                meme_url = data.get("url")
                if not meme_url:
                    return None

                return {
                    "url": meme_url,
                    "subreddit": subreddit,
                    "category_name": category["display_name"]
                }
    except Exception as e:
        logger.error(f"Meme fetch error: {e}")
        return None


async def get_joke_from_api():
    try:
        url = "https://v2.jokeapi.dev/joke/Any?lang=en"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status != 200:
                    return None

                data = await resp.json()

                if not data or not isinstance(data, dict):
                    return None

                if data.get("error"):
                    return None

                joke = None
                if data.get("type") == "single":
                    joke = data.get("joke")
                elif data.get("type") == "twopart":
                    setup = data.get("setup")
                    delivery = data.get("delivery")
                    if setup and delivery:
                        joke = f"{setup}\n\n{delivery}"

                if joke:
                    joke = clean_joke_text(joke)

                return joke
    except Exception as e:
        logger.error(f"Joke fetch error: {e}")
        return None


async def translate_text(text: str):
    """Переводит текст с английского на русский."""
    try:
        if not text:
            return text

        encoded_text = quote(text)
        url = f"https://api.mymemory.translated.net/get?q={encoded_text}&langpair=en|ru"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status != 200:
                    return text

                data = await resp.json()

                if not data or not isinstance(data, dict):
                    return text

                response_data = data.get("responseData")
                if not response_data or not isinstance(response_data, dict):
                    return text

                translated = response_data.get("translatedText")
                return translated if translated else text
    except Exception as e:
        logger.error(f"Translate error: {e}")
        return text


def clean_joke_text(text: str) -> str:
    """Очищает шутку от мусорных символов в конце."""
    if not text:
        return text

    # Ищем первое вхождение 3+ специальных символов подряд (признак мусора)
    # Примеры мусора: (#$JF(#)$(@J#(), !*FNIN!, ##@
    match = re.search(r'[!@#$%^&*()_+\-=\[\]{};\'"\\|,.<>/?]{3,}', text)

    if match:
        # Обрезаем текст до начала мусора + убираем пробелы в конце
        cleaned = text[:match.start()].strip()
        # Убираем висящие предлоги/союзы в конце
        cleaned = re.sub(r'\s+(и|а|но|или|что|чтобы|потому)\s*$', '', cleaned)
        return cleaned

    return text