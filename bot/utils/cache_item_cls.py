import os

from typing import List

from utils.parsers.VK_parser import VKPost
from utils.parsers.Telegram_parser import TGPost, create_media_item
from utils.parsers.meta_display_cls import MetaDisplayCLS


class PostCacheItem(MetaDisplayCLS):
    __slots__ = [
        'group_id',
        'send_to',
        'post_platform',
        'post_item'
    ]

    def __init__(
            self,
            group_id: int,
            send_to: List[str | int],
            post_item: TGPost | VKPost,
            post_platform: str = 'telegram'
    ):
        self.group_id = group_id
        self.send_to = send_to
        self.post_platform = post_platform
        self.post_item = post_item

    def __build_post(self) -> TGPost:
        if self.post_platform == 'telegram':
            if isinstance(self.post_item, TGPost):
                self.post_item.chat_ids = self.send_to
                return self.post_item

            else:
                local_path = self.post_item.get('local_path')
                media = []

                for item in os.listdir(local_path):
                    item = local_path / item
                    item_path = item.absolute()
                    suffixes = item.suffixes

                    m = create_media_item(suffixes, item_path, self.post_item.as_dict())

                    if m:
                        media.append(m)

                post = TGPost(
                    id_=0,
                    local_path=local_path,
                    send_to=self.send_to,
                    text=self.post_item.message,
                    entities=None,
                    media=media
                )

                return post

        # todo другие платформы

    def to_dict(self):
        self.post_item = self.__build_post()

        return {
            'group_id': self.group_id,
            'send_to': self.send_to,
            'post_platform': self.post_platform,
            'post_item': self.post_item
        }
