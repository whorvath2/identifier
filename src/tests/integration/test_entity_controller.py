import json
from http import HTTPStatus
from typing import Dict, Any, Optional

from co.deability.identifier.api.app import app
from conftest import ACCEPT_JSON_HEADERS, JSON_CONTENT_HEADERS

ROOT_DIR: str = "/identifier/entity"
ENTITY: Dict[str, str] = {"foo": "bar"}
UPDATED_ENTITY: Dict[str, str] = {"fizz": "buzz"}
SECOND_ENTITY: Dict[str, str] = {"hello": "world"}
SEARCH_TERMS: Dict[str, str] = {"findby": "foo"}
SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {"fizzbuzz": {"type": "string"}},
}
UPDATED_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {"foobar": {"type": "string"}},
}


def _add_entity(entity=None, second_run: bool = False):
    if entity is None:
        entity = ENTITY
    with app.test_client() as client:
        endpoint = f"{ROOT_DIR}/add/foobar"
        response = client.post(
            endpoint,
            headers=ACCEPT_JSON_HEADERS | JSON_CONTENT_HEADERS,
            data=json.dumps(entity),
        )
        if second_run:
            return response
        else:
            entity_id = response.json.get("created")
            assert response.status_code == HTTPStatus.CREATED
            return entity_id


def _update_entity(identifier: str):
    with app.test_client() as client:
        endpoint = f"{ROOT_DIR}/update/{identifier}"
        response = client.put(
            endpoint,
            headers=ACCEPT_JSON_HEADERS | JSON_CONTENT_HEADERS,
            data=json.dumps(UPDATED_ENTITY),
        )
        assert response.status_code == HTTPStatus.OK
        updated_id = response.json.get("updated")
        assert updated_id
        return updated_id


def _get_entity(identifier: str):
    with app.test_client() as client:
        endpoint = f"{ROOT_DIR}/read/{identifier}"
        response = client.get(endpoint, headers=ACCEPT_JSON_HEADERS)
        assert response.status_code == HTTPStatus.OK
        return response.json


def _add_search_terms(identifier: str):
    with app.test_client() as client:
        endpoint = f"{ROOT_DIR}/index/add/{identifier}"
        response = client.post(
            endpoint,
            headers=ACCEPT_JSON_HEADERS | JSON_CONTENT_HEADERS,
            data=json.dumps(SEARCH_TERMS),
        )
        assert response.status_code == HTTPStatus.NO_CONTENT
        return response


def _run_search():
    with app.test_client() as client:
        endpoint = f"{ROOT_DIR}/search"
        response = client.get(
            endpoint,
            headers=ACCEPT_JSON_HEADERS | JSON_CONTENT_HEADERS,
            data=json.dumps(SEARCH_TERMS),
        )
        assert response.status_code == HTTPStatus.OK
        if response.is_json:
            return response.json
        return []


def test_add_entity():
    entity_id = _add_entity()
    assert entity_id
    assert len(entity_id) == 32


def test_get_entity():
    entity_id = _add_entity()
    with app.test_client() as client:
        endpoint = f"{ROOT_DIR}/read/{entity_id}"
        response = client.get(endpoint, headers=ACCEPT_JSON_HEADERS)
        assert response.json == ENTITY
        assert response.status_code == HTTPStatus.OK


def test_remove_entity(setup_entity_repository):
    entity_id = _add_entity()
    with app.test_client() as client:
        endpoint = f"{ROOT_DIR}/archive/{entity_id}"
        response = client.delete(endpoint)
        assert response.status_code == HTTPStatus.NO_CONTENT


def test_update_entity():
    entity_id = _add_entity()
    updated_id = _update_entity(identifier=entity_id)
    assert _get_entity(identifier=entity_id) == UPDATED_ENTITY
    assert _get_entity(identifier=updated_id) == UPDATED_ENTITY


def test_add_search_terms():
    entity_id = _add_entity()
    _add_search_terms(identifier=entity_id)


def test_remove_search_terms(setup_entity_repository):
    entity_id = _add_entity()
    _add_search_terms(identifier=entity_id)
    with app.test_client() as client:
        endpoint = f"{ROOT_DIR}/index/delete"
        response = client.delete(
            endpoint,
            headers=ACCEPT_JSON_HEADERS | JSON_CONTENT_HEADERS,
            data=json.dumps(SEARCH_TERMS),
        )
        assert response.status_code == HTTPStatus.NO_CONTENT
    assert _run_search() == []


def test_find_entities_by_search_terms():
    entity_id = _add_entity()
    _add_search_terms(identifier=entity_id)
    assert _run_search()[0] == ENTITY


def test_find_entity_identifiers_by_search_terms():
    entity_id = _add_entity()
    _add_search_terms(identifier=entity_id)
    with app.test_client() as client:
        endpoint = f"{ROOT_DIR}/search/ids"
        response = client.get(
            endpoint,
            headers=ACCEPT_JSON_HEADERS | JSON_CONTENT_HEADERS,
            data=json.dumps(SEARCH_TERMS),
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json[0] == entity_id


def test_find_by_search_terms_after_entity_updated():
    entity_id = _add_entity()
    _add_search_terms(identifier=entity_id)
    _update_entity(identifier=entity_id)
    assert _run_search()[0] == UPDATED_ENTITY


def test_find_by_search_terms_against_updated_entity():
    entity_id = _add_entity()
    updated_id = _update_entity(identifier=entity_id)
    _add_search_terms(identifier=updated_id)
    assert _run_search()[0] == UPDATED_ENTITY


def test_cannot_add_entity_twice():
    entity_id = _add_entity()
    response = _add_entity(second_run=True)
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_add_one_search_terms_to_two_entities():
    entity_id = _add_entity()
    _add_search_terms(identifier=entity_id)
    another_id = _add_entity(entity=SECOND_ENTITY)
    _add_search_terms(identifier=another_id)
    search_result = _run_search()
    assert search_result.index(ENTITY) >= 0
    assert search_result.index(SECOND_ENTITY) >= 0


def _add_schema(name: str):
    with app.test_client() as client:
        endpoint = f"{ROOT_DIR}/schema/add/{name}"
        response = client.post(
            endpoint,
            headers=ACCEPT_JSON_HEADERS | JSON_CONTENT_HEADERS,
            data=json.dumps(SCHEMA),
        )
        return response


def _get_schema(name: str):
    with app.test_client() as client:
        endpoint = f"{ROOT_DIR}/schema/read/{name}"
        response = client.get(
            endpoint,
            headers=ACCEPT_JSON_HEADERS,
        )
        return response


def _remove_schema(name: str):
    with app.test_client() as client:
        endpoint = f"{ROOT_DIR}/schema/delete/{name}"
        response = client.delete(
            endpoint,
            headers=ACCEPT_JSON_HEADERS,
        )
        return response


def test_add_and_remove_schema(setup_entity_repository):
    name = "a_schema"
    response = _add_schema(name=name)
    assert response.status_code == HTTPStatus.NO_CONTENT
    response = _get_schema(name=name)
    assert response.json == {name: SCHEMA}
    response = _remove_schema(name=name)
    assert response.status_code == HTTPStatus.NO_CONTENT
    response = _get_schema(name=name)
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_schema(setup_entity_repository):
    name = "a_schema"
    _add_schema(name=name)
    with app.test_client() as client:
        endpoint = f"{ROOT_DIR}/schema/update/{name}"
        response = client.put(
            endpoint,
            headers=ACCEPT_JSON_HEADERS | JSON_CONTENT_HEADERS,
            data=json.dumps(UPDATED_SCHEMA),
        )
        assert response.status_code == HTTPStatus.NO_CONTENT
    response = _get_schema(name=name)
    assert response.json == {name: UPDATED_SCHEMA}
