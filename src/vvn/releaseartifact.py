from pathlib import Path

from fsspec.implementations.memory import MemoryFileSystem
from fsspec.implementations.tar import TarFileSystem
from fsspec.implementations.zip import ZipFileSystem
from pydantic import BaseModel, Field
from urlpath import URL

from .executable import Executable


class ReleaseArtifact(BaseModel):
    executables: list[Executable]

    _url: URL
    _mem_fs = MemoryFileSystem()

    def _download(self):
        try:
            response = self._url.get()
            if response.ok:  # Download successful?
                # Save file to memory.
                with self._mem_fs.open(self._url.name, "wb") as file:
                    file.write(response.content)
            else:
                print("TODO download failed")
        except Exception:
            print("TODO download failed")

    def install(self, target_dir: Path):
        if not self._mem_fs.ls("/"):
            self._download()

        if self._mem_fs.ls("/"):
            with self._mem_fs.open(self._url.name, "rb") as file:
                if self._url.suffix == ".exe":
                    self._mem_fs.get_file(
                        self._url.name, self.target_name or self._url.name
                    )
                elif self._url.suffix == ".zip":
                    zip_fs = ZipFileSystem(file)
                    zip_fs.get_file(
                        self.path_in_archive,
                        target_dir / (self.target_name or self.path_in_archive.name),
                    )
                elif len(self._url.suffixes) == 2 and self._url.suffix[0] == ".tar":
                    tar_fs = TarFileSystem(file)
                    tar_fs.get_file(
                        self.path_in_archive,
                        target_dir / (self.target_name or self.path_in_archive.name),
                    )
                else:
                    print("TODO unknown suffix")
        else:
            print("TODO nothing was downloaded")
