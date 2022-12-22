import sys

from utils.logging.loggers_handlers import ConsoleHandler, LogsDBHandler


dict_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "base": {
            "format": "%(levelname)s | %(name)s | %(asctime)s | %(lineno)s | %(message)s",
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    "handlers": {
        "console": {
            "()": ConsoleHandler,
            "level": "DEBUG",
            'stream': sys.stdout
        },
        "logs_db_handler": {
            "()": LogsDBHandler,
            "level": "DEBUG",
            "formatter": "base",
        }
    },
    "loggers": {
        "BASE_DEBUG_LOGGER": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "telethon.network.mtprotosender": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "start": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "edit_rls": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "slots": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "channels": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "slots_payment": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "subscription": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "main_cycle": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "clear_cache": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "send_all_posts": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "user_mgmt": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "parsers_thread": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "collector_posts": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "init_db": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "notify": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "telegram_parser": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "tg_post": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "vk_parser": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "vk_post": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "backup": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "qiwi_api_logger": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        }
    },
    'root': {
        "level": "DEBUG",
        "handlers": [
            'console',
            # 'logs_db_handler'
        ],
    }
}
