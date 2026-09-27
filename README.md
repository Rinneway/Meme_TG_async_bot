# 🤖 Async Memes Telegram Bot

Асинхронный Telegram-бот, который умеет искать и отправлять случайные мемы по темам, а также генерировать и переводить шутки на лету. 

🔗 **[НАЖМИТЕ ЗДЕСЬ, ЧТОБЫ ЗАПУСТИТЬ БОТА В TELEGRAM](https://t.me/riNN_dev_test_bot)**  

---

## ✨ Возможности

- 🖼 **Умный поиск мемов:** Распознает ключевые слова в сообщениях пользователя (например, "кот", "программирование", "python") и выдает релевантные мемы из Reddit через API.
- 😂 **Генератор шуток:** Получает случайные шутки и автоматически переводит их с английского на русский язык.
- 🌐 **Переключение языков:** Inline-кнопка позволяет мгновенно переключиться между русской и английской версиями одной и той же шутки без повторных запросов.
- 🔄 **Умные повторные попытки:** Если API не ответил или картинка не загрузилась, бот предложит попробовать снова через inline-кнопку, не заставляя пользователя ждать.

---

## 🛠 Технологический стек

- **Язык:** Python 3.14
- **Фреймворк:** [aiogram 3.x](https://docs.aiogram.dev/) (асинхронная работа с Telegram API)
- **Сетевые запросы:** `aiohttp` (глобальная сессия для оптимизации)
- **Конфигурация:** `python-dotenv`
- **Внешние API:** 
  - `meme-api.com` (получение мемов из Reddit)
  - `v2.jokeapi.dev` (база шуток)
  - `mymemory.translated.net` (бесплатный перевод текста)

---

## 📂 Структура проекта

Проект разделен на модули для соблюдения принципов чистой архитектуры (Separation of Concerns):

```text
├── main.py                 # Точка входа (запуск бота)
├── bot.py                  # Создание Bot и Dispatcher, регистрация роутеров
├── config.py               # Конфигурация (токен бота)
├── state.py                # Глобальное состояние (сессия, кэш)
├── constants.py            # Константы и CallbackData классы
├── filters.py              # Алиасы для CallbackData
├── requirements.txt        # Зависимости Python
├── versel.json             # Параметры для Vercel
│
├── api/
|   └── index.py                # Инициализация бота через webhooks
|
├── databases/
│   ├── __init__.py         # Импорт всех функций и моделей
│   ├── bot.bd              # база данных со всеми обработками
│   ├── databases.py        # основная логика работы с бд
│   └── models.py           # модели SQLAlchemy
|
├── handlers/               # Обработчики сообщений и команд
│   ├── __init__.py         # Импорт роутеров
│   ├── commands.py         # /start, /help
│   ├── messages.py         # Обработка текста
│   └── callbacks.py        # Inline-кнопки
│
├── services/               # Внешние сервисы и API
│   ├── __init__.py         # Пустой файл
│   ├── api.py              # Запросы к API (мемы, шутки, перевод)
│   └── keyboards.py        # Генерация inline-клавиатур
│
└── utils/                  # Вспомогательные функции
    ├── __init__.py         # Пустой файл
    └── helpers.py          # find_topic, send_joke, send_meme
```

## 📊 Архитектура БД

```text
categories (категории)
├── id (INTEGER PRIMARY KEY)
├── name (TEXT UNIQUE)         # Пример: "cats", "programming"
├── display_name (TEXT)        # Пример: "Коты"
└── is_active (BOOLEAN)        -- можно отключать категории

keywords (ключевые слова)
├── id (INTEGER PRIMARY KEY)
── category_id (INTEGER FK)
└── keyword (TEXT)             # Пример: "кот", "программ"

subreddits (сабреддиты)
├── id (INTEGER PRIMARY KEY)
├── category_id (INTEGER FK)
└── name (TEXT)                # Пример: "catmemes", "ProgrammerHumor"
```
