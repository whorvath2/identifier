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
from pathlib import Path

import pytest
import re
import os

from co.deability.identifier import config
from co.deability.identifier.errors.BadRepositoryError import BadRepositoryError
from co.deability.identifier.errors.IllegalArgumentError import IllegalArgumentError
from co.deability.identifier.errors.IllegalIdentifierError import IllegalIdentifierError
from co.deability.identifier.api.repositories.id_repository import (
    IdRepository,
    _is_valid,
    _generate_id,
)
from co.deability.identifier.api.repositories.id_repository_type import IdRepositoryType
from co.deability.identifier.errors.TooManyRetriesError import TooManyRetriesError
from conftest import TEMP_PATH


def test_id_repository_construction():
    with pytest.raises(IllegalArgumentError):
        IdRepository(repository_type="aString", base_path="./")
    with pytest.raises(BadRepositoryError):
        IdRepository(
            repository_type=IdRepositoryType.WRITER,
            base_path="./foobar",
        )

    IdRepository._writer = None
    repository: IdRepository = IdRepository(
        repository_type=IdRepositoryType.WRITER,
        base_path=TEMP_PATH,
    )
    assert repository._writer == repository
    assert len(repository._readers) <= config.MAX_READER_COUNT

    IdRepository._readers = []
    repository = IdRepository(
        repository_type=IdRepositoryType.READER,
        base_path=TEMP_PATH,
    )
    assert IdRepository._readers[0] == repository
    os.environ["ID_MAX_READER_COUNT"] = "1"
    another_repository: IdRepository = IdRepository(
        repository_type=IdRepositoryType.READER,
        base_path=TEMP_PATH,
    )
    assert IdRepository._readers[0] == repository


def test_validity_tester():
    an_id = "aShortId"  # too short
    assert not _is_valid(an_id)
    an_id = "x" * 32  # illegal characters
    assert not _is_valid(an_id)
    an_id = "a" * 32
    assert _is_valid(an_id)


def test_id_generator():
    an_id = _generate_id()
    assert re.compile("[a-f0-9]{32}").match(an_id)


def test_repository_create_id_fails_with_illegal_retries_values(
    mock_id_repository_writer,
):
    with pytest.raises(IllegalArgumentError):
        mock_id_repository_writer.create_id(retries=None)
    with pytest.raises(IllegalArgumentError):
        mock_id_repository_writer.create_id(retries="foobar")
    with pytest.raises(IllegalArgumentError):
        mock_id_repository_writer.create_id(retries=-1)


def test_repository_calculates_paths_correctly(mock_id_repository_writer):
    an_id: str = "abc"
    assert Path(TEMP_PATH, "a/b/c") == mock_id_repository_writer._path_calculator(
        identifier=an_id
    )


def test_repository_creates_ids(mock_id_repository_writer):
    an_id = mock_id_repository_writer.create_id()
    assert (
        an_id
        and len(an_id) == 32
        and Path(mock_id_repository_writer._path_calculator(an_id)).exists()
    )


def test_create_id_with_bad_retries_raises_error(mock_id_repository_writer):
    with pytest.raises(IllegalArgumentError):
        mock_id_repository_writer.create_id(retries=None)
    with pytest.raises(IllegalArgumentError):
        mock_id_repository_writer.create_id(retries=-1)


def test_create_id_with_failed_retries_raises_correct_error(mock_id_repository_writer):
    holder = mock_id_repository_writer._serialize
    mock_id_repository_writer._serialize = lambda identifier: False
    with pytest.raises(TooManyRetriesError):
        mock_id_repository_writer.create_id(retries=0)
    mock_id_repository_writer._serialize = holder


def test_repository_checks_identifier_existence_correctly(mock_id_repository_writer):
    an_id = mock_id_repository_writer.create_id()
    assert mock_id_repository_writer.exists(identifier=an_id)

    with pytest.raises(IllegalIdentifierError):
        mock_id_repository_writer.exists(identifier="foobar")
