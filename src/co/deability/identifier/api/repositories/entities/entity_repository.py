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
import json
from pathlib import Path
from typing import Dict, Any, Optional

from co.deability.identifier import config
from co.deability.identifier.api import repositories
from co.deability.identifier.api.repositories import entities
from co.deability.identifier.errors.NoSuchEntityError import NoSuchEntityError

"""
A repository that uses an entity's data to create an identifier for the entity.

#todo add versioning for entity files.
"""


def find_entity_path(identifier: str) -> Optional[Path]:
    entity_file: Path = next(entities.get_data_file_paths(identifier=identifier), None)
    return entity_file


def create_entity(entity: Dict[str, Any]) -> str:
    identifier: str = entities.calculate_id_from_data(data=entity)
    identifier_path: Path = repositories.create_identifier_path(identifier=identifier)
    new_data_path: Path = entities.calculate_new_data_path(
        identifier_path=identifier_path
    )
    assert identifier_path.exists()
    new_data_path.write_text(data=json.dumps(entity), encoding=config.TEXT_ENCODING)
    return identifier


def read_entity(identifier: str) -> Optional[Dict[str, Any]]:
    entity_file: Path = find_entity_path(identifier=identifier)
    result = (
        json.loads(entity_file.read_text(encoding=config.TEXT_ENCODING))
        if entity_file
        else None
    )
    if result == {}:
        result = None
    return result


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
    new_identifier: str = entities.calculate_id_from_data(data=entity)
    old_data_path: Path = find_entity_path(identifier=identifier)
    if not old_data_path:
        raise NoSuchEntityError(
            message=f"The supplied identifier is recognized, but no corresponding entity was found, so the update could not be applied."
        )
    if new_identifier == identifier:
        new_data_path: Path = entities.calculate_new_data_path(
            identifier_path=old_data_path.parent
        )
        new_data_path.write_text(data=json.dumps(entity), encoding=config.TEXT_ENCODING)
        if old_data_path.is_symlink():
            _link_last(first_path=old_data_path.readlink(), target_path=new_data_path)
        entities.update_link(old_path=old_data_path, new_path=new_data_path)
    else:
        new_identifier_path: Path = repositories.calculate_path(
            identifier=new_identifier
        )
        if not new_identifier_path.exists():
            repositories.create_identifier_path(identifier=new_identifier)
            new_data_path: Path = entities.calculate_new_data_path(
                identifier_path=new_identifier_path
            )
            new_data_path.write_text(
                data=json.dumps(entity), encoding=config.TEXT_ENCODING
            )
            entities.update_link(old_path=old_data_path, new_path=new_data_path)
        else:
            update_entity(identifier=new_identifier, entity=entity)
    return new_identifier


def delete_entity(identifier: str) -> None:
    entity_path: Path = find_entity_path(identifier=identifier)
    if not entity_path:
        raise NoSuchEntityError(
            message=f"There is no entity matching the supplied identifier, so no entity was deleted."
        )
    elif entity_path.is_symlink():
        _link_last(
            first_path=entity_path.readlink(),
            target_path=entities.DELETED_ENTITY_PATH,
        )
    entities.update_link(old_path=entity_path, new_path=entities.DELETED_ENTITY_PATH)
    assert entity_path.is_symlink()
    assert entity_path.exists()


def does_entity_exist(id_or_entity: [str, Dict[str, Any]]):
    identifier = (
        id_or_entity
        if isinstance(id_or_entity, str)
        else entities.calculate_id_from_data(data=id_or_entity)
    )
    return read_entity(identifier=identifier) is not None


def _link_last(first_path: Path, target_path: Path):
    if first_path:
        if first_path.is_symlink():
            next_path = first_path.readlink()
            while next_path and next_path.is_symlink():
                current_path = next_path
                next_path = next_path.readlink()
                if not next_path:
                    entities.update_link(old_path=current_path, new_path=target_path)
            if next_path:
                entities.update_link(old_path=next_path, new_path=target_path)
        else:
            entities.update_link(old_path=first_path, new_path=target_path)
