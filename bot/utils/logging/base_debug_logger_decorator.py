import functools
import logging.config

from typing import Callable
from logging import Logger

from data import DEBUG
from utils.logging.loggers_config import dict_config

logging.config.dictConfig(dict_config)
BASE_LOGGER = logging.getLogger('BASE_DEBUG_LOGGER')


def async_dec_logger(logger_: Logger = None):
    """
    Декоратор для асинхронных функций
    :param logger_: Logger
    :return: __decorator Callable
    """
    if not logger_:
        logger_ = BASE_LOGGER

    def __decorator(func: Callable):

        @functools.wraps(func)
        async def __wrap(*args, **kwargs):
            if DEBUG:
                try:
                    logger_.debug('Start func: <{}>'.format(func.__name__))

                    res = await func(*args, **kwargs)

                    logger_.debug('End func: <{}>'.format(func.__name__))

                    return res

                except Exception as ex:
                    logger_.exception('Exception in func: <{n}>: `{ex}`'.format(n=func.__name__, ex=ex))
                    raise
            else:
                return await func(*args, **kwargs)

        return __wrap

    return __decorator


def sync_dec_logger(logger_: Logger = None):
    """
    Декоратор для синхронных функций
    :param logger_: Logger
    :return: __decorator Callable
    """
    if not logger_:
        logger_ = BASE_LOGGER

    def __decorator(func: Callable):

        @functools.wraps(func)
        def __wrap(*args, **kwargs):
            if DEBUG:
                try:
                    logger_.debug('Start func: <{}>'.format(func.__name__))

                    res = func(*args, **kwargs)

                    logger_.debug('End func: <{}>'.format(func.__name__))

                    return res

                except Exception as ex:
                    logger_.exception('Exception in func: <{n}>: `{ex}`'.format(n=func.__name__, ex=ex))
                    raise
            else:
                return func(*args, **kwargs)

        return __wrap

    return __decorator
