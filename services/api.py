import random
import logging
import asyncio
from urllib.parse import quote

from state import session
from constants import SUBREDDITS


async def get_meme_from_api(topic: str):
    subreddits = SUBREDDITS.get(topic, SUBREDDITS["other"])
    subreddit = random.choice(subreddits)
    url = f"https://meme-api.com/gimme/{subreddit}"

    try:
        async with session.get(url, timeout=5) as resp:
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
    url = "https://v2.jokeapi.dev/joke/Any?lang=en&blacklistFlags=nsfw,religious,political,racist,sexist,explicit"
    try:
        async with session.get(url, timeout=5) as resp:
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
    if not text:
        return text

    encoded_text = quote(text)
    url = f"https://api.mymemory.translated.net/get?q={encoded_text}&langpair=en|ru"
    try:
        async with session.get(url, timeout=5) as resp:
            if resp.status != 200:
                return text

            data = await resp.json()

            if not data or not isinstance(data, dict):
                return text

            translated = data.get("responseData", {}).get("translatedText")
            return translated if translated else text
    except Exception as e:
        logging.error(f"Translate error: {e}")
        return text