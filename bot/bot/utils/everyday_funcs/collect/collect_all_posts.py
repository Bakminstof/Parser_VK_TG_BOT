import asyncio
import logging.config

from typing import List, Tuple, Dict
from sqlalchemy import select
from sqlalchemy.engine.row import Row

from db import async_mian_session, GroupsTable, UsersTable
from loader import TELETON_CLIENT
from utils.logging import dict_config, async_dec_logger, sync_dec_logger
from utils.parsers import TelegramParser
from utils.cache_item_cls import PostCacheItem
from utils.groupe_cache_cls import GroupCache
from utils.parsers.VK_parser import VKPost
from utils.parsers.Telegram_parser import TGPost
from utils.everyday_funcs.collect.thread_collect_all_post import ParserThread

CACHE: Dict[Tuple[int, str], GroupCache] = {}
TO_SEND_CACHE: List[Dict[str, List[str | int] | str | TGPost | VKPost]] = []

logging.config.dictConfig(dict_config)
collector_posts_logger = logging.getLogger('collector_posts')


@async_dec_logger(collector_posts_logger)
async def collect_all() -> None:
    groups_stmt = select(
        GroupsTable.id,
        GroupsTable.main_group_name,
        GroupsTable.main_group_url,
        GroupsTable.main_group_type,
        GroupsTable.main_group_id,
        GroupsTable.send_to_group_name,
        GroupsTable.send_to_group_url,
        GroupsTable.send_to_group_type,
        GroupsTable.send_to_group_id,
        GroupsTable.user_ids
    )
    users_stmt = select(
        UsersTable.telegram_id,
        UsersTable.subscription
    )

    groups_result = await async_mian_session.execute(groups_stmt)
    users_result = await async_mian_session.execute(users_stmt)

    groups_info: List[Row] | List[None] = groups_result.all()
    users_info: List[Row] | List[None] = users_result.all()

    collector_posts_logger.info(
        'Get users and groups data form db\nUsers info: {}\nGroups info: {}'.format(
            users_info,
            groups_info
        )
    )

    users_check: Dict[int, bool] = {
        row.telegram_id: row.subscription for row in users_info
    }

    main_groups: set[Tuple[int, str, str]] = set()
    group_rls: Dict[Tuple[int, str, str, int, str, str], List[int]] = dict()

    for row in groups_info:
        main_groups.add((row.main_group_id, row.main_group_type, row.main_group_url))

        group_rls[
            (
                row.main_group_id,
                row.main_group_type,
                row.main_group_url,
                row.send_to_group_id,
                row.send_to_group_type,
                row.send_to_group_url
            )
        ] = row.user_ids

    relationships: Dict[Tuple[int, str], List[Tuple[int, str]]] = {}

    for main_group_id, \
        main_group_type, \
        main_group_url, \
        send_to_group_id, \
        send_to_group_type, \
        send_to_group_url in group_rls.keys():

        main_group = (main_group_id, main_group_type)
        to_send_group = (send_to_group_id, send_to_group_type)

        val = relationships.get(main_group)
        user_ids = group_rls.get(
            (
                main_group_id,
                main_group_type,
                main_group_url,
                send_to_group_id,
                send_to_group_type,
                send_to_group_url
            )
        )

        check_subs = [users_check.get(id_) for id_ in user_ids]

        if val:
            if True in check_subs:
                relationships[main_group].append(to_send_group)
        else:
            if True in check_subs:
                relationships[main_group] = [to_send_group]

    collector_posts_logger.info('Build relationships: {}'.format(relationships))

    await start_parsers(main_groups)

    collector_posts_logger.info('Cache `CACHE` is build. ~{}'.format(CACHE))

    build__to_send_cache(relationships)


@async_dec_logger(collector_posts_logger)
async def start_parsers(groups: set[Tuple[int, str, str]]) -> None:
    workers = []
    tasks = []

    client = TELETON_CLIENT

    for group_id, type_, group_url in groups:
        post_ids = CACHE.get((group_id, type_), {}).get('post_ids', None)
        collector_posts_logger.info('Create parser\'s')

        if type_ == 'telegram':
            tg_parser = TelegramParser(
                group_id=group_id,
                group_url=group_url,
                client=client,
                post_ids=post_ids
            )
            tasks.append(tg_parser.start())
        else:
            p_thread = ParserThread(
                cache=CACHE,
                group_id=group_id,
                group_url=group_url,
                group_type=type_,
                post_ids=post_ids
            )
            p_thread.start()
            workers.append(p_thread)

    collector_posts_logger.warning('Run parser\'s coroutines - {}; threads - {}'.format(len(tasks), len(workers)))

    tg_cache_items: Tuple[Dict[Tuple[int, str], GroupCache] | BaseException] = await asyncio.gather(*tasks)

    for worker in workers:
        worker.join(120)

    del workers, tasks

    for item in tg_cache_items:
        CACHE.update(item)


@sync_dec_logger(collector_posts_logger)
def build__to_send_cache(relationships: Dict[Tuple[int, str], List[Tuple[int, str]]]) -> None:
    collector_posts_logger.info('Start build `TO_SEND_CACHE`')

    if CACHE:
        for main_group, to_send_group in relationships.items():
            gr = CACHE.get(main_group)
            posts = gr.posts

            to_sends: List[int] = [ts[0] for ts in to_send_group]

            for post in posts:
                p = PostCacheItem(
                    group_id=main_group[0],
                    send_to=to_sends,
                    post_item=post,
                    post_platform='telegram'
                )

                TO_SEND_CACHE.append(p.to_dict())

        collector_posts_logger.info('Cache `TO_SEND_CACHE` is build. ~{}'.format(TO_SEND_CACHE))

    else:
        collector_posts_logger.warning('Cache `CACHE` is empty')

    collector_posts_logger.info('Collecting done')
