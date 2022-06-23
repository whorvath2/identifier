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
from typing import Final

from co.deability.identifier.api.app import app
from conftest import ACCEPT_JSON_HEADERS

ROOT_DIR: Final[str] = "/identifier"


def _create_id():
    with app.test_client() as client:
        endpoint = f"{ROOT_DIR}/new"
        id_content = client.get(endpoint, headers=ACCEPT_JSON_HEADERS).json
        random_id = id_content.get("created")
        return random_id


def test_health_check():
    with app.test_client() as client:
        endpoint = f"{ROOT_DIR}"
        response = client.get(endpoint, headers=ACCEPT_JSON_HEADERS)
        assert "OK" in str(response.json)


def test_create_id():
    random_id = _create_id()
    assert len(random_id) == 32


def test_check_id_exists():
    with app.test_client() as client:
        random_id = _create_id()
        endpoint = f"{ROOT_DIR}/exists/{random_id}"
        response = client.get(endpoint, headers=ACCEPT_JSON_HEADERS)
        assert response.json.get(f"{random_id} exists") is True


def test_add_data():
    with app.test_client() as client:
        random_id = _create_id()
        endpoint = f"{ROOT_DIR}/data/add/{random_id}"
        body = {"foo": "bar"}
        response = client.post(endpoint, headers=ACCEPT_JSON_HEADERS, json=body)
        assert str(response.json).find(str(body)) >= 0


def test_get_current_data():
    with app.test_client() as client:
        endpoint = f"{ROOT_DIR}/new"
        random_id = _create_id()
        endpoint = f"{ROOT_DIR}/data/add/{random_id}"
        body = {"foo": "bar"}
        client.post(endpoint, headers=ACCEPT_JSON_HEADERS, json=body)
        endpoint = f"{ROOT_DIR}/data/current/{random_id}"
        response = client.get(endpoint, headers=ACCEPT_JSON_HEADERS)
        assert str(response.json).find(str(body)) >= 0


def test_get_all_data():
    with app.test_client() as client:
        endpoint = f"{ROOT_DIR}/new"
        random_id = _create_id()
        endpoint = f"{ROOT_DIR}/data/add/{random_id}"
        body_one = {"foo": "bar"}
        client.post(endpoint, headers=ACCEPT_JSON_HEADERS, json=body_one)
        body_two = {"fizz": "buzz"}
        client.post(endpoint, headers=ACCEPT_JSON_HEADERS, json=body_two)
        endpoint = f"{ROOT_DIR}/data/all/{random_id}"
        response = client.get(endpoint, headers=ACCEPT_JSON_HEADERS)
        output = str(response.json)
        assert output.find(str(body_one)) >= 0
        assert output.find(str(body_two)) >= 0
