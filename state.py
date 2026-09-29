import aiohttp

session: aiohttp.ClientSession | None = None
user_joke_cache = {}


def clear_user_joke_cache():
    global user_joke_cache
    user_joke_cache.clear()