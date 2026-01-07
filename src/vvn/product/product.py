from pathlib import Path

from pydantic import BaseModel
from semver import Version

import vvn.config as config

from .githubrelease import GitHubRelease
from .releaseartifact import ReleaseArtifact

cfg = config.get_section("product")

INSTALL_DIR = (
    "install_dir",
    (
        Path.home() / ".local/bin",
        Path.home() / ".local/bin",
        Path.home() / "AppData/Local/bin",
    ),
)


class Product(BaseModel):
    github_release: GitHubRelease
    release_artifact: ReleaseArtifact

    def print_status(self):
        executable = self.release_artifact.executables[0]
        installed_ver = executable.get_version(cfg[INSTALL_DIR])
        latest_ver = self.github_release.latest_version
        confidence = ""

        try:
            installed_ver = Version.parse(installed_ver)
            latest_ver = Version.parse(latest_ver)
        except ValueError:
            if (
                installed_ver
            ):  # Determine confidence only if we have an installed product.
                # If we weren't able to parse the version into semver, we have
                # low confidence.
                confidence = "(?)"

        print(
            f"{str(executable.target_name):25} "
            f"{str(installed_ver):15} {str(latest_ver):15} "
            f"{confidence}"
        )

    def is_installed(self) -> bool:
        executable = self.release_artifact.executables[0]
        return executable.exists(cfg[INSTALL_DIR])
