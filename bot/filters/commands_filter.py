from aiogram.types import Message
from aiogram.dispatcher.filters import Filter


class CommandFilter(Filter):
    def __init__(self, command: str, prefix: str = '/'):
        self.command = command
        self.prefix = prefix

    async def check(self, message: Message) -> bool:
        if message.text == self.prefix + self.command:
            return True
        else:
            return False
