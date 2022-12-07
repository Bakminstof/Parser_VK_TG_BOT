from aiogram import types

from loader import dp


@dp.message_handler(state=None)
async def others(message: types.Message):
    await message.answer('Не понимаю :/\n'
                         'Список команд /help')
