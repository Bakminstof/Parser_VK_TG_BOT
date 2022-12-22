import datetime
import logging.config

from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.storage import FSMContextProxy

from db import update_user_stmt, async_mian_session
from data import current_slot_price, QIWI_PAYMENT_URL
from loader import dp, qiwi_api
from states import States
from data.prices import ONE_SLOT_PRICE, THREE_SLOTS_PRICE, FIVE_SLOTS_PRICE
from utils.logging import dict_config
from hendlers.handlers_funcs import pay_process
from keyboards.inline.callbacks import callback_slots_price

logging.config.dictConfig(dict_config)
slots_payment_logger = logging.getLogger('slots_payment')


# Покупка дополнительных слотов
@dp.callback_query_handler(callback_slots_price.filter(), state=[States.CollectSlotState, States.SendSlotState])
async def add_slot(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    st = await state.get_state()

    async with state.proxy() as data:
        date_end_subscription: datetime.datetime = data.get(user_id).get('date_end_subscription')
        subs_days = date_end_subscription.date() - datetime.date.today()
        subs_days = int(subs_days.days)

        if call.data.split(':')[-1] == 'one':
            group_count = 1
            price = current_slot_price(ONE_SLOT_PRICE, subs_days, group_count)
            label = '1 слот'

        elif call.data.split(':')[-1] == 'three':
            group_count = 3
            price = current_slot_price(THREE_SLOTS_PRICE, subs_days, group_count)
            label = '3 слота'

        else:
            group_count = 5
            price = current_slot_price(FIVE_SLOTS_PRICE, subs_days, group_count)
            label = '5 слотов'

        subs_days_str = str(subs_days)

        if subs_days_str.endswith(('2', '3', '4')):
            d = 'дня'
        elif subs_days_str.endswith('1'):
            d = 'день'
        else:
            d = 'дней'

        msg = 'Покупка доп. слотов: {slot} на {subs_days} {d}\n'.format(slot=label, subs_days=subs_days, d=d)

        final_price = price

        await call.message.edit_text(msg, parse_mode='HTML')

        bill = qiwi_api.bill(final_price)

        fin_msg = 'Для оплаты нужно будет перевести на киви-кошелёк:\n\n' \
                  '<b>{amount} руб.</b>\n\n' \
                  'И в строке комментарий обязательно вставить это ключ \u2b07\ufe0f \u2b07\ufe0f'.format(
                    amount=final_price
                  )

        key_msg = '<b>{key}</b>'.format(key=bill['id'])
        pay_msg = '<b><a href="{payment_url}">Оплатить</a></b>'.format(payment_url=QIWI_PAYMENT_URL)

        await call.message.answer(fin_msg, parse_mode='HTML')
        await call.message.answer(key_msg, parse_mode='HTML')

        mes = await call.message.answer(pay_msg, parse_mode='HTML')

        if await pay_process(bill=bill, message=mes):
            await successful_payment_slot(user_id=user_id, group_count=group_count, message=mes, st=st, data=data)
            await state.reset_state(with_data=False)

        else:
            exc_mes = 'Произошла ошибка, повторите позже'
            await mes.edit_text(exc_mes)
            await state.reset_state(with_data=True)


async def successful_payment_slot(user_id: int, st: str, group_count: int, message: Message, data: FSMContextProxy):
    if st == States.CollectSlotState.state:
        slot_type = 'collect'
        data[user_id]['additionally_search_group'] = \
            data.get(user_id).get('additionally_search_group', 0) + group_count

    else:
        slot_type = 'send'
        data[user_id]['additionally_send_group'] = \
            data.get(user_id).get('additionally_send_group', 0) + group_count

    user = data.get(user_id)
    stmt = update_user_stmt(user)

    await async_mian_session.execute(stmt)
    await async_mian_session.commit()

    await message.answer('<b>Добавлено!</b>', parse_mode='HTML')

    slots_payment_logger.info(
        'User `{user_id}`: Successful payment {count} {type} slots '.format(
            user_id=user_id,
            type=slot_type,
            count=group_count
        )
    )
