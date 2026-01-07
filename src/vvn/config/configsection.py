from configparser import ConfigParser
from pathlib import Path

from .supportedplatform import SupportedPlatform


class ConfigSection:
    def __init__(self, config: ConfigParser, section: str):
        self.section = section
        self.config = config
        if not config.has_section(self.section):
            config.add_section(self.section)

    def __getitem__(self, option: str | tuple) -> bool | int | str | Path:
        default_value = ""
        if isinstance(option, tuple):  # Default value supplied?
            option, default_value = option
            if isinstance(default_value, tuple):  # Platform-dependent default?
                default_value = default_value[SupportedPlatform.current()]
        return self.get_value(option, default_value)

    def __setitem__(self, option: str, value: str | int | bool | Path) -> None:
        self.config[self.section][option] = str(value)

    def getint(self, option: str) -> int | None:
        return self.config.getint(self.section, option)

    def getboolean(self, option: str) -> bool | None:
        return self.config.getboolean(self.section, option)

    def get_value(
        self, option: str, default_value: bool | int | str | Path
    ) -> bool | int | str | Path:
        if not self.config.has_option(self.section, option):
            self.config[self.section][option] = str(default_value)

        if isinstance(default_value, int):
            return int(self.config[self.section][option])
        elif isinstance(default_value, bool):
            return self.config[self.section][option] != "False"
        elif isinstance(default_value, Path):
            return Path(self.config[self.section][option])
        else:
            return self.config[self.section][option]
