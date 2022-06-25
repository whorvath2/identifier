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
