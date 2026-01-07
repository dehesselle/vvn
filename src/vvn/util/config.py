# SPDX-FileCopyrightText: 2026 René de Hesselle <dehesselle@web.de>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import configparser
import platform
from enum import IntEnum
from pathlib import Path

import platformdirs

config = configparser.ConfigParser()
ini_file = (
    Path(
        platformdirs.user_config_dir(
            appauthor=False,
            appname="vvn",
            ensure_exists=True,
        )
    )
    / "config.ini"
)


class Platform(IntEnum):
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


class ConfigSection:
    def __init__(self, section: str, config=config):
        self.section = section
        self.config = config
        if not config.has_section(self.section):
            config.add_section(self.section)

    def __getitem__(self, option: str | tuple) -> bool | int | str | Path:
        default_value = ""
        if isinstance(option, tuple):  # Default value supplied?
            option, default_value = option
            if isinstance(default_value, tuple):  # Platform-dependent default?
                default_value = default_value[Platform.current()]
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


def load() -> None:
    if ini_file.exists():
        config.read(ini_file)


def save() -> None:
    ini_file.parent.mkdir(parents=True, exist_ok=True)
    with open(ini_file, "w") as file:
        config.write(file)


def getInt(section: str, option: str, fallback: int = -1) -> int:
    try:
        return config.getint(section, option)
    except configparser.NoOptionError:
        if not config.has_section(section):
            config.add_section(section)
        config.set(section, option, str(fallback))
    return config.getint(section, option)


def getStr(section: str, option: str, fallback: str = "") -> str:
    try:
        return config.get(section, option)
    except configparser.NoOptionError:
        if not config.has_section(section):
            config.add_section(section)
        config.set(section, option, fallback)
    return config.get(section, option)


def exists(section: str, option: str) -> bool:
    return config.has_option(section, option)
