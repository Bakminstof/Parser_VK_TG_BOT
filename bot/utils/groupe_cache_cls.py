from typing import List
from pathlib import Path

from utils.parsers.VK_parser import VKPost
from utils.parsers.Telegram_parser import TGPost
from utils.parsers.meta_display_cls import MetaDisplayCLS


class GroupCache(MetaDisplayCLS):
    __slots__ = [
        'group_name',
        'group_dir',
        'posts',
        'post_ids'
    ]

    def __init__(self, group_name: str, group_dir: Path, posts: List[TGPost | VKPost], post_ids: List[int]):
        """

        :param group_name: str
        :param posts: List[TGPost | VKPost]
        :param post_ids: List[int]
        """
        self.group_name = group_name
        self.group_dir = group_dir
        self.posts = posts
        self.post_ids = post_ids
