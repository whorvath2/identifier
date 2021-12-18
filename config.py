import os
from pathlib import Path
from typing import Final

MAX_READER_COUNT: Final[int] = int(os.environ.get("ID_MAX_READER_COUNT", 1))

_default_base_path: Path = Path(Path.cwd(), "dev_db")
_base_path: str = os.environ.get("ID_BASE_PATH")
BASE_PATH: Final[Path] = Path(_base_path) if _base_path else _default_base_path

# Configurable because we may be using NFS
MAX_RETRIES: int = int(os.environ.get("ID_MAX_RETRIES", 0))
