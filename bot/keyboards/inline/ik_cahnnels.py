from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from keyboards.inline.callbacks import (
    callback_channels,
    callback_choice,
    callback_slots,
    callback_slot_type,
    callback_slots_price
)


channels_add_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Добавить группу',
                callback_data=callback_channels.new(
                    type='add'
                )
            )
        ],
        [
            InlineKeyboardButton(
                text='Добавить слот',
                callback_data=callback_slots.new(
                    type='add_slot'
                )
            ),
            InlineKeyboardButton(
                text='Удалить слот',
                callback_data=callback_slots.new(
                    type='del_slot'
                )
            )
        ],
        [
            InlineKeyboardButton(
                text='Назад',
                callback_data=callback_channels.new(
                    type='main_back'
                )
            )
        ]
    ]
)

channels_change_del_back_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Изменить',
                callback_data=callback_channels.new(
                    type='change'
                )
            ),
            InlineKeyboardButton(
                text='Удалить',
                callback_data=callback_channels.new(
                    type='del'
                )
            )
        ],
        [
            InlineKeyboardButton(
                text='Назад',
                callback_data=callback_channels.new(
                    type='back'
                )
            )
        ]
    ]
)

channels_edit_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Редактировать',
                callback_data=callback_channels.new(
                    type='edit'
                )
            )
        ]
    ]
)

channels_choice_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Да',
                callback_data=callback_choice.new(
                    choice='yes'
                )
            ),
            InlineKeyboardButton(
                text='Нет',
                callback_data=callback_choice.new(
                    choice='no'
                )
            )
        ]
    ]
)

channels_add_group_slot_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Добавить',
                callback_data=callback_slots.new(
                    type='add_slot'
                )
            )

        ]
    ]
)

channels_slot_type_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Для сбора',
                callback_data=callback_slot_type.new(
                    type='collect'
                )
            ),
            InlineKeyboardButton(
                text='Для отправки',
                callback_data=callback_slot_type.new(
                    type='send'
                )
            )
        ]
    ]
)

slots_price_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='1',
                callback_data=callback_slots_price.new(
                    type='one'
                )
            ),
            InlineKeyboardButton(
                text='3',
                callback_data=callback_slots_price.new(
                    type='three'
                )
            ),
            InlineKeyboardButton(
                text='5',
                callback_data=callback_slots_price.new(
                    type='five'
                )
            ),
        ]
    ]
)

back_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Назад',
                callback_data=callback_channels.new(
                    type='back'
                )
            )
        ]
    ]
)
