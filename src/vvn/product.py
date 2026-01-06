import json
import platform
from importlib.resources import files

from pydantic import BaseModel
from semver import Version

from .githubrelease import GitHubRelease
from .releaseartifact import ReleaseArtifact

REPOSITORY = files("vvn.repository")


class Product(BaseModel):
    github_release: GitHubRelease
    release_artifact: ReleaseArtifact

    def print_status(self):
        executable = self.release_artifact.executables[0]
        installed_ver = executable.get_version()
        latest_ver = self.github_release.latest_version
        confidence = ""

        try:
            installed_ver = Version.parse(installed_ver)
            latest_ver = Version.parse(latest_ver)
        except ValueError:
            confidence = "(?)"

        print(
            f"{executable.target_name:25} "
            f"{str(installed_ver):15} {str(latest_ver):15} "
            f"{confidence}"
        )


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

    def print_status(self):
        print("product                   installed       latest")
        print("------------------------- --------------- ---------------")
        for product in self.products:
            product.print_status()
