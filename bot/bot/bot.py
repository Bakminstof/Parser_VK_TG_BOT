import sentry_sdk

from aiogram import executor

from utils.misc.on_events import on_startup, on_shutdown
from utils.everyday_funcs.main_cycle import dp

sentry_sdk.init(
    dsn="https://90eda125245b4a669ac95818a4a59b08@o1267040.ingest.sentry.io/4504270378696704",

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0
)


if __name__ == '__main__':
    ## dev ##
    executor.start_polling(
        dispatcher=dp,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=False,
    )
