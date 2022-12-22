import logging.config

from typing import List
from threading import Thread, Semaphore

from utils.logging import dict_config, sync_dec_logger
from utils.parsers import VKParser
from utils.groupe_cache_cls import GroupCache


logging.config.dictConfig(dict_config)
parsers_thread_logger = logging.getLogger('parsers_thread')


class ParserThread(Thread):
    def __init__(
            self,
            cache: dict[tuple[int, str], GroupCache],
            group_id: int,
            group_url: str,
            group_type: str,
            post_ids: List[int] | None = None
    ):
        super().__init__()
        self.cache = cache
        self.post_ids = post_ids if post_ids else []

        self.group_id = group_id
        self.group_url = group_url
        self.group_type = group_type
        self.group_name = self.group_url.split('/')[-1]

        self.__logging_main_str = 'Parser=({thread}): '.format(
            thread=self.name,
            group=self.group_name
        ) + '{}'

        self.__semaphore = Semaphore()

    @sync_dec_logger(parsers_thread_logger)
    def run(self) -> None:
        if self.group_type == 'vk':
            parser = VKParser(group_id=self.group_id, group_url=self.group_url)

            log_ = '({}) Start parser\'s thread'.format(parser.name)
            parsers_thread_logger.info(self.__logging_main_str.format(log_))

            parser.post_ids = self.post_ids

            log_ = 'Cache id\'s: {}'.format(parser.post_ids)
            parsers_thread_logger.info(self.__logging_main_str.format(log_))

            parser.start()

            group = GroupCache(
                group_name=self.group_name,
                group_dir=parser.group_content_dir,
                posts=parser.posts,
                post_ids=parser.post_ids
            )

            self.__semaphore.acquire()
            self.cache[(self.group_id, self.group_type)] = group
            self.__semaphore.release()

            log_ = 'Append to cache: {}'.format(group)
            parsers_thread_logger.info(self.__logging_main_str.format(log_))
        else:
            parsers_thread_logger.warning('Another type parsers')
