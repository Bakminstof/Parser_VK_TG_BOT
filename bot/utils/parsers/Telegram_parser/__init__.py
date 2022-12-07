from .tg_post_cls import TGPost, Media, Entity
from .telegram_parser import TelegramParser, create_media_item, create_tg_client, get_entity

__all__ = [
    'TelegramParser',
    'create_media_item',
    'create_tg_client',
    'get_entity',
    'TGPost',
    'Media',
    'Entity'
]
