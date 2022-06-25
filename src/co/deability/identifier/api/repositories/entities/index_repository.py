import json
from pathlib import Path
from typing import Dict, Any, List, Generator, Optional, Iterator

from co.deability.identifier import config
from co.deability.identifier.api import repositories
from co.deability.identifier.api.repositories import entities
from co.deability.identifier.api.repositories.entities import entity_repository
from co.deability.identifier.errors.BadRequestError import BadRequestError
from co.deability.identifier.errors.NoSuchEntityError import NoSuchEntityError


def create_index(identifier: str, index: Dict[str, Any]) -> None:
    """
    Adds an index entry to the repository that points to the entity identified by the supplied identifier.

    :param identifier:
    :param index:
    :return:
    """
    if not index:
        raise BadRequestError("The index terms cannot be empty.")
    target_path: Path = entity_repository.find_entity_path(identifier=identifier)
    if not target_path:
        raise NoSuchEntityError(message="The target identifier is not recognized.")
    index_identifier: str = entities.calculate_id_from_data(data=index)
    index_identifier_path: Path = (
        repositories.create_identifier_path(identifier=index_identifier)
        if not entities.find_identifier(data=index)
        else repositories.calculate_path(identifer=index_identifier)
    )
    new_data_path: Path = entities.calculate_new_data_path(
        identifier_path=index_identifier_path
    )
    new_data_path.symlink_to(target=target_path)


def delete_index(index_or_identifier: [str, Dict[str, Any]]) -> None:
    index_identifier: str = (
        index_or_identifier
        if isinstance(index_or_identifier, str)
        else _get_index_identifier_path(index=index_or_identifier)
    )
    index_identifier_paths: Iterator[Path] = entities.get_data_file_paths(
        identifier=index_identifier
    )
    if not index_identifier_paths:
        raise NoSuchEntityError(
            message=f"There is no index entry matching the supplied data, so no index entry was deleted."
        )
    for index_identifier_path in index_identifier_paths:
        if index_identifier_path.exists():
            entities.update_link(
                old_path=index_identifier_path, new_path=entities.DELETED_ENTITY_PATH
            )


def find_entity_ids(index: Dict[str, Any]) -> List[str]:
    found_entity_ids: List[str] = []
    entity_paths = _get_entity_paths(index=index)
    for entity_path in entity_paths:
        found_entity_ids.append(
            repositories.calculate_identifier(identifier_path=entity_path)
        )
    return found_entity_ids


def find_entities(index: Dict[str, Any]) -> List[Dict[str, Any]]:
    found_entities: List[Dict[str, Any]] = []
    entity_paths = _get_entity_paths(index=index)
    for entity_path in entity_paths:
        entity = json.loads(entity_path.read_text(encoding=config.TEXT_ENCODING))
        if entity:
            found_entities.append(entity)
    return found_entities


def _get_index_identifier_path(index: Dict[str, Any]) -> Optional[Path]:
    if not index:
        raise BadRequestError("The index terms cannot be empty.")
    index_identifier: str = entities.calculate_id_from_data(data=index)
    index_identifier_path: Path = repositories.calculate_path(
        identifer=index_identifier
    )
    return index_identifier_path if index_identifier_path.exists() else None


def _get_entity_paths(index: Dict[str, Any]) -> List[Path]:
    index_identifier_path: Path = _get_index_identifier_path(index=index)
    entity_paths: List[Path] = []
    if index_identifier_path:
        index_identifier: str = repositories.calculate_identifier(
            identifier_path=index_identifier_path
        )
        entity_paths += entities.get_data_file_paths(identifier=index_identifier)
    return entity_paths
