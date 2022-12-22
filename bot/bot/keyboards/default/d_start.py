from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


start_wo_subs_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text='Подписка'
            ),
            KeyboardButton(
                text='Попробовать\n(3 дня бесплатно)'
            ),
        ],
        [
           KeyboardButton(
                text='Информация о боте'
            ),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

start_subs_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text='Подписка'
            )
        ],
        [
           KeyboardButton(
                text='Информация о боте'
            ),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

start_with_subs_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text='Информация о боте'
            )
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)
