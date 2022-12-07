from aiogram import types

from loader import dp


@dp.message_handler(commands=['help'], state=None)
async def get_help(message: types.Message):
    await message.answer(
        '<b>Список доступных команд:</b>\n\n'
        '/start - <i>запуск бота</i>\n\n'
        '/info - <i>информация</i>\n\n'
        '/channels - <i>список каналов/групп</i>\n\n'
        '/subs - <i>подписка</i>\n\n'
        '/cancel - <i>отменить все действия</i>\n\n'
        '/help - <i>список команд</i>\n\n',
        parse_mode='HTML'
    )
