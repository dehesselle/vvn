import json
import platform
from importlib.resources import files

from .product import Product

REPOSITORY = files("vvn.product.repository")


class Products:
    def __init__(self):
        self.products: list[Product] = list()
        self._load()

    def _load(self):
        for file in REPOSITORY.iterdir():
            if file.suffix == ".json" and all(
                _ in file.suffixes
                for _ in [f".{platform.system()}", f".{platform.machine()}"]
            ):
                product_json = json.loads(file.read_text())
                self.products.append(Product(**product_json))

    def print_status(self, show_all: bool = False):
        if self.products:
            print("product                   installed       latest")
            print("------------------------- --------------- ---------------")
            for product in self.products:
                if product.is_installed() or show_all:
                    product.print_status()
        else:
            print(f"No products found for {platform.system()} / {platform.machine()}.")
