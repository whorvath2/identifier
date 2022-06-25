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
import hashlib
import json
import os
import uuid
from pathlib import Path
from typing import Final, Any, Dict, Optional, Iterator

from co.deability.identifier import config
from co.deability.identifier.api import repositories
from co.deability.identifier.api.repositories import BASE_PATH
from co.deability.identifier.errors.BadRequestError import BadRequestError
from co.deability.identifier.services import time_service

DIGEST_SIZE: Final[int] = int(config.IDENTIFIER_LENGTH / 2)
DELETED_ENTITY_PATH: Final[Path] = Path(BASE_PATH, "deleted_entity.json")
if not DELETED_ENTITY_PATH.exists():
    DELETED_ENTITY_PATH.write_text("{}")


def data_exists(identifier: str) -> bool:
    """
    Returns true if there is data (currently an entity or an index) available through the supplied
    identifier.

    :param identifier:
    :return:
    """
    entity_file: Path = next(get_data_file_paths(identifier=identifier), None)
    data = (
        json.loads(entity_file.read_text(encoding=config.TEXT_ENCODING))
        if entity_file
        else None
    )
    return data is not None and data != {}


# @cache
def find_identifier(data: Dict[str, Any]) -> str:
    """
    Returns an identifier associated with the supplied data if one exists and has not been archived;
    otherwise returns None.

    :param data: The data for which an identifier is sought.
    :return:
    """
    check_if_empty(data=data)
    identifier: str = calculate_id_from_data(data=data)
    return identifier if data_exists(identifier=identifier) else None


# @cache
def calculate_id_from_data(data: Dict[str, Any]) -> str:
    """
    Returns a string of fixed length that is derived from the contents of the supplied data.
    The string is intended to be used in the creation of an identifier in an entity or index
    repository.

    :param data: The data from which the id will be calculated.
    :return: A string of fixed length which may be used to create an identifier.

    """
    as_json: str = json.dumps(data)
    return hashlib.blake2b(
        bytes(as_json.encode(config.TEXT_ENCODING)),
        digest_size=DIGEST_SIZE,
        usedforsecurity=False,
    ).hexdigest()


def calculate_new_data_path(identifier_path: Path) -> Path:
    """
    Returns a path to a file in which the data represented by the supplied identifier
    may be written. The returned path has not been created, nor checked for existence; it
    falls to the user of this method to create the file.

    :param identifier: The identifier for the data that may be written to the file represented by
    the returned path.
    :return: A path to a file in which data regarding the entity may be written.
    """
    timestamp: str = f"{time_service.now_epoch_micro()}".zfill(repositories.TIME_LENGTH)
    return Path(identifier_path, f"{timestamp}{repositories.DATA_FILE}")


def get_data_file_paths(identifier: str) -> Iterator[Path]:
    """
    Returns a generator that produces all data file paths associated with a particular identifier.
    Note that some or all of the file paths may be symlinks.

    :param identifier: The identifier that must exist and may contain at least one data file.
    :return: a generator that produces all data file paths associated with a particular identifier.
    """
    id_folder: Path = repositories.calculate_path(identifier=identifier)
    return id_folder.glob(f"*{repositories.DATA_FILE}")


def check_if_empty(data: Optional[Dict[str, Any]]) -> None:
    """
    Raises a BadRequestError if the supplied data is either None or an empty dictionary, meaning its
    contents can't be processed.

    :param data: The dictionary to be checked for having processable contents.
    """
    if not data:
        raise BadRequestError(
            message="The supplied entity is empty and cannot be processed."
        )


def _tmp_file() -> str:
    return f"{str(uuid.uuid4())}.tmp"


def update_link(old_path: Path, new_path: Path) -> None:
    assert new_path.exists(), f"{new_path} doesn't exist"
    assert old_path.exists()
    temp_path: Path = Path(old_path.parent, _tmp_file())
    os.symlink(new_path, temp_path)
    os.rename(temp_path, old_path)
    assert new_path.exists()
    assert old_path.is_symlink()
    assert old_path.exists()
