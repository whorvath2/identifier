"""
Copyright © 2022 William L Horvath II

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
from typing import Dict, Any, Optional, Final

from co.deability.identifier import config
from co.deability.identifier.api import repositories
from co.deability.identifier.api.repositories import BASE_PATH
from co.deability.identifier.errors.BadRequestError import BadRequestError
from co.deability.identifier.errors.IllegalArgumentError import IllegalArgumentError
from co.deability.identifier.errors.NoSuchEntityError import NoSuchEntityError
from co.deability.identifier.services import time_service

"""
A repository that uses an entity's data to create an identifier for the entity.

#todo add versioning for entity files.
"""


DELETED_ENTITY_PATH: Final[Path] = Path(BASE_PATH, "deleted_entity.json")
if not DELETED_ENTITY_PATH.exists():
    DELETED_ENTITY_PATH.write_text("{}")


def create_entity(entity: Dict[str, Any]) -> Path:
    _check_entity(entity=entity)
    identifier: str = _calculate_identifier_from_entity(entity=entity)
    identifier_path: Path = repositories.create_identifier_path(identifier=identifier)
    new_data_path: Path = _calculate_new_entity_path(identifier_path=identifier_path)
    new_data_path.write_text(data=json.dumps(entity), encoding=config.TEXT_ENCODING)
    return new_data_path


def read_entity(identifier: str) -> Optional[Dict[str, Any]]:
    repositories.check_identifier(identifier=identifier)
    entity_file: Path = _get_entity_file_path(identifier=identifier)
    result = (
        json.loads(entity_file.read_text(encoding=config.TEXT_ENCODING))
        if entity_file
        else None
    )
    return result


def find_entity(entity: Dict[str, Any]) -> str:
    _check_entity(entity=entity)
    identifier: str = _calculate_identifier_from_entity(entity=entity)
    return identifier


def update_entity(identifier: str, entity: Dict[str, Any]) -> str:
    """
    Returns a new identifier for the supplied entity which was previously identified by the
    supplied identifier.

    If the entity's new identifier is equal to the previous identifier, the timestamp on the data
    file is updated (though its contents will remain unchanged), and the previous identifier is
    returned.

    If the entity's new identifier is different, but resolves to a directory which already exists
    and contains a file, and the file is not a symlink to another file,

    If the supplied entity would result in the re-creation of an old version of itself, any symlinks
    from intervening versions are updated to point to the latest version.

    :param identifier:
    :param entity:
    :return:
    """
    repositories.check_identifier(identifier)
    _check_entity(entity=entity)
    new_identifier: str = _calculate_identifier_from_entity(entity=entity)
    old_data_path: Path = _get_entity_file_path(identifier=identifier)
    if not old_data_path:
        raise NoSuchEntityError(
            message=f"The supplied identifier is recognized, but no corresponding entity was found, so the update could not be applied."
        )
    if new_identifier == identifier:
        new_data_path: Path = _calculate_new_entity_path(
            identifier_path=old_data_path.parent
        )
        new_data_path.write_text(data=json.dumps(entity), encoding=config.TEXT_ENCODING)
        if old_data_path.is_symlink():
            _link_last(first_path=old_data_path.readlink(), target_path=new_data_path)
        _update_link(old_path=old_data_path, new_path=new_data_path)
    else:
        new_identifier_path: Path = repositories.calculate_path(
            identifier=new_identifier
        )
        if not new_identifier_path.exists():
            repositories.create_identifier_path(identifier=new_identifier)
            new_data_path: Path = _calculate_new_entity_path(
                identifier_path=new_identifier_path
            )
            new_data_path.write_text(
                data=json.dumps(entity), encoding=config.TEXT_ENCODING
            )
            _update_link(old_path=old_data_path, new_path=new_data_path)
        else:
            update_entity(identifier=new_identifier, entity=entity)
    return new_identifier


def _link_last(first_path: Path, target_path: Path):
    if first_path:
        if first_path.is_symlink():
            next_path = first_path.readlink()
            while next_path and next_path.is_symlink():
                current_path = next_path
                next_path = next_path.readlink()
                if not next_path:
                    _update_link(old_path=current_path, new_path=target_path)
            if next_path:
                _update_link(old_path=next_path, new_path=target_path)
        else:
            _update_link(old_path=first_path, new_path=target_path)


def delete_entity(identifier: str) -> None:
    repositories.check_identifier(identifier=identifier)
    entity_path: Path = _get_entity_file_path(identifier=identifier)
    print(f"entity_path 1: {entity_path}")
    if not entity_path:
        raise NoSuchEntityError(
            message=f"There is no entity matching the supplied identifier, so no entity was deleted."
        )
    elif entity_path.is_symlink():
        _link_last(
            first_path=entity_path.readlink(),
            target_path=DELETED_ENTITY_PATH,
        )
    _update_link(old_path=entity_path, new_path=DELETED_ENTITY_PATH)
    assert entity_path.is_symlink()
    assert entity_path.exists()


def does_entity_exist(id_or_entity: [str, Dict[str, Any]]):
    if isinstance(id_or_entity, str):
        return read_entity(identifier=id_or_entity) is not None
    elif isinstance(id_or_entity, dict):
        return find_entity(entity=id_or_entity) is not None
    else:
        raise IllegalArgumentError(
            message="id_or_entity must be a string or dictionary."
        )


DIGEST_SIZE: Final[int] = int(config.IDENTIFIER_LENGTH / 2)


def _calculate_identifier_from_entity(entity: Dict[str, Any]) -> str:
    _check_entity(entity=entity)
    as_json: str = json.dumps(entity)
    return hashlib.blake2b(
        bytes(as_json.encode(config.TEXT_ENCODING)),
        digest_size=DIGEST_SIZE,
        usedforsecurity=False,
    ).hexdigest()


def _calculate_new_entity_path(identifier_path: Path) -> Path:
    """
    Returns a path to a file in which data about the entity represented by the supplied identifier
    may be written. The returned path has not been created, nor checked for existence; it
    falls to the user of this method to create the file.

    :param identifier: The identifier for the entity whose data may be written to a file at
    the returned path.
    :return: A possible path to a file in which data regarding the entity may be written.
    """
    timestamp: str = f"{time_service.now_epoch_micro()}".zfill(repositories.TIME_LENGTH)
    return Path(identifier_path, f"{timestamp}{repositories.DATA_FILE}")


def _get_entity_file_path(identifier: str) -> Optional[Path]:
    id_folder: Path = repositories.calculate_path(identifier=identifier)
    return next(id_folder.glob(f"*{repositories.DATA_FILE}"), None)


def _check_entity(entity: Optional[Dict[str, Any]]) -> None:
    """
    Raises a BadRequestError if the supplied entity is either None or an empty dictionary.
    :param entity: The entity to be checked for having processable data.
    """
    if not entity:
        raise BadRequestError(
            message="The supplied entity is empty and cannot be processed."
        )


def _tmp_file() -> str:
    return f"{str(uuid.uuid4())}.tmp"


def _update_link(old_path: Path, new_path: Path) -> None:
    assert new_path.exists(), f"{new_path} doesn't exist"
    assert old_path.exists()
    temp_path: Path = Path(old_path.parent, _tmp_file())
    os.symlink(new_path, temp_path)
    os.rename(temp_path, old_path)
    assert new_path.exists()
    assert old_path.is_symlink()
    assert old_path.exists()
