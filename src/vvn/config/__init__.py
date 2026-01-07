from configparser import ConfigParser

from .configfile import ConfigFile
from .configsection import ConfigSection

config = ConfigParser()
config_file = ConfigFile(config)  # provides automatic save/laod


def get_section(section: str) -> ConfigSection:
    return ConfigSection(config, section)
