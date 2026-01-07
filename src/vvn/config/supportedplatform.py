import platform
from enum import IntEnum


class SupportedPlatform(IntEnum):
    DARWIN = 0
    LINUX = 1
    WINDOWS = 2

    @classmethod
    def current(cls) -> int:
        match platform.system():
            case "Darwin":
                return cls.DARWIN
            case "Linux":
                return cls.LINUX
            case "Windows":
                return cls.WINDOWS
            case _:
                raise ValueError(f"unsupported platform {platform.system()}")
