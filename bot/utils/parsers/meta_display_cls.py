from typing import Any


class MetaDisplayCLS:
    __slots__ = []

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

    def __repr__(self) -> str:
        name = self.__class__.__name__
        args = []

        for atr in self.__slots__:
            key = atr
            val = self.__getitem__(key)

            cur_pair = "{k}={v}".format(k=key, v=val if type(val) is not str else "'{}'".format(val))

            args.append(
                cur_pair
            )

        return "{name_cls}({args})".format(name_cls=name, args=', '.join(args))

    def __str__(self) -> str:
        return self.__repr__()

    def get(self, item) -> Any:
        return getattr(self, item)
