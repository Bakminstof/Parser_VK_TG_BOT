import logging.config
import os
import shutil

from typing import List

from utils.everyday_funcs.collect import CACHE, TO_SEND_CACHE
from utils.logging import sync_dec_logger, dict_config

logging.config.dictConfig(dict_config)
clear_cache_logger = logging.getLogger('clear_cache')


@sync_dec_logger(clear_cache_logger)
def clear_cache_and_content_directories() -> None:
    group_names = []

    for group in CACHE.values():
        group.posts.clear()
        group_names.append(group.group_name)

        clear_cache_logger.debug('Removed {} posts in CACHE from group {}'.format(len(group.posts), group.group_name))

        group_dir = group.group_dir

        items: List[str] = os.listdir(group_dir)

        for item in items:
            post_id = group_dir / item
            shutil.rmtree(post_id)

        clear_cache_logger.debug('Clear {} directory, removed {} items'.format(group.group_name, len(items)))

    TO_SEND_CACHE.clear()

    clear_cache_logger.debug('Clear: `CACHE`, `TO_SEND_CACHE`, content in directories: {}'.format(group_names))

    group_names.clear()
