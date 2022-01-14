"""
Copyright © 2021 William L Horvath II

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import os
from pathlib import Path
from typing import Final

MAX_READER_COUNT: Final[int] = int(os.environ.get("ID_MAX_READER_COUNT", 1))

_default_base_path: Path = Path(Path.cwd(), "dev_db")
_base_path: str = os.environ.get("ID_BASE_PATH")
BASE_PATH: Final[Path] = Path(_base_path) if _base_path else _default_base_path
if __debug__:
    BASE_PATH.mkdir(mode=510, exist_ok=True, parents=True)

# Configurable because we may be using NFS
MAX_RETRIES: int = int(os.environ.get("ID_MAX_RETRIES", 0))
