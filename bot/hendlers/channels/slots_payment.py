import datetime
import logging.config

from aiogram.types import ShippingQuery, ContentType, Message, PreCheckoutQuery, LabeledPrice, CallbackQuery
from aiogram.dispatcher import FSMContext

from db import update_user_stmt, async_session
from data import PAYMENTS_TOKEN, CURRENCY_RUB, current_slot_price
from loader import dp
from states import States
from data.prices import ONE_SLOT_PRICE, THREE_SLOTS_PRICE, FIVE_SLOTS_PRICE
from utils.logging import dict_config
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
            label = '1 слот'
            current_price = [
                LabeledPrice(label=label, amount=current_slot_price(ONE_SLOT_PRICE, subs_days, group_count))
            ]

        elif call.data.split(':')[-1] == 'three':
            group_count = 3
            label = '3 слота'
            current_price = [
                LabeledPrice(label=label, amount=current_slot_price(THREE_SLOTS_PRICE, subs_days, group_count))
            ]

        else:
            group_count = 5
            label = '5 слотов'
            current_price = [
                LabeledPrice(label=label, amount=current_slot_price(FIVE_SLOTS_PRICE, subs_days, group_count))
            ]
        subs_days_str = str(subs_days)

        if subs_days_str.endswith(('2', '3', '4')):
            d = 'дня'
        elif subs_days_str.endswith('1'):
            d = 'день'
        else:
            d = 'дней'

        data['group_count'] = group_count

        title = 'Доп. слоты'
        description = 'Покупка доп. слотов: {slot} на {subs_days} {d}\n'.format(slot=label, subs_days=subs_days, d=d)

        await dp.bot.send_invoice(
            chat_id=call.message.chat.id,
            title=title,
            description=description,
            provider_token=PAYMENTS_TOKEN,
            currency=CURRENCY_RUB,
            prices=current_price,
            is_flexible=False,  # True, если цена будет зависеть от доставки
            start_parameter='start_parameter',
            payload='some payload payload payload'
        )
        if st == States.CollectSlotState.state:
            slot_type = 'collect'
        else:
            slot_type = 'send'

        slots_payment_logger.info(
            'User `{id_user}`: Start payment to add {type} slots {count}'.format(
                id_user=user_id,
                type=slot_type,
                count=group_count
            )
        )


@dp.shipping_query_handler(lambda q: True, state=[States.CollectSlotState, States.SendSlotState])
async def shipping_porc_slots(shipping_query: ShippingQuery):
    await dp.bot.answer_shipping_query(shipping_query.id, ok=True)


@dp.pre_checkout_query_handler(lambda q: True, state=[States.CollectSlotState, States.SendSlotState])
async def pre_checkout_porc_slots(pre_checkout_query: PreCheckoutQuery):
    await dp.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT, state=[States.CollectSlotState, States.SendSlotState])
async def successful_payment_slot(message: Message, state: FSMContext):
    id_user = message.from_user.id

    st = await state.get_state()

    async with state.proxy() as data:
        group_count = data.get('group_count')

        if st == States.CollectSlotState.state:
            slot_type = 'collect'
            data[id_user]['additionally_search_group'] = \
                data.get(id_user).get('additionally_search_group', 0) + group_count

        else:
            slot_type = 'send'
            data[id_user]['additionally_send_group'] = \
                data.get(id_user).get('additionally_send_group', 0) + group_count

        user = data.get(id_user)
        stmt = update_user_stmt(user)

        await async_session.execute(stmt)
        await async_session.commit()

        await message.answer('<b>Добавлено!</b>', parse_mode='HTML')

        del data['group_count']

    await state.reset_state(with_data=False)

    slots_payment_logger.info(
        'User `{id_user}`: Successful payment {count} {type} slots '.format(
            id_user=id_user,
            type=slot_type,
            count=group_count
        )
    )
