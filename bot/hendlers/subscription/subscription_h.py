import datetime
import logging.config

from aiogram.dispatcher import FSMContext

from db import async_session, update_user_stmt
from data import continue_subscription_price, CURRENCY_RUB, PAYMENTS_TOKEN
from states import States
from loader import dp
from filters import TextFilter, CommandFilter
from data.prices import ONE_WEEK_GROUP_PRICE, THREE_MONTHS_GROUP_PRICE, ONE_MONTH_GROUP_PRICE, SLOT_PERCENT
from utils.logging import dict_config
from keyboards.inline.callbacks import callback_test_period, callback_subs
from hendlers.handlers_funcs import check_subscription_and_add_to_cache
from keyboards.inline import (
    subs_append_keyboard,
    subs_buy_keyboard,
    subs_buy_test_keyboard,
    subs_keyboard,
    test_period_keyboard
)
from aiogram.types import (
    Message,
    ReplyKeyboardRemove,
    CallbackQuery,
    LabeledPrice,
    ShippingQuery,
    PreCheckoutQuery,
    ContentType
)


logging.config.dictConfig(dict_config)
subscription_logger = logging.getLogger('subscription')

CMD = 'subs'


# Просмотр подписки
@dp.callback_query_handler(callback_subs.filter(type='back'), state=None)
@dp.callback_query_handler(callback_test_period.filter(choice='no'), state=None)
@dp.message_handler(TextFilter(text='Подписка'), state=None)
@dp.message_handler(CommandFilter(command=CMD), state=None)
async def subscription(message_call: Message | CallbackQuery, state: FSMContext):
    if isinstance(message_call, CallbackQuery):
        message = message_call.message
        user_id = message_call.from_user.id
        back = True
    else:
        message = message_call
        user_id = message.from_user.id
        back = False

    subs, test = await check_subscription_and_add_to_cache(user_id, state)

    async with state.proxy() as data:
        date_end_subscription: datetime.datetime = data.get(user_id).get('date_end_subscription')

    if not test and not subs:
        msg = 'У вас сейчас нет подписки. Вы можете воспользоваться тестовым периодом или сразу оформить подписку'

        if back:
            await message.edit_text(msg, reply_markup=subs_buy_test_keyboard)
        else:
            await message.answer(msg, reply_markup=subs_buy_test_keyboard)

        subscription_logger.info('User `{id_user}` -> {cmd} :: Not subs, not test'.format(id_user=user_id, cmd=CMD))

    elif test and not subs:
        msg = 'Ваш пробный период закончился. Для дальнейшей работы необходимо приобрести подписку'

        if back:
            await message.edit_text(msg, reply_markup=subs_buy_keyboard)
        else:
            await message.answer(msg, reply_markup=subs_buy_keyboard)

        subscription_logger.info('User `{id_user}` -> {cmd} :: Not subs, have test'.format(id_user=user_id, cmd=CMD))

    else:
        days_left = date_end_subscription.date() - datetime.date.today()
        days_left = str(days_left.days)

        if days_left.endswith(('2', '3', '4')):
            d = 'дня'
        elif days_left.endswith('1'):
            d = 'день'
        else:
            d = 'дней'

        msg = 'У вас подписка до {}\nОсталось: {} {}'.format(date_end_subscription.date(), days_left, d)

        if back:
            await message.edit_text(msg, reply_markup=subs_append_keyboard)
        else:
            await message.answer(msg, reply_markup=subs_append_keyboard)

        subscription_logger.info(
            'User `{id_user}`: Subscription days left :: {days}'.format(id_user=user_id, days=days_left)
        )


# Проверка тестового периода
@dp.message_handler(TextFilter(text='Попробовать\n(3 дня бесплатно)'), state=None)
async def test_period(message: Message, state: FSMContext):
    _, test = await check_subscription_and_add_to_cache(message.from_user.id, state)

    if not test:
        await message.answer('Воспользоваться тестовым периодом?', reply_markup=test_period_keyboard)
    else:
        await message.answer('Вы уже использовали тестовый период', reply_markup=ReplyKeyboardRemove())

    subscription_logger.info(
        'User `{id_user}`: Test period :: {test}'.format(id_user=message.from_user.id, test='Used' if test else 'Not')
    )


# Активация тестового периода
@dp.callback_query_handler(callback_subs.filter(type='test'), state=None)
@dp.callback_query_handler(callback_test_period.filter(choice='yes'), state=None)
async def test_period_yes(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        user = data.get(call.from_user.id)

        today = datetime.date.today()

        user['subscription'] = True
        user['subscription_test_period'] = True
        user['date_end_subscription'] = user.get('date_end_subscription') \
            if user.get('date_end_subscription') \
            else today + datetime.timedelta(days=3)

        stmt = update_user_stmt(user)

        await call.message.delete_reply_markup()
        await call.message.edit_text('Тестовый период активирован!')

        await async_session.execute(stmt)
        await async_session.commit()

        subscription_logger.info(
            'User `{id_user}`: Activate test period :: {date}'.format(
                id_user=call.from_user.id,
                date=today
            )
        )


# Выбор продолжительности подписки
@dp.callback_query_handler(callback_subs.filter(type=['buy', 'append']), state=None)
async def get_subs(call: CallbackQuery):
    msg = 'На сколько вы хотите приобрести подписку?'
    await call.message.edit_text(msg, reply_markup=subs_keyboard)


# Начало покупки подписки
@dp.callback_query_handler(callback_subs.filter(type=['week', 'one_month', 'three_months']), state=None)
async def append_subs(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id

    if call.data.split(':')[-1] == 'week':
        label = '1 неделя'
        base_price = ONE_WEEK_GROUP_PRICE
        subs_days_count = 7

    elif call.data.split(':')[-1] == 'one_month':
        label = '1 месяц'
        base_price = ONE_MONTH_GROUP_PRICE
        subs_days_count = 30

    else:
        label = '3 месяца'
        base_price = THREE_MONTHS_GROUP_PRICE
        subs_days_count = 90

    async with state.proxy() as data:
        additionally_search_group = data.get(user_id).get('additionally_search_group', 0)
        additionally_send_group = data.get(user_id).get('additionally_send_group', 0)

        data['subs_add_days_count'] = subs_days_count

        if additionally_send_group or additionally_search_group:
            price = continue_subscription_price(base_price, additionally_send_group + additionally_search_group)
            final_price_msg = '<b>{total_price} руб.</b> ' \
                              '(<b>базовая цена {base_price} руб.</b> за {subs_days_count} дней + ' \
                              '<b>доп. слоты {slots_price} руб.</b> за {subs_days_count} дней)'.format(
                                total_price=price[0],
                                base_price=price[1],
                                slots_price=price[2],
                                subs_days_count=subs_days_count
                              )

            msg = 'С учетом подключенных дополнительных слотов\n' \
                  '<i>({collect}{sep}{send})</i>\n' \
                  'стоимость (+ {slot_perc}% к базовой подписки стоимости за слот) будет составлять:' \
                  '\n\n<b>{price}</b>'.format(
                    collect='доп слоты для сбора: {}'.format(additionally_search_group)
                    if additionally_search_group
                    else '',
                    sep=',' if additionally_search_group and additionally_send_group else '',
                    send='доп слоты для отправки: {}'.format(additionally_send_group)
                    if additionally_send_group
                    else '',
                    slot_perc=SLOT_PERCENT,
                    price=final_price_msg
                  )
            final_price = price[0] * 100

        else:
            msg = 'Стоимость подписки будет составлять:\n\n<b>{price} руб.</b>'.format(
                price=base_price / 100
            )
            final_price = base_price

        await call.message.edit_text(msg, parse_mode='HTML')

        title = 'Подписка {}'.format(label)
        description = 'Оплатить подписку'

        current_price = [
            LabeledPrice(label=label, amount=final_price)
        ]

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

        await States.SubsPaymentState.set()


@dp.shipping_query_handler(lambda q: True, state=States.SubsPaymentState)
async def shipping_porc_subs(shipping_query: ShippingQuery):
    await dp.bot.answer_shipping_query(shipping_query.id, ok=True)


@dp.pre_checkout_query_handler(lambda q: True, state=States.SubsPaymentState)
async def pre_checkout_porc_subs(pre_checkout_query: PreCheckoutQuery):
    await dp.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


# Хэндлер успешный покупки подписки
@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT, state=States.SubsPaymentState)
async def successful_payment_slot(message: Message, state: FSMContext):
    id_user = message.from_user.id

    async with state.proxy() as data:
        subs_add_days_count = data.get('subs_add_days_count')
        date_end_subscription: datetime.date = data.get(id_user).get('date_end_subscription')
        date_start_subscription: datetime.date = data.get(id_user).get('date_start_subscription', None)

        data[id_user]['date_start_subscription'] = datetime.date.today() \
            if date_start_subscription is None \
            else date_start_subscription

        data[id_user]['date_end_subscription'] = date_end_subscription + datetime.timedelta(days=subs_add_days_count)

        user = data.get(id_user)
        stmt = update_user_stmt(user)

        await async_session.execute(stmt)
        await async_session.commit()

        await message.answer('<b>Подписка успешно приобретена!</b>', parse_mode='HTML')

        del data['subs_add_days_count']

    await state.reset_state(with_data=False)

    subscription_logger.info(
        'User `{id_user}`: Successful payment subs :: {days}'.format(
            id_user=id_user,
            days=subs_add_days_count
        )
    )
