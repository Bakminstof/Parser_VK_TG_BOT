import sys

from utils.logging.loggers_handlers import ConsoleHandler


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
        }
    },
    "loggers": {
        "qiwi_api_logger": {
            "level": "DEBUG",
            "handlers": [
                "console"
            ],
            'propagate': False
        }
    },
    'root': {
        "level": "DEBUG",
        "handlers": [
            'console'
        ]
    }
}
