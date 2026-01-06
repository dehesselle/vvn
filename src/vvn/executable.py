import re
import subprocess

from pydantic import BaseModel, Field


class Executable(BaseModel):
    target_name: str = Field(default="")
    path_in_archive: str = Field(default="")
    version_arg: str = Field(default="")
    version_pattern: str = Field(default="")

    def get_version(self, filename: str = "") -> str:
        if filename := filename if filename else self.target_name:
            cp = subprocess.run(
                [filename, self.version_arg],
                encoding="utf-8",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if cp.returncode:
                print(f"TODO failed to execute {filename}")
                return ""
            else:
                if match := re.match(self.version_pattern, cp.stdout or cp.stderr):
                    return match.group(1)
                else:
                    print(f"TODO failed to version_pattern {self.version_pattern}")
                    return ""
        else:
            print("TODO no filename, can't do anything")
