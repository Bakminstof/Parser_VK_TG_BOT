from typing import List

from aiogram.types import Message
from aiogram.dispatcher.filters import Filter


class TextFilter(Filter):
    def __init__(self, text: str | List[str]):
        self.text = text

    async def check(self, message: Message) -> bool:
        if isinstance(self.text, list):
            if message.text in self.text:
                return True
            else:
                return False
        else:
            if message.text == self.text:
                return True
            else:
                return False
