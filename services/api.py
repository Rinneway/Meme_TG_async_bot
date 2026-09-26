import random
import logging
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
            return {
                "url": data.get("url"),
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