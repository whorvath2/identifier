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
from co.deability.identifier.api.repositories.id_repository import IdRepository
from co.deability.identifier.api.repositories.id_repository_type import IdRepositoryType
from conftest import ACCEPT_JSON_HEADERS, TEMP_PATH

ROOT_DIR: Final[str] = "/identifier"


def test_health_check():

    with app.test_client() as client:
        endpoint = f"{ROOT_DIR}"
        response = client.get(endpoint, headers=ACCEPT_JSON_HEADERS)
        assert "OK" in str(response.json)


def test_create_id():
    with app.test_client() as client:
        endpoint = f"{ROOT_DIR}/new"
        response = client.get(endpoint, headers=ACCEPT_JSON_HEADERS)
        assert "created" in str(response.json)
