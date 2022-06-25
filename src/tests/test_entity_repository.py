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
import json

import pytest

from co.deability.identifier.api import repositories
from co.deability.identifier.api.repositories import entities
from co.deability.identifier.api.repositories.entities import entity_repository
from co.deability.identifier.errors.NoSuchEntityError import NoSuchEntityError


def test_creates_entity():
    entity = {"foo": "bar"}
    new_identifier = entity_repository.create_entity(entity=entity)
    new_data_path = next(entities.get_data_file_paths(identifier=new_identifier))
    assert new_data_path.exists()
    assert json.loads(new_data_path.read_text()) == entity


def test_finds_entity_by_its_content():
    entity = {"foo": "bar"}
    new_identifier = entity_repository.create_entity(entity=entity)
    new_data_path = next(entities.get_data_file_paths(identifier=new_identifier), None)
    identifier = entities.find_identifier(data=entity)
    assert (
        repositories.calculate_identifier(identifier_path=new_data_path.parent)
        == identifier
    )


def test_reads_entity():
    entity = {"foo": "bar"}
    new_identifier = entity_repository.create_entity(entity=entity)
    new_data_path = next(entities.get_data_file_paths(identifier=new_identifier), None)
    identifier = repositories.calculate_identifier(identifier_path=new_data_path.parent)
    assert entity == entity_repository.read_entity(identifier=identifier)


def test_updates_entity():
    entity = {"foo": "bar"}
    first_identifier = entity_repository.create_entity(entity=entity)
    first_data_path = next(entities.get_data_file_paths(identifier=first_identifier))
    new_entity = {"fizz": "buzz"}
    new_identifier = entity_repository.update_entity(
        identifier=first_identifier, entity=new_entity
    )
    assert first_data_path.exists()
    assert first_data_path.is_symlink()
    assert json.loads(first_data_path.read_text()) == new_entity
    new_data_path = next(entities.get_data_file_paths(identifier=new_identifier))
    assert json.loads(new_data_path.read_text()) == new_entity


def test_updates_entity_to_old_value_correctly():
    first_entity = {"foo": "bar"}
    first_identifier = entity_repository.create_entity(entity=first_entity)
    second_entity = {"fizz": "buzz"}
    second_identifier = entity_repository.update_entity(
        identifier=first_identifier, entity=second_entity
    )
    final_identifier = entity_repository.update_entity(
        identifier=second_identifier, entity=first_entity
    )
    assert final_identifier == first_identifier
    assert entity_repository.read_entity(identifier=first_identifier) == first_entity
    assert entity_repository.read_entity(identifier=second_identifier) == first_entity
    assert entity_repository.read_entity(identifier=final_identifier) == first_entity


def test_updates_entity_to_old_value_correctly_with_many_changes():
    first_entity = {"foo": "bar"}
    first_identifier = entity_repository.create_entity(entity=first_entity)

    second_entity = {"fizz": "buzz"}
    second_identifier = entity_repository.update_entity(
        identifier=first_identifier, entity=second_entity
    )
    third_entity = {"silly": "walks"}
    third_identifier = entity_repository.update_entity(
        identifier=second_identifier, entity=third_entity
    )
    fourth_entity = {"spam": "green eggs and spam"}
    fourth_identifier = entity_repository.update_entity(
        identifier=third_identifier, entity=fourth_entity
    )
    final_identifier = entity_repository.update_entity(
        identifier=fourth_identifier, entity=second_entity
    )
    assert final_identifier == second_identifier
    assert entity_repository.read_entity(identifier=first_identifier) == second_entity
    assert entity_repository.read_entity(identifier=second_identifier) == second_entity
    assert entity_repository.read_entity(identifier=third_identifier) == second_entity
    assert entity_repository.read_entity(identifier=fourth_identifier) == second_entity
    assert entity_repository.read_entity(identifier=final_identifier) == second_entity


def test_does_not_update_missing_entity():
    entity = {"foo": "bar"}
    identifier = entities.calculate_id_from_data(data=entity)
    repositories.create_identifier_path(identifier=identifier)
    with pytest.raises(NoSuchEntityError):
        entity_repository.update_entity(identifier=identifier, entity=entity)


def test_deletes_entity(setup_entity_repository):
    entity = {"foo": "bar"}
    expected = {}
    identifier = entity_repository.create_entity(entity=entity)
    entity_repository.delete_entity(identifier=identifier)
    data_path = next(entities.get_data_file_paths(identifier=identifier))
    assert data_path.is_symlink()
    assert data_path.readlink()
    assert data_path.exists(), f"{data_path}"
    assert json.loads(data_path.read_text()) == expected
