import aiohttp

session: aiohttp.ClientSession | None = None
user_joke_cache = {}