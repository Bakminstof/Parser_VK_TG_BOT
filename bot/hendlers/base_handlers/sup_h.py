from aiogram import types

from data import SUPPORT
from loader import dp


@dp.message_handler(commands=['sup'], state=None)
async def get_help(message: types.Message):
    await message.answer(
        'Связаться с поддержкой:\n'
        '<b><a href="{SUPPORT}">Поддержка</a></b>'.format(SUPPORT=SUPPORT),
        parse_mode='HTML'
    )
