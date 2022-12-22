import logging.config

from typing import Dict, Any, List
from pathlib import Path

from utils.logging import dict_config
from utils.parsers.meta_display_cls import MetaDisplayCLS


logging.config.dictConfig(dict_config)
vk_post_logger = logging.getLogger('vk_post')


class VKPost(MetaDisplayCLS):
    __slots__ = [
        'id',
        'owner_id',
        'friends_only',
        'from_group',
        'message',
        'attachments',
        'local_path'
    ]

    def __init__(
            self,
            id_: int,
            local_path: Path,
            # для отправки
            owner_id: int = None,
            message: str = '',
            from_group: bool = True,
            friends_only: bool = False,
            attachments: List['Attachment'] | List[None] | None = None

    ):
        """
        `owner_id` идентификатор пользователя или сообщества, на стене которого должна быть опубликована запись.
            (Обратите внимание, идентификатор сообщества в параметре owner_id необходимо указывать со знаком "-" —
            например, owner_id=-1 соответствует идентификатору сообщества ВКонтакте API (club1))

        """
        self.id = id_
        self.local_path = local_path
        # для отправки
        self.owner_id = owner_id
        self.friends_only = 1 if friends_only else 0
        self.from_group = 1 if from_group else 0
        self.message = message
        self.attachments = attachments

    def as_dict(self) -> Dict[str, Any]:
        post_dict = {}

        for atr in self.__slots__:
            if atr == 'id' or atr == 'local_path':
                continue

            if atr == 'attachments':
                post_dict[atr] = ','.join([att.as_string() for att in self.attachments])
                continue

            key = atr
            val = self.__getitem__(key)

            if val:
                post_dict[key] = val

        post = {
            'id': self.id,
            'local_path': self.local_path,
            'owner_id': self.owner_id,
            'message': self.message,
            'attachments': self.attachments,
            'friends_only': self.friends_only,
            'from_group': self.from_group
        }

        vk_post_logger.debug('Make post: {post}'.format(post=post))

        return post_dict


class Attachment(MetaDisplayCLS):
    __slots__ = [
        'id',
        'type',
        'owner_id',
        'url',
        'local_path'
    ]

    def __init__(self, type_: str, owner_id: int, media_id: int, local_path: Path, url: str | None = None):
        """
        `type_` тип медиавложения
            photo — фотография;
            video — видеозапись ;
            audio — аудиозапись;
            doc — документ;
            page — wiki-страница;
            note — заметка;
            poll — опрос;
            album — альбом;
            market — товар;
            market_album — подборка товаров;
            audio_playlist — плейлист с аудио.

        `owner_in` идентификатор владельца медиавложения (обратите внимание, если объект находится в сообществе,
            этот параметр должен быть отрицательным)

        `media_id` идентификатор медиавложения

        `url` одна URL ссылка HTTP/HTTPS протоколы

        :param type_: one of photo/video/audio/doc/page/note/poll/album/market/market_album/audio_playlist
        """
        self.id = media_id
        self.type = type_
        self.owner_id = owner_id
        self.url = url
        self.local_path = local_path

    def as_string(self):
        if self.url:
            return '{}'.format(self.url)
        else:
            return '{type}{owner_id}_{media_id}'.format(
                type=self.type,
                owner_id=self.owner_id,
                media_id=self.id,
            )


## in dev
# class MessageAttachment:
#     def __init__(self, type_: str, owner_id: int, media_id: int, access_key: str = None):
#         """
#         `owner_in` идентификатор владельца медиавложения (обратите внимание, если объект находится в сообществе,
#             этот параметр должен быть отрицательным)
#
#         `media_id` идентификатор медиавложения
#
#         `access_key` В случае, если прикрепляется объект, принадлежащий другому пользователю следует добавлять к
#             вложению его access_key в формате <type><owner_id>_<media_id>_<access_key>
#
#         :param type_: one of photo/video/audio/doc/wall/market/poll
#         """
#         self.type = type_
#         self.owner_id = owner_id
#         self.media_id = media_id
#         self.access_key = access_key
#
#
#
#     def __repr__(self):
#         return '{type}{owner_id}_{media_id}{access_key}'.format(
#             type=self.type,
#             owner_id=self.owner_id,
#             media_id=self.media_id,
#             access_key='_{}'.format(self.access_key) if self.access_key else '',
#         )
#
#     def __str__(self):
#         return self.__repr__()
