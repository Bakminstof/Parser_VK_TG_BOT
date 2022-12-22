from aiogram.types import ReplyKeyboardRemove, Message
from aiogram.dispatcher import FSMContext

from data import BOT_INFO
from loader import dp
from filters import TextFilter, CommandFilter
from keyboards.default.d_info import info_keyboard, info_subs_keyboard
from hendlers.handlers_funcs.funcs import check_subscription_and_add_to_cache


@dp.message_handler(TextFilter(text='Информация о боте'), state=None)
@dp.message_handler(CommandFilter(command='info'), state=None)
async def get_info(message: Message, state: FSMContext):
    subs, test = await check_subscription_and_add_to_cache(message.from_user.id, state)

    if not test and not subs:
        keyboard = info_keyboard
    elif test and not subs:
        keyboard = info_subs_keyboard
    else:
        keyboard = ReplyKeyboardRemove()

    await message.answer(BOT_INFO, reply_markup=keyboard, parse_mode='HTML')
    await state.reset_state(with_data=False)
