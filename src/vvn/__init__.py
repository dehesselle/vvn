from argparse import ArgumentParser
from enum import StrEnum

from .products import Products
from .version import VERSION


class Command(StrEnum):
    LIST = "list"
    INSTALL = "install"
    UNINSTALL = "uninstall"
    UPDATE = "update"


def list_products(show_all: bool = False):
    products = Products()
    products.print_status(show_all)


def cli() -> None:
    arg_parser = ArgumentParser(description="manage tools")
    arg_parser.add_argument("--version", action="version", version=f"vvn {VERSION}")
    command_parser = arg_parser.add_subparsers(
        help="available commands", dest="command"
    )

    list_command_parser = command_parser.add_parser(
        Command.LIST, help="list installed tools"
    )
    list_command_parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        required=False,
        help="show all available tools",
    )

    args = arg_parser.parse_args()

    match args.command:
        case Command.LIST:
            list_products(args.all)
        case _:
            arg_parser.print_usage()


def main() -> None:
    cli()
