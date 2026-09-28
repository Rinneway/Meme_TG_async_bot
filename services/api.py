import logging
import aiohttp
from urllib.parse import quote

from databases import find_category_by_text
from services.pinterest_client import get_random_pin
from constants import PINTEREST_QUERIES

logger = logging.getLogger(__name__)


async def get_meme_from_api(text: str):
    """получает мемы по api"""
    try:
        # Ищем категорию в БД
        category = await find_category_by_text(text)

        if not category:
            logger.warning(f"No category found for text: {text}")
            return None

        category_name = category["name"]

        # Берем запрос для Pinterest (или имя категории как запасной вариант)
        search_query = PINTEREST_QUERIES.get(category_name, f"{category_name} funny meme")

        pin = await get_random_pin(search_query)

        if not pin or not pin.get("url"):
            logger.warning(f"No pins found for query: {search_query}")
            return None

        return {
            "url": pin["url"],
            "name": category_name,
            "category_name": category["display_name"]
        }

    except Exception as e:
        logger.error(f"Meme fetch error: {e}")
        return None


async def get_joke_from_api():
    """Получает случайную шутку на английском."""
    try:
        url = "https://v2.jokeapi.dev/joke/Any?lang=en&blacklistFlags=nsfw,religious,political,racist,sexist,explicit"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status != 200:
                    return None

                data = await resp.json()
                if not data or not isinstance(data, dict) or data.get("error"):
                    return None

                if data.get("type") == "single":
                    return data.get("joke")
                elif data.get("type") == "twopart":
                    setup = data.get("setup")
                    delivery = data.get("delivery")
                    if setup and delivery:
                        return f"{setup}\n\n{delivery}"
                return None
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
