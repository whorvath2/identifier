from co.deability.identifier.api.app import app
from conftest import ACCEPT_JSON_HEADERS


def test_health_check():
    with app.test_client() as client:
        endpoint = "/identifier"
        response = client.get(endpoint, headers=ACCEPT_JSON_HEADERS)
        assert "OK" in str(response.json)
