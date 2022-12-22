import os
import time
import asyncio
import threading
import logging.config

from typing import List, Dict, Any, Tuple
from pathlib import Path, PosixPath
from telethon import TelegramClient
from aiogram.types import MessageEntity, MessageEntityType
from telethon.tl.types import MessageMediaContact, User, Chat, Channel
from telethon.tl.types.messages import ChannelMessages
from telethon.tl.functions.messages import GetHistoryRequest

from data import TG_API_ID, TG_API_HASH, TG_PHONE
from utils.logging import dict_config, async_dec_logger, sync_dec_logger
from utils.groupe_cache_cls import GroupCache
from utils.parsers.meta_display_cls import MetaDisplayCLS
from utils.parsers.Telegram_parser.tg_post_cls import TGPost, Media


logging.config.dictConfig(dict_config)
telegram_parser_logger = logging.getLogger('telegram_parser')


@sync_dec_logger(telegram_parser_logger)
def create_media_item(suffixes: List[str], path: PosixPath, post: Dict[str, Any] = None) -> Media | None:
    kwargs = None

    if '.jpg' in suffixes:
        m_type = 'photo'
    elif '.mp4' in suffixes:
        m_type = 'video'
    elif '.mp3' in suffixes:
        m_type = 'audio'
    # elif '.pdf' in suffixes:
    #     m_type = 'doc'
    elif '.gif' in suffixes:
        m_type = 'animation'
    elif '.oga' in suffixes:
        m_type = 'voice'
    elif '.tgs' in suffixes:
        m_type = 'sticker'
    elif '.vcard' in suffixes:
        m_type = 'contact'
        kwargs = post.get('media').get('kwargs')
    else:
        m_type = 'doc'
        # другой тип медиа

    media_item = Media(
        type_=m_type,
        location=path,
        kwargs=kwargs
    )

    log_ = '({}): Got media: {}'.format(threading.current_thread().name, media_item)
    telegram_parser_logger.debug(log_)

    return media_item


@async_dec_logger(telegram_parser_logger)
async def create_tg_client() -> TelegramClient:
    telegram_parser_logger.debug('Create telegram searcher client')

    client_session_name = Path(__file__).parent / 'sessions' / 'client_session'
    client_session_name = client_session_name.absolute()

    client = TelegramClient(str(client_session_name), TG_API_ID, TG_API_HASH)
    await client.start(phone=TG_PHONE)

    return client


@async_dec_logger(telegram_parser_logger)
async def get_entity(client: TelegramClient, name: str) -> User | Chat | Channel | str:
    try:
        entity = await client.get_entity(name)
        return entity
    except ValueError:
        telegram_parser_logger.warning('Closed group: {}'.format(name))
        return 'Closed'
    except Exception:
        telegram_parser_logger.warning('Not found: {}'.format(name))
        return 'Not found'


class TelegramParser(MetaDisplayCLS):
    __ID = 0

    def __init__(
            self,
            group_id: int,
            group_url: str,
            client: TelegramClient,
            post_count_limit: int = 40,
            timeout: int = 120,
            post_ids: List[int] | None = None,
    ):

        if post_ids is None:
            post_ids: List[int] = []

        TelegramParser.__ID += 1

        self.id = TelegramParser.__ID
        self.name = 'Telegram_parser'
        self.__parser_type = 'telegram'
        self.client = client
        self.timeout = timeout
        self.group_name = group_url.split('/')[-1]
        self.group_id = group_id

        self.__logging_main_str = '({name} <{id}>)({group}): '.format(
            name=self.name,
            id=self.id,
            group=self.group_name
        ) + '{}'

        self.__content_dir = Path(__file__).parent / 'content'
        self.__content_dir = self.__content_dir.absolute()

        self.group_content_dir = self.__content_dir / self.group_name
        self.group_content_dir = self.group_content_dir.absolute()

        self.post_count_limit = post_count_limit
        self.posts: List[TGPost] = []
        self.post_ids = post_ids

        self.__check_exist_dir()

    @sync_dec_logger(telegram_parser_logger)
    def __check_exist_dir(self) -> None:
        log_ = 'Check group dir'
        telegram_parser_logger.debug(self.__logging_main_str.format(log_))

        if not os.path.exists(self.group_content_dir):
            os.mkdir(self.group_content_dir)

            log_ = 'Create group dir'
            telegram_parser_logger.debug(self.__logging_main_str.format(log_))

    @async_dec_logger(telegram_parser_logger)
    async def start(self) -> Dict[Tuple[int, str], GroupCache]:
        log_ = 'Start TG parser'
        telegram_parser_logger.debug(self.__logging_main_str.format(log_))

        group = await self.pars()
        return {(self.group_id, self.__parser_type): group}

    @async_dec_logger(telegram_parser_logger)
    async def pars(self) -> GroupCache:
        log_ = 'Start parsing channel: {}'.format(self.group_name)
        telegram_parser_logger.debug(self.__logging_main_str.format(log_))

        posts = []
        post_ids = []

        channel_posts: ChannelMessages = await self.client(
            GetHistoryRequest(
                peer=self.group_id,
                limit=self.post_count_limit,
                offset_date=None,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0
            )
        )

        tasks = []

        for mes in channel_posts.messages:
            check_group: int | None = mes.grouped_id

            if check_group:
                post_id = check_group
            else:
                post_id = mes.id

            if post_id in self.post_ids:
                continue

            post_ids.append(post_id)

            post_dir_local_path = self.group_content_dir / str(post_id)
            post_dir_local_path = post_dir_local_path.absolute()

            if not os.path.exists(post_dir_local_path):
                log_ = 'Post: ({}) Create post dir: {}'.format(post_id, post_dir_local_path)
                telegram_parser_logger.debug(self.__logging_main_str.format(log_))
                os.mkdir(post_dir_local_path)

            entities = mes.entities
            media = mes.media

            if entities:
                entities = self.__get_entities(entities, post_id)

                log_ = 'Post: ({}) Got entities'.format(post_id)
                telegram_parser_logger.debug(self.__logging_main_str.format(log_))

            if media:

                def callback_download_media(current, total):
                    log__ = 'Post: ({}) Download media bytes: {:.2%}'.format(post_id, current / total)
                    telegram_parser_logger.debug(self.__logging_main_str.format(log__))

                media = self.__get_media(post_id, media, post_dir_local_path)

                tasks.append(
                    self.client.download_media(
                        message=mes,
                        file=str(post_dir_local_path),
                        progress_callback=callback_download_media
                    )
                )

                log_ = 'Post: ({}) Got media, append download task'.format(post_id)
                telegram_parser_logger.debug(self.__logging_main_str.format(log_))

            post = {
                'id': post_id,
                'grouped_id': check_group,
                'local_path': post_dir_local_path,
                'text': mes.message,
                'entities': entities,
                'media': media
            }

            log_ = 'Create mid post: {}'.format(post)
            telegram_parser_logger.debug(self.__logging_main_str.format(log_))

            posts.append(post)

        st = time.time()
        log_ = 'Start downloading media'
        telegram_parser_logger.debug(self.__logging_main_str.format(log_))

        await asyncio.gather(*tasks)

        fn = time.time()
        log_ = 'Finish downloading media: {} sec.'.format(round(fn - st, 2))
        telegram_parser_logger.debug(self.__logging_main_str.format(log_))

        self.post_ids = post_ids

        self.__make_posts(posts)

        return self.__build_tg_cache_item()

    @sync_dec_logger(telegram_parser_logger)
    def __build_tg_cache_item(self) -> GroupCache:
        group = GroupCache(
            group_name=self.group_name,
            group_dir=self.group_content_dir,
            posts=self.posts,
            post_ids=self.post_ids
        )

        return group

    @sync_dec_logger(telegram_parser_logger)
    def __get_media(self, post_id: int, media, path: Path) -> Dict[str, str | Path]:
        log_ = 'Start get media'
        telegram_parser_logger.debug(self.__logging_main_str.format(log_))

        if isinstance(media, MessageMediaContact):
            media_item = {
                'path': path,
                'kwargs': {
                    'phone_number': media.phone_number,
                    'first_name': media.first_name,
                    'last_name': media.last_name,
                    'vcard': media.vcard
                }
            }
        else:
            media_item = {
                'path': path
            }

        log_ = 'Post: ({}) Got media: {}'.format(post_id, media_item)
        telegram_parser_logger.debug(self.__logging_main_str.format(log_))

        return media_item

    @sync_dec_logger(telegram_parser_logger)
    def __get_entity_type(self, type_, post_id: int | str) -> str | None:
        if type_ == 'MessageEntityHashtag':
            entity_type = MessageEntityType.HASHTAG
        elif type_ == 'MessageEntityBotCommand':
            entity_type = MessageEntityType.BOT_COMMAND
        elif type_ == 'MessageEntityUrl':
            entity_type = MessageEntityType.URL
        elif type_ == 'MessageEntityEmail':
            entity_type = MessageEntityType.EMAIL
        elif type_ == 'MessageEntityBold':
            entity_type = MessageEntityType.BOLD
        elif type_ == 'MessageEntityItalic':
            entity_type = MessageEntityType.ITALIC
        elif type_ == 'MessageEntityCode':
            entity_type = MessageEntityType.CODE
        elif type_ == 'MessageEntityPre':
            entity_type = MessageEntityType.PRE
        elif type_ == 'MessageEntityTextUrl':
            entity_type = MessageEntityType.TEXT_LINK
        elif type_ == 'MessageEntityMentionName':
            entity_type = MessageEntityType.TEXT_MENTION
        elif type_ == 'MessageEntityPhone':
            entity_type = MessageEntityType.PHONE_NUMBER
        elif type_ == 'MessageEntityCashtag':
            entity_type = MessageEntityType.CASHTAG
        elif type_ == 'MessageEntityUnderline':
            entity_type = MessageEntityType.UNDERLINE
        elif type_ == 'MessageEntityMention':
            entity_type = MessageEntityType.MENTION
        elif type_ == 'MessageEntityStrike':
            entity_type = MessageEntityType.STRIKETHROUGH
        elif type_ == 'MessageEntitySpoiler':
            entity_type = MessageEntityType.SPOILER
        elif type_ == 'MessageEntityCustomEmoji':
            entity_type = MessageEntityType.CUSTOM_EMOJI
        else:
            entity_type = None

        log_ = 'Post: ({}) Get entity type: {}'.format(post_id, entity_type)
        telegram_parser_logger.debug(self.__logging_main_str.format(log_))

        return entity_type

    @sync_dec_logger(telegram_parser_logger)
    def __get_entities(self, entities, post_id) -> List[MessageEntity] | None:
        log_ = 'Post: ({}) Get entities'.format(post_id)
        telegram_parser_logger.debug(self.__logging_main_str.format(log_))

        data = []

        for ent in entities:
            ent = ent.to_dict()
            type_ = self.__get_entity_type(ent.get('_'), post_id)

            if type_:
                entity = MessageEntity(
                    type=type_,
                    offset=ent.get('offset'),
                    length=ent.get('length'),
                    url=ent.get('url'),
                    language=ent.get('language'),
                    custom_emoji_id=ent.get('document_id')
                )

                data.append(entity)
        if data:
            log_ = 'Post: ({}) Got entities: {}'.format(post_id, data)
            telegram_parser_logger.debug(self.__logging_main_str.format(log_))

            return data
        else:
            log_ = 'Post: ({}) Entities not found'.format(post_id)
            telegram_parser_logger.debug(self.__logging_main_str.format(log_))

            return None

    @sync_dec_logger(telegram_parser_logger)
    def __make_posts(self, posts: list) -> None:
        log_ = 'Start making TGPosts'
        telegram_parser_logger.debug(self.__logging_main_str.format(log_))

        created_posts: List[TGPost] = []

        last_group_id = 0

        for post in posts:
            check_group = post.get('grouped_id')

            media = []

            if check_group:
                if last_group_id == check_group:
                    continue

                group = [p for p in posts if p.get('grouped_id') == check_group]

                text = [p.get('text') for p in group if p.get('text')]
                text = text[0] if text else ''

                entities = [p.get('entities') for p in group if p.get('entities')]
                entities = entities[0] if entities else None

                last_group_id = check_group

            else:
                text = post.get('text', '')
                entities = post.get('entities')

            for item in os.listdir(post.get('local_path')):
                item = post.get('local_path') / item
                item_path: PosixPath = item.absolute()
                suffixes = item.suffixes

                m = create_media_item(suffixes, item_path, post)

                if m:
                    media.append(m)

            if text or media:
                tg_post = TGPost(
                    id_=post.get('id'),
                    local_path=post.get('local_path'),
                    text=text,
                    media=media,
                    entities=entities
                )

                created_posts.append(tg_post)

                log_ = 'Create post: {}'.format(tg_post)
                telegram_parser_logger.debug(self.__logging_main_str.format(log_))

            else:
                log_ = 'Not found text or media in post id={}'.format(post.get('id'))
                telegram_parser_logger.warning(self.__logging_main_str.format(log_))

        self.posts = created_posts

        log_ = 'Completed {} telegram posts: {}'.format(len(self.posts), self.posts)
        telegram_parser_logger.debug(self.__logging_main_str.format(log_))
