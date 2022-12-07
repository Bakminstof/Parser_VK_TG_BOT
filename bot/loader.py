import asyncio

from asyncio import AbstractEventLoop
from aiogram import Bot, Dispatcher
from telethon import TelegramClient
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data import BOT_TOKEN
from utils.parsers.Telegram_parser import create_tg_client

# BOT
bot: Bot = Bot(token=BOT_TOKEN)
storage: MemoryStorage = MemoryStorage()
dp: Dispatcher = Dispatcher(bot, storage=storage)
loop: AbstractEventLoop = asyncio.get_event_loop()

TELETON_CLIENT: TelegramClient = loop.run_until_complete(create_tg_client())
