from pathlib import Path

import pytest
import re

from errors.BadRepositoryError import BadRepositoryError
from errors.IllegalArgumentError import IllegalArgumentError
from errors.IllegalIdentifierError import IllegalIdentifierError
from api.repositories.IdRepository import IdRepository, _is_valid, _generate_id
from api.repositories.IdRepositoryType import IdRepositoryType


def test_id_repository_construction():
    with pytest.raises(IllegalArgumentError):
        IdRepository(
            repository_type=IdRepositoryType.READER, base_path="./", max_reader_count=-1
        )
    with pytest.raises(IllegalArgumentError):
        IdRepository(repository_type="aString", base_path="./", max_reader_count=1)
    with pytest.raises(BadRepositoryError):
        IdRepository(
            repository_type=IdRepositoryType.READER,
            base_path="./foobar",
            max_reader_count=1,
        )


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
    mock_id_repository_root,
):
    repository: IdRepository = IdRepository(
        repository_type=IdRepositoryType.WRITER,
        base_path=mock_id_repository_root,
        max_reader_count=1,
    )
    with pytest.raises(IllegalArgumentError):
        repository.create_id(retries=None)
    with pytest.raises(IllegalArgumentError):
        repository.create_id(retries="foobar")
    with pytest.raises(IllegalArgumentError):
        repository.create_id(retries=-1)


def test_repository_calculates_paths_correctly(mock_id_repository_root):
    repository: IdRepository = IdRepository(
        repository_type=IdRepositoryType.WRITER,
        base_path=mock_id_repository_root,
        max_reader_count=1,
    )
    an_id: str = "abc"
    assert Path(mock_id_repository_root, "a/b/c") == repository._path_calculator(
        identifier=an_id
    )


def test_repository_creates_ids(mock_id_repository_root):
    repository: IdRepository = IdRepository(
        repository_type=IdRepositoryType.WRITER,
        base_path=mock_id_repository_root,
        max_reader_count=1,
    )
    an_id = repository.create_id()
    print(an_id)
    assert (
        an_id and len(an_id) == 32 and Path(repository._path_calculator(an_id)).exists()
    )


def test_repository_checks_identifier_existence_correctly(mock_id_repository_root):
    repository: IdRepository = IdRepository(
        repository_type=IdRepositoryType.WRITER,
        base_path=mock_id_repository_root,
        max_reader_count=1,
    )
    an_id = repository.create_id()
    assert repository.exists(identifier=an_id)

    with pytest.raises(IllegalIdentifierError):
        repository.exists(identifier="foobar")
