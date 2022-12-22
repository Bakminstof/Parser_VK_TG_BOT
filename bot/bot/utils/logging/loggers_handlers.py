import datetime
import logging
import sys

from db import LOG_CACHE, BaseLoggerTable

format_ = "%(levelname)s | %(name)s | %(asctime)s | %(lineno)s | %(message)s"
date_fmt_ = '%Y-%m-%d %H:%M:%S'


class ColourFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    turquoise = "\x1b[36;20m"
    purple = "\x1b[35;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    def __init__(self):
        super().__init__()
        self.datefmt = date_fmt_
        self.default_time_format = format_

    FORMATS = {
        logging.NOTSET: grey + format_ + reset,
        logging.DEBUG: turquoise + format_ + reset,
        logging.INFO: purple + format_ + reset,
        logging.WARNING: yellow + format_ + reset,
        logging.ERROR: red + format_ + reset,
        logging.CRITICAL: bold_red + format_ + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(fmt=log_fmt, datefmt=self.datefmt)
        return formatter.format(record)


class ConsoleHandler(logging.Handler):
    def __init__(self, fmt=ColourFormatter(), stream=sys.stderr):
        super().__init__()
        self.stream = stream
        self.formatter = fmt

    def emit(self, record: logging.LogRecord) -> None:
        message = self.format(record)
        self.stream.write(message + '\n')


class LogsDBHandler(logging.Handler):
    def emit(self, log: logging.LogRecord) -> None:
        self.format(log)
        date, time = log.asctime.split()

        log = BaseLoggerTable(
            level=log.levelname,
            name=log.name,
            dtime=datetime.datetime(
                year=int(date[0:4]),
                month=int(date[5:7]),
                day=int(date[8:10]),
                hour=int(time[0:2]),
                minute=int(time[3:5]),
                second=int(time[6:8]),
            ),
            line=log.lineno,
            message=log.message,
            except_text=log.exc_text
        )

        LOG_CACHE.append(log)
