from aiogram.filters.callback_data import CallbackData


admins = [1767307608]

# Ключевые слова оптимизированы: только частотные корни и реальные запросы пользователей
MEME_KEYWORDS = {
    "cats": [
        "кот", "кошк", "котик", "котэ", "котят", "кис", "кисул", "мяу", "мур",
        "cat", "cats", "meow", "chonk"
    ],
    "programming": [
        "программ", "код", "developer", "разработ", "python", "питон", "прог",
        "it", "ит", "айти", "баг", "фича", "дедлайн", "джун", "сеньор", "мидл",
        "git", "гит", "верст", "фронт", "бэк", "сервер", "комп", "ноут", "java", "js"
    ],
    "gaming": [
        "игр", "game", "gaming", "геймер", "дота", "cs", "csgo", "майнкрафт",
        "minecraft", "gta", "роблокс", "roblox", "steam", "стим", "playstation",
        "xbox", "nintendo", "катк", "нуб", "скилл", "пати", "геймпад"
    ],
    "anime": [
        "аним", "anime", "манг", "manga", "отаку", "наруто", "ванпис", "one piece",
        "геншин", "genshin", "вайфу", "тян", "кун", "косплей", "cosplay", "исэкай"
    ],
    "work": [
        "работ", "офис", "начальник", "босс", "коллега", "зарплат", "дедлайн",
        "увольнен", "собес", "резюме", "удаленк", "фриланс", "корпорат", "пятниц",
        "понедельник", "выгоран", "отпуск"
    ],
    "study": [
        "школ", "универ", "университет", "колледж", "студент", "школьник", "ученик",
        "экзамен", "сессия", "зачет", "дз", "домашк", "пара", "лекц", "диплом", "физик", "математ", "учеб"
    ],
    "other": [
        "мем", "мемас", "прикол", "шутк", "жиза", "треш", "кринж", "ржака", "угар",
        "смешн", "funny", "dank", "random", "разн", "друг", "просто", "любой"
    ],
}

TOPIC_NAMES = {
    "cats": "Коты",
    "programming": "Программирование",
    "gaming": "Игры",
    "anime": "Аниме",
    "work": "Работа и офис",
    "study": "Учеба",
    "other": "Разное",
}

PINTEREST_QUERIES = {
    "cats": "funny cats memes cute",
    "programming": "programming humor coding memes developer",
    "gaming": "gaming memes funny gamer video games",
    "anime": "anime memes funny manga otaku",
    "work": "office humor work memes funny corporate",
    "study": "student life study memes funny college",
    "other": "funny memes dank random humor",
}

# Оставляем как резервный вариант (fallback), если Pinterest не сработает
SUBREDDITS = {
    "cats": ["catmemes", "cathumor", "cats", "catsareliquid", "chonkers"],
    "programming": ["programmerhumor", "programmerdadjokes", "codingmemes", "softwaregore", "techsupportgore"],
    "gaming": ["gamingmemes", "gaming", "games", "gamephysics", "pcmasterrace"],
    "anime": ["animemes", "anime", "manga", "wholesomeanimemes", "goodanimemes"],
    "work": ["antiwork", "workplacehumor", "office", "coworkerstories", "talesfromthejob"],
    "study": ["schoolmemes", "college", "science", "math", "engineering"],
    "other": ["memes", "dankmemes", "wholesomememes", "me_irl"],
}


class RetryMemeCD(CallbackData, prefix="rm"):
    topic: str


class ToggleLangCD(CallbackData, prefix="tl"):
    pass