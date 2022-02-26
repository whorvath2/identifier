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
import shutil
from pathlib import Path
import sys
from typing import Final

import pytest

# add the parent directory to the path per noqa: E402
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + "/../")
os.environ["APP_LOG_LEVEL"] = "DEBUG"
os.environ["ROOT_LOG_LEVEL"] = "INFO"
test_path: Path = Path(Path.home().absolute(), ".identifier/test")
os.environ["IDENTIFIER_DATA_PATH"] = str(test_path)

from co.deability.identifier import api
from co.deability.identifier.api.repositories.id_repository import IdRepository
from co.deability.identifier.api.repositories.id_repository_type import IdRepositoryType

# turn on debug-level logging for tests
logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)

ACCEPT_JSON_HEADERS: Final[dict[str]] = {"Accept": "application/json"}


def pytest_runtest_setup(item):
    print(f"Constructing temporary path {test_path}...")
    test_path.mkdir(parents=True, exist_ok=True)


def pytest_runtest_teardown(item):
    print(f"...Destroying temporary path {test_path}")
    shutil.rmtree(test_path, ignore_errors=True)


@pytest.fixture
def http_client():
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
def mock_id_repository_writer():
    return IdRepository(repository_type=IdRepositoryType.WRITER, base_path=test_path)


@pytest.fixture
def mock_id_repository_reader():
    return IdRepository(repository_type=IdRepositoryType.READER, base_path=test_path)
