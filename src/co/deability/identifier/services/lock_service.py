from collections.abc import Generator
from pathlib import Path
from typing import Final, Optional

from co.deability.identifier.constants.TimeMachineType import TimeMachineType
from co.deability.identifier.services import time_service

LOCK_FILE: Final[str] = ".lock"


def try_lock(id_folder: Path) -> Optional[Path]:
    if is_locked(id_folder=id_folder):
        return None
    try:
        return create_lock(id_folder=id_folder)
    except FileExistsError:
        return None


def create_lock(id_folder: Path) -> Path:
    path: Path = next(lock_pathmaker(id_folder=id_folder))
    path.touch(exist_ok=False)
    return path


def lock_pathmaker(id_folder) -> Generator[Path]:
    yield Path(
        id_folder,
        f"{time_service.time_machine(type=TimeMachineType.MICRO)}.{LOCK_FILE}",
    )


def lock_finder(id_folder: Path) -> Generator[Path]:
    return id_folder.glob(f"*.{LOCK_FILE}")


def next_lock(lock_finder_gen: Generator[Path], lock: Optional[Path] = None):
    locks: list[Path] = list(lock_finder_gen)
    if lock:
        locks.remove(lock)
    yield locks[0] if locks else None


def release_lock(lock: Path) -> None:
    lock.unlink(missing_ok=False)


def is_locked(id_folder: Path) -> bool:
    return next_lock(lock_finder_gen=lock_finder(id_folder=id_folder)) is not None


def release_all_locks(id_folder: Path) -> None:
    for lock in lock_finder(id_folder=id_folder):
        release_lock(lock)
