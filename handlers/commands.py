import asyncio

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.enums import ChatAction

from constants import TOPIC_NAMES

router = Router()


@router.message(CommandStart(deep_link=True))
async def cmd_start(message: Message, command: CommandObject):
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    await asyncio.sleep(0.3)
    await message.answer(
        f"Привет! Ты пришел от @{command.args}. \n"
        "Я показываю мемы и шутки. Напиши: «мем про программирование», «коты» или «шутка»."
    )


@router.message(CommandStart())
async def cmd_start_default(message: Message):
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    await asyncio.sleep(0.3)
    await message.answer(
        "Привет! Я показываю мемы и шутки. \n"
        "Напиши: «мем про программирование», «коты» или «шутка»."
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    topics = ", ".join(TOPIC_NAMES.values())
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    await asyncio.sleep(0.3)
    await message.answer(
        f"Привет, {message.from_user.full_name}!\n"
        f"Доступные тематики мемов: {topics}.\n"
        "Также можно написать «шутка», «прикол» или «анекдот»."
    )