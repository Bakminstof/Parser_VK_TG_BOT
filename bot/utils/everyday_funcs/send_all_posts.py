import logging.config
import asyncio

from typing import List
from aiogram import Bot

from utils.logging import dict_config, async_dec_logger
from utils.parsers.VK_parser import VKPost
from utils.everyday_funcs.collect import TO_SEND_CACHE
from utils.parsers.Telegram_parser import TGPost


logging.config.dictConfig(dict_config)
send_all_posts_logger = logging.getLogger('send_all_posts')


@async_dec_logger(send_all_posts_logger)
async def send_all(bot: Bot) -> None:
    tasks = []

    for item in TO_SEND_CACHE:
        tg_post: TGPost | VKPost = item.get('post_item')

        task = tg_post.for_send_in_tg()
        tasks.append(task)

        #         'group_name',
        #         'send_to',
        #         'post_platform',
        #         'post_item'

    posts: List[dict] = await asyncio.gather(*tasks)

    bot_tasks = []

    for post in posts:
        type_ = post.pop('type')
        chat_ids = post.pop('chat_ids')

        for chat in chat_ids:
            post['chat_id'] = chat

            if type_ == 'text':
                bot_task = bot.send_message(**post)
                bot_tasks.append(bot_task)

                # await bot_task
                # time.sleep(3)

            elif type_ == 'contact':
                bot_task = bot.send_contact(**post)
                bot_tasks.append(bot_task)

                # await bot_task
                # time.sleep(3)

            elif type_ == 'voice':
                bot_task = bot.send_voice(**post)
                bot_tasks.append(bot_task)

                # await bot_task
                # time.sleep(3)

            elif type_ == 'sticker':
                bot_task = bot.send_sticker(**post)
                bot_tasks.append(bot_task)

                # await bot_task
                # time.sleep(3)

            elif type_ == 'group':
                bot_task = bot.send_media_group(**post)
                bot_tasks.append(bot_task)

                # await bot_task
                # time.sleep(3)

        # dp.bot.send_chat_action()  # ?
        # dp.bot.send_video_note()  # ?
        # dp.bot.send_invoice()  # ?
        # dp.bot.send_venue()  # ?
        # dp.bot.send_dice()  # ?
        # dp.bot.send_game()  # ?
        # dp.bot.send_location()
        # dp.bot.send_poll()

    await asyncio.gather(*bot_tasks)  # todo Flood control!!!

    send_all_posts_logger.info('Send {} posts'.format(len(posts)))
