import pytest

from errors.BadRepositoryError import BadRepositoryError
from errors.IllegalArgumentError import IllegalArgumentError
from repositories.IdRepository import IdRepository
from repositories.IdRepositoryType import IdRepositoryType


def test_id_repository_construction():
    with pytest.raises(IllegalArgumentError):
        IdRepository(type=IdRepositoryType.READER, base_path="./", max_reader_count=-1)
    with pytest.raises(IllegalArgumentError):
        IdRepository(type="aString", base_path="./", max_reader_count=1)
    with pytest.raises(BadRepositoryError):
        IdRepository(
            type=IdRepositoryType.READER, base_path="./foobar", max_reader_count=1
        )
