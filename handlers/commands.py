import asyncio
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.enums import ChatAction

from constants import admins
from databases import get_all_active_categories, add_category, delete_category, get_category_stats
from services.keyboards import main_menu_keyboard

router = Router()


@router.message(CommandStart(deep_link=True))
async def cmd_start(message: Message, command: CommandObject):
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    await asyncio.sleep(0.3)
    await message.answer(
        f"Привет! Ты пришел от @{command.args}. \n"
        "Я показываю мемы и шутки. Напиши: «мем про программирование», «коты» или «шутка».",
        reply_markup=main_menu_keyboard
    )


@router.message(CommandStart())
async def cmd_start_default(message: Message):
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    await asyncio.sleep(0.3)
    await message.answer(
        "Привет! Я показываю мемы и шутки. \n"
        "Напиши: «мем про программирование», «коты» или «шутка».",
        reply_markup=main_menu_keyboard
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

    categories = await get_all_active_categories()
    topics = ", ".join([cat["display_name"] for cat in categories])

    await asyncio.sleep(0.1)
    await message.answer(
        f"Привет, {message.from_user.full_name}!\n"
        f"Доступные тематики мемов: {topics}.\n"
        "Также можно написать «шутка», «прикол» или «анекдот»."
    )


@router.message(Command("categories"))
async def cmd_categories(message: Message):
    """Показать все активные категории."""
    if message.from_user.id not in admins:
        await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
        await asyncio.sleep(0.3)
        await message.answer("Нет нужных прав доступа.")
        return

    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    categories = await get_all_active_categories()

    text = "📋 Активные категории:\n\n"
    for cat in categories:
        text += f"• {cat['display_name']} (`{cat['name']}`)\n"

    await asyncio.sleep(0.1)
    await message.answer(text)


@router.message(Command("add_category"))
async def cmd_add_category(message: Message):
    """
    Добавить категорию. Формат:
    /add_category name|display_name|keyword1,keyword2|sub1,sub2
    """
    if message.from_user.id not in admins:
        await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
        await asyncio.sleep(0.3)
        await message.answer("Нет нужных прав доступа.")
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
        await asyncio.sleep(0.3)
        await message.answer("Использование: /add_category name|display|kw1,kw2|sub1,sub2")
        return

    parts = args[1].split("|")
    if len(parts) != 4:
        await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
        await asyncio.sleep(0.3)
        await message.answer("Неверный формат. Нужно 4 части через |")
        return

    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

    name, display_name, keywords_str, subreddits_str = parts
    keywords = [k.strip() for k in keywords_str.split(",")]
    subreddits = [s.strip() for s in subreddits_str.split(",")]

    success = await add_category(name, display_name, keywords, subreddits)
    await asyncio.sleep(0.1)

    if success:
        await message.answer(f"✅ Категория `{name}` добавлена!")
    else:
        await message.answer("❌ Ошибка при добавлении категории (возможно, уже существует)")


@router.message(Command("delete_category"))
async def cmd_delete_category(message: Message):
    """Удалить категорию по имени."""
    if message.from_user.id not in admins:
        await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
        await asyncio.sleep(0.3)
        await message.answer("Нет нужных прав доступа.")

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
        await asyncio.sleep(0.3)
        await message.answer("Использование: /delete_category name")
        return

    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

    name = args[1].strip()
    success = await delete_category(name)
    await asyncio.sleep(0.1)

    if success:
        await message.answer(f"✅ Категория `{name}` удалена!")
    else:
        await message.answer("❌ Категория не найдена")


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Показать статистику БД."""
    if message.from_user.id not in admins:
        await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
        await asyncio.sleep(0.3)
        await message.answer("Нет нужных прав доступа.")

    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

    stats = await get_category_stats()
    text = (
        "📊 Статистика базы данных:\n\n"
        f"• Категорий: {stats['categories']}\n"
        f"• Ключевых слов: {stats['keywords']}\n"
        f"• Сабреддитов: {stats['subreddits']}"
    )
    
    await asyncio.sleep(0.1)
    await message.answer(text)