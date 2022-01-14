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
import logging
import os
from pathlib import Path
import shutil
import sys
from typing import Final

import pytest

# add the parent directory to the path
myPath = os.path.dirname(os.path.abspath(__file__))  # noqa: E402
sys.path.insert(0, myPath + "/../")  # noqa: E402

from co.deability.identifier import api, config
from co.deability.identifier.api.repositories.id_repository import IdRepository
from co.deability.identifier.api.repositories.id_repository_type import IdRepositoryType

# turn on debug-level logging for tests
logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)

ACCEPT_JSON_HEADERS: Final[dict[str]] = {"Accept": "application/json"}


@pytest.fixture
def http_client(mock_id_repository_root):
    """
    Mock HTTP client for use in testing routes.
    """
    app = api.init_app()
    app.debug = True
    with app.app_context():
        app.config["TESTING"] = True
        client = app.test_client()
        yield client


@pytest.fixture
def mock_id_repository_root(request):
    print("Setup")
    temp_path = Path(config.BASE_PATH, "temp")
    temp_path.mkdir(parents=True, exist_ok=True)
    yield Path(temp_path)

    def teardown():
        print("Teardown")
        shutil.rmtree(path=temp_path, ignore_errors=False)

    request.addfinalizer(teardown)

    return "resource"


@pytest.fixture
def mock_id_repository_writer(mock_id_repository_root):
    return IdRepository(
        repository_type=IdRepositoryType.WRITER, base_path=mock_id_repository_root
    )