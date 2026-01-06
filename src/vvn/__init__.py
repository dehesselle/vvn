import requests
from bs4 import BeautifulSoup
import re
import subprocess
from pathlib import Path
from urlpath import URL


from fsspec.implementations.memory import MemoryFileSystem
from fsspec.implementations.zip import ZipFileSystem
from fsspec.implementations.tar import TarFileSystem


class Executable:
    def __init__(self, filename: str, version_arg: str, version_pattern: str):
        self.filename = filename
        self.version_arg = version_arg
        self.version_pattern = version_pattern

    @property
    def version(self) -> str:
        cp = subprocess.run(
            [self.filename, self.version_arg],
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if cp.returncode:
            print(f"TODO failed to execute {self.filename}")
            return ""
        else:
            if match := re.match(self.version_pattern, cp.stdout or cp.stderr):
                return match.group(1)
            else:
                print(f"TODO failed to version_pattern {self.version_pattern}")
                return ""


class GitHubRelease:
    def __init__(
        self,
        org: str,
        project: str,
        artifact_pattern: str,
        version_pattern: str = r"v[0-9]+\.[0-9]+\.[0-9]",
    ):
        self.org = org
        self.project = project
        self.artifact_pattern = artifact_pattern
        self.version_pattern = version_pattern
        self._release_tags = list()

    @property
    def release_tags(self) -> list[str]:
        if not self._release_tags:
            for page_no in range(3):
                html = requests.get(
                    f"https://github.com/{self.org}/{self.project}/releases?page={page_no}"
                ).content
                soup = BeautifulSoup(html, "html.parser")

                for tag in soup.find_all(
                    "a", href=re.compile(f"{self.org}/{self.project}/tree")
                ):
                    self._release_tags.append(tag.get("href").split("/")[-1])

        return self._release_tags

    @property
    def latest_version(self) -> str:
        versions = [
            tag for tag in self.release_tags if re.match(self.version_pattern, tag)
        ]
        if versions:
            versions.sort(reverse=True)
            return versions[0]
        else:
            return ""

    def get_download_url(self, version: str):
        html = requests.get(
            f"https://github.com/{self.org}/{self.project}/releases/expanded_assets/{version}"
        ).content
        soup = BeautifulSoup(html, "html.parser")
        html_section = soup.find(
            "a",
            href=re.compile(
                re.escape(f"/{self.org}/{self.project}/releases/download/{version}/")
                + self.artifact_pattern
            ),
        )

        return "https://github.com" + html_section.get("href") if html_section else ""


class Artifact:
    def __init__(
        self,
        url: URL,
        target_name: str = "",
        path_in_archive: Path | None = None,
    ):
        self.url = url
        self.target_name = target_name
        self.path_in_archive = path_in_archive
        self.mem_fs = MemoryFileSystem()

    @property
    def is_archive(self) -> bool:
        if self.file.suffix == ".exe":
            return False
        else:
            return True

    def _download(self):
        response = self.url.get()
        if response.ok:
            with self.mem_fs.open(self.url.name, "wb") as file:
                file.write(response.content)

    def install(self, target_dir: Path):
        if not self.mem_fs.ls("/"):
            self._download()

        with self.mem_fs.open(self.url.name, "rb") as file:
            if self.url.suffix == ".exe":
                self.mem_fs.get_file(self.url.name, (self.target_name or self.url.name))
            elif self.url.suffix == ".zip":
                zip_fs = ZipFileSystem(file)
                zip_fs.get_file(
                    self.path_in_archive,
                    target_dir / (self.target_name or self.path_in_archive.name),
                )
            elif len(self.url.suffixes) == 2 and self.url.suffix[0] == ".tar":
                tar_fs = TarFileSystem(file)
                tar_fs.get_file(
                    self.path_in_archive,
                    target_dir / (self.target_name or self.path_in_archive.name),
                )
            else:
                print("TODO unknown suffix")


# class Package:
#     def __init__(self, executable, ):
#         pass


def main() -> None:
    print("Hello from vvn!")
    # session = HTMLSession()
    # r = session.get("https://github.com/kovidgoyal/kitty/releases")
    # for item in r.html.links:
    #     if "archive/refs/tags" in item:
    #         print(item)
    #     if "releases/download" in item:
    #         print(item)
    # print("------------")
    # r = session.get("https://github.com/kovidgoyal/kitty/releases/tag/v0.45.0")

    a = Artifact(
        URL("http://46.224.71.166:8000/awscred_msvc-static-2.zip"),
        path_in_archive=Path("awscred.exe"),
    )
    a.install(Path("C:/Users/Rene/Downloads"))

    exit()

    exe = Executable("moor.exe", "--version", r"(v[0-9]+\.[0-9]+\.[0-9])")
    print(exe.version)
    exit()

    ghr = GitHubRelease("kovidgoyal", "kitty", r"kitty-.*\.dmg")
    print(ghr.get_download_url("v0.45.0"))
    # print(ghr.latest_version)
    exit()

    mylist = ghr.get_release_tags()
    for i in mylist:
        v = Version(i)
        print(v)

    print(mylist)
    print(mylist[2])
    print(type(mylist))
    # for tag in ghr.get_release_tags():
    #    print(tag)

    exit()
    response = requests.get("https://github.com/kovidgoyal/kitty/releases")
    html = response.content

    soup = BeautifulSoup(html, "html.parser")
    for f in soup.find_all("h2", attrs={"class": "sr-only"}):
        print(f)

    print("----------------")
    for g in soup.find_all("a", href=re.compile("kovidgoyal/kitty/tree")):
        print(g.get("href"))

    print("----------------")
    exit()
    response = requests.get(
        "https://github.com/kovidgoyal/kitty/releases/expanded_assets/v0.45.0"
    )
    html = response.content

    soup = BeautifulSoup(html, "html.parser")
    for f in soup.find_all("a"):
        print(f.get("href"))

    exit()
    print(len(f))
    # print(f)
    print(f[1])
    g = soup.find

    f.attr
    # for item: HTMLResponse in r.html.links:
    #     print(item)
