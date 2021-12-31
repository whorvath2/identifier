from typing import Final

from co.deability.identifier.api.app import app
from conftest import ACCEPT_JSON_HEADERS

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
