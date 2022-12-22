from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from keyboards.inline.callbacks import callback_subs, callback_test_period

subs_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='1 неделя',
                callback_data=callback_subs.new(
                    type='week'
                )
            ),
            InlineKeyboardButton(
                text='1 месяц',
                callback_data=callback_subs.new(
                    type='one_month'
                )
            ),
            InlineKeyboardButton(
                text='3 месяца',
                callback_data=callback_subs.new(
                    type='three_months'
                )
            )
        ],
        [
            InlineKeyboardButton(
                text='Назад',
                callback_data=callback_subs.new(
                    type='back'
                )
            )
        ]
    ]
)

subs_buy_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Купить',
                callback_data=callback_subs.new(
                    type='buy'
                )
            )
        ]
    ]
)

subs_append_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Продлить',
                callback_data=callback_subs.new(
                    type='append'
                )
            )
        ]
    ]
)


subs_buy_test_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Купить',
                callback_data=callback_subs.new(
                    type='buy'
                )
            ),
            InlineKeyboardButton(
                text='Попробовать\n(3 дня бесплатно)',
                callback_data=callback_subs.new(
                    type='test'
                )
            )
        ]
    ]
)


test_period_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Да',
                callback_data=callback_test_period.new(
                    choice='yes'
                )
            ),
            InlineKeyboardButton(
                text='Нет',
                callback_data=callback_test_period.new(
                    choice='no'
                )
            ),
        ]
    ]
)
