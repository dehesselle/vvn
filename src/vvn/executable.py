import re
import subprocess
from pathlib import Path

from pydantic import BaseModel, Field


class Executable(BaseModel):
    target_name: Path | None = Field(default=None)
    path_in_archive: str = Field(default="")
    version_arg: str = Field(default="")
    version_pattern: str = Field(default="")

    def get_version(self, target_dir: Path | None = None) -> str:
        if target_file := (
            target_dir / self.target_name if target_dir else self.target_name
        ):
            cp = subprocess.run(
                [target_file, self.version_arg],
                encoding="utf-8",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if cp.returncode:
                print(f"TODO failed to execute {target_file}")
                return ""
            else:
                if match := re.match(self.version_pattern, cp.stdout or cp.stderr):
                    return match.group(1)
                else:
                    print(f"TODO failed to version_pattern {self.version_pattern}")
                    return ""
        else:
            print("TODO no filename, can't do anything")

    def exists(self, target_dir: Path) -> bool:
        return (target_dir / self.target_name).exists()
