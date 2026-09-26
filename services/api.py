import random
import logging
import aiohttp
from urllib.parse import quote

from constants import SUBREDDITS


async def get_meme_from_api(topic: str):
    try:
        subreddits = SUBREDDITS.get(topic, SUBREDDITS["other"])
        if not subreddits:
            return None

        subreddit = random.choice(subreddits)
        url = f"https://meme-api.com/gimme/{subreddit}"

        # Создаём локальную сессию для каждого запроса
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
                    "subreddit": data.get("subreddit", subreddit)
                }
    except Exception as e:
        logging.error(f"Meme fetch error: {e}")
        return None


async def get_joke_from_api():
    try:
        url = "https://v2.jokeapi.dev/joke/Any?lang=en&blacklistFlags=nsfw,religious,political,racist,sexist,explicit"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status != 200:
                    return None

                data = await resp.json()

                if not data or not isinstance(data, dict):
                    return None

                if data.get("error"):
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
        logging.error(f"Joke fetch error: {e}")
        return None


async def translate_text(text: str):
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
        logging.error(f"Translate error: {e}")
        return text