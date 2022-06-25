from typing import Dict, Any, List

from co.deability.identifier.api.repositories import entities
from co.deability.identifier.api.repositories.entities import (
    entity_repository,
    index_repository,
)


def add_entity(entity: Dict[str, Any]) -> Dict[str, str]:
    identifier: str = entity_repository.create_entity(entity=entity)
    return {"created identifier": identifier}


def remove_entity(identifier: str) -> None:
    entity_repository.delete_entity(identifier=identifier)


def update_entity(identifier: str, entity: Dict[str, Any]) -> Dict[str, str]:
    new_identifier: str = entity_repository.update_entity(
        identifier=identifier, entity=entity
    )
    return {"updated identifier": new_identifier}


def get_entity(identifier: str) -> Dict[str, Any]:
    return entity_repository.read_entity(identifier=identifier)


def add_search_terms(identifier: str, search_terms: Dict[str, Any]) -> None:
    index_repository.create_index(identifier=identifier, index=search_terms)


def remove_search_terms(search_terms: Dict[str, Any]) -> None:
    index_repository.delete_index(index_or_identifier=search_terms)


def remove_search_index(index_identifier: str) -> None:
    index_repository.delete_index(index_or_identifier=index_identifier)


def search_for_entities(index_terms: Dict[str, Any]) -> List[Dict[str, Any]]:
    return index_repository.find_entities(index=index_terms)


def search_for_entity_ids(index_terms: Dict[str, Any]) -> List[str]:
    return index_repository.find_entity_ids(index=index_terms)
