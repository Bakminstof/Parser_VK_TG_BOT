from aiogram import types
from aiogram.types import ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext

from loader import dp


@dp.message_handler(commands=['cancel'], state='*')
async def get_help(message: types.Message, state: FSMContext):
    await state.reset_state(with_data=True)
    await message.answer('Вы отменили все действия', reply_markup=ReplyKeyboardRemove())
