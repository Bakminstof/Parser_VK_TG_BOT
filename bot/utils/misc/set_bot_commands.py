from aiogram import types, Dispatcher


async def set_default_commands(dp: Dispatcher):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Запустить бота"),
            types.BotCommand("info", "Информация"),
            types.BotCommand("channels", "Список каналов/групп"),
            types.BotCommand("subs", "Подписка"),
            types.BotCommand("cancel", "Отменить все действия"),
            types.BotCommand("help", "Список команд"),
            types.BotCommand("sup", "Поддержка"),
        ]
    )
