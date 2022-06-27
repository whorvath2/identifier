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
from typing import Dict, Any, List

from co.deability.identifier.api import repositories
from co.deability.identifier.api.repositories import entities
from co.deability.identifier.api.repositories.entities import (
    entity_repository,
    index_repository,
)


def add_entity(entity: Dict[str, Any]) -> Dict[str, str]:
    identifier: str = entity_repository.create_entity(entity=entity)
    return {"created": identifier}


def remove_entity(identifier: str) -> None:
    repositories.check_identifier(identifier=identifier)
    entity_repository.delete_entity(identifier=identifier)


def update_entity(identifier: str, entity: Dict[str, Any]) -> Dict[str, str]:
    repositories.check_identifier(identifier=identifier)
    new_identifier: str = entity_repository.update_entity(
        identifier=identifier, entity=entity
    )
    return {"updated": new_identifier}


def get_entity(identifier: str) -> Dict[str, Any]:
    repositories.check_identifier(identifier=identifier)
    return entity_repository.read_entity(identifier=identifier)


def add_search_terms(identifier: str, search_terms: Dict[str, Any]) -> None:
    entities.check_if_empty(data=search_terms)
    repositories.check_identifier(identifier=identifier)
    index_repository.create_index(identifier=identifier, index=search_terms)


def remove_search_terms(search_terms: Dict[str, Any]) -> None:
    entities.check_if_empty(data=search_terms)
    index_identifier: str = entities.calculate_id_from_data(data=search_terms)
    index_repository.delete_index(index_identifier=index_identifier)


def search_for_entities(search_terms: Dict[str, Any]) -> List[Dict[str, Any]]:
    entities.check_if_empty(data=search_terms)
    return index_repository.find_entities(index=search_terms)


def search_for_entity_ids(search_terms: Dict[str, Any]) -> List[str]:
    entities.check_if_empty(data=search_terms)
    return index_repository.find_entity_ids(index=search_terms)


def add_schema(schema: Dict[str, Any], name: str) -> None:
    entities.check_schema(schema=schema)
    entity_repository.add_schema(schema=schema, name=name)


def remove_schema(name: str) -> None:
    entity_repository.remove_schema(name=name)


def update_schema(schema: Dict[str, Any], name: str) -> None:
    entities.check_schema(schema=schema)
    entity_repository.update_schema(schema=schema, name=name)


def get_schema(name: str = None) -> Dict[str, Any]:
    return entity_repository.get_schema(name=name)
