import logging.config

from typing import List, Dict, Any
from pathlib import PosixPath
from aiogram.types import (
    MessageEntity,
    MessageEntityType,
    MediaGroup,
    InputFile,
    InputMediaPhoto,
    InputMediaVideo,
    InputMediaAudio,
    InputMediaDocument,
    InputMediaAnimation
)

from utils.logging import dict_config
from utils.parsers.meta_display_cls import MetaDisplayCLS

logging.config.dictConfig(dict_config)
tg_post_logger = logging.getLogger('tg_post')


class TGPost(MetaDisplayCLS):
    __slots__ = [
        'id',
        'local_path',
        'chat_ids',
        'text',
        'media',
        'entities'
    ]

    def __init__(
            self,
            id_: int,
            local_path: str,
            text: str,
            send_to: List[int | str] = None,
            entities: List[MessageEntity] = None,
            media: List['Media'] = None
    ):
        self.id = id_
        self.local_path = local_path
        # для отправки
        self.chat_ids = send_to
        self.text = text
        self.entities = entities
        self.media = media

    async def for_send_in_tg(self):
        if self.media:
            media_group = []

            for i, m in enumerate(self.media):
                if m.type == 'photo':
                    input_type = InputMediaPhoto
                elif m.type == 'video':
                    input_type = InputMediaVideo
                elif m.type == 'audio':
                    input_type = InputMediaAudio
                elif m.type == 'doc':
                    input_type = InputMediaDocument
                elif m.type == 'animation':
                    input_type = InputMediaAnimation
                elif m.type == 'voice':
                    voice = InputFile(m.location)
                    media_dict = {
                        'type': 'voice',
                        'chat_ids': self.chat_ids,
                        'voice': voice,
                        'caption': self.text,
                        'caption_entities': self.entities
                    }

                    self.__make_log(media_dict)

                    return media_dict

                elif m.type == 'sticker':
                    sticker = InputFile(m.location)
                    media_dict = {
                        'type': 'sticker',
                        'chat_ids': self.chat_ids,
                        'sticker': sticker,
                    }

                    self.__make_log(media_dict)

                    return media_dict

                elif m.type == 'contact':
                    kwargs = m.kwargs
                    media_dict = {
                        'type': 'contact',
                        'chat_ids': self.chat_ids
                    }
                    media_dict.update(kwargs)

                    self.__make_log(media_dict)

                    return media_dict

                else:
                    tg_post_logger.warning(
                        'Invalid media type: id - {}, path - {}, text - {}'.format(
                            self.id,
                            self.local_path,
                            self.text
                        )
                    )

                    continue

                if i == 0:
                    media = input_type(
                        media=InputFile(m.location),
                        caption=self.text if self.text else None,
                        caption_entities=self.entities
                    )
                else:
                    media = input_type(media=InputFile(m.location))

                media_group.append(media)

            media_group = MediaGroup(media_group)

            self.__make_log(media_group)

            return {
                'type': 'group',
                'chat_ids': self.chat_ids,
                'media': media_group
            }

        else:

            self.__make_log()

            return {
                'type': 'text',
                'chat_ids': self.chat_ids,
                'text': self.text,
                'entities': self.entities
            }

    def __make_log(self, media: Any | None = None) -> None:
        post = {
            'id': self.id,
            'local_path': self.local_path,
            'chat_ids': self.chat_ids,
            'text': self.text,
            'entities': self.entities,
            'media': media
        }

        tg_post_logger.debug('Make post: {post}'.format(post=post))


class Media(MetaDisplayCLS):
    __slots__ = [
        'type',
        'location',
        'kwargs'
    ]

    def __init__(self, type_: str, location: PosixPath, kwargs: Dict[str, Any] = None):
        """
        `type_` on of photo/video
        :param type_: string
        :param location: PosixPath
        """
        self.type = type_
        self.location = location
        self.kwargs = kwargs


class Entity:
    def __init__(self, **atr):
        self.__unsupported_type = False

        for key, val in atr.items():
            if key == '_':
                key = 'type'

                if val == 'MessageEntityHashtag':
                    val = MessageEntityType.HASHTAG
                elif val == 'MessageEntityBotCommand':
                    val = MessageEntityType.BOT_COMMAND
                elif val == 'MessageEntityUrl':
                    val = MessageEntityType.URL
                elif val == 'MessageEntityEmail':
                    val = MessageEntityType.EMAIL
                elif val == 'MessageEntityBold':
                    val = MessageEntityType.BOLD
                elif val == 'MessageEntityItalic':
                    val = MessageEntityType.ITALIC
                elif val == 'MessageEntityCode':
                    val = MessageEntityType.CODE
                elif val == 'MessageEntityPre':
                    val = MessageEntityType.PRE
                elif val == 'MessageEntityTextUrl':
                    val = MessageEntityType.TEXT_LINK
                elif val == 'MessageEntityMentionName':
                    val = MessageEntityType.TEXT_MENTION
                elif val == 'MessageEntityPhone':
                    val = MessageEntityType.PHONE_NUMBER
                elif val == 'MessageEntityCashtag':
                    val = MessageEntityType.CASHTAG
                elif val == 'MessageEntityUnderline':
                    val = MessageEntityType.UNDERLINE
                elif val == 'MessageEntityMention':
                    val = MessageEntityType.MENTION
                elif val == 'MessageEntityStrike':
                    val = MessageEntityType.STRIKETHROUGH
                elif val == 'MessageEntitySpoiler':
                    val = MessageEntityType.SPOILER
                elif val == 'MessageEntityCustomEmoji':
                    val = MessageEntityType.CUSTOM_EMOJI
                # elif val == 'MessageEntityBlockquote':
                #     val = ''
                # elif val == 'MessageEntityBankCard':
                #     val = ''
                else:
                    self.__unsupported_type = True
                    break

            self.__setattr__(key, val)

    def to_dict(self) -> Dict[str, str | int] | None:
        if self.__unsupported_type:
            return None

        entity_dict = {}

        for key, val in self.__dict__.items():
            entity_dict[key] = val

        return entity_dict
