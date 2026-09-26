from aiogram.filters.callback_data import CallbackData

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
    "cats": ["catmemes", "CatHumor", "cats"],
    "programming": ["ProgrammerHumor", "ProgrammerDadJokes", "codingmemes"],
    "other": ["memes", "dankmemes", "funny"],
}


class RetryMemeCD(CallbackData, prefix="rm"):
    topic: str


class RetryJokeCD(CallbackData, prefix="rj"):
    pass


class ToggleLangCD(CallbackData, prefix="tl"):
    pass