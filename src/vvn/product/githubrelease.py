import re

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel
from semver import Version
from urlpath import URL

import vvn.config as config

cfg = config.get_section("github")

PARSE_RELEASE_PAGES = (
    "parse_release_pages",
    2,
)  # collect release tags from this many pages


class GitHubRelease(BaseModel):
    organization: str
    project: str
    artifact_pattern: str
    version_pattern: str

    _release_tags = list()

    @property
    def release_tags(self) -> list[str]:
        if not self._release_tags:  # If we haven't collected any release tags yet:
            for page_no in range(cfg[PARSE_RELEASE_PAGES]):
                html = requests.get(
                    f"https://github.com/{self.organization}/{self.project}/releases?page={page_no}"
                ).content
                soup = BeautifulSoup(html, "html.parser")

                for tag in soup.find_all(
                    "a",
                    href=re.compile(
                        re.escape(f"{self.organization}/{self.project}/tree")
                    ),
                ):
                    # The tag comes after the final slash.
                    self._release_tags.append(tag.get("href").split("/")[-1])

        return self._release_tags

    @property
    def latest_version(self) -> str:
        try:
            # Try to interpet the versions as semver to enhance the sort
            # that follows.
            versions = [
                Version.parse(re.match(self.version_pattern, tag).group(1))
                for tag in self.release_tags
                if re.match(self.version_pattern, tag)
            ]
        except ValueError:
            # Keep verions as arbitrary strings. The sort that follows might
            # yield undesired results (e.g. "2.9.0" > "2.10.0").
            versions = [
                re.match(self.version_pattern, tag).group(1)
                for tag in self.release_tags
                if re.match(self.version_pattern, tag)
            ]

        if versions:
            versions.sort(reverse=True)
            return str(versions[0])
        else:
            return ""

    def get_download_url(self, version: str) -> URL | None:
        html = requests.get(
            f"https://github.com/{self.organization}/{self.project}/releases/expanded_assets/{version}"
        ).content
        soup = BeautifulSoup(html, "html.parser")
        html_section = soup.find(
            "a",
            href=re.compile(
                re.escape(
                    f"/{self.organization}/{self.project}/releases/download/{version}/"
                )
                + self.artifact_pattern
            ),
        )

        return (
            URL("https://github.com") / html_section.get("href")
            if html_section
            else None
        )
