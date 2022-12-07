from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


info_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text='Попробовать\n(3 дня бесплатно)'
            ),
            KeyboardButton(
                text='Подписка'
            ),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

info_subs_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text='Подписка'
            ),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)
