from pathlib import Path

from co.deability.identifier.api import repositories
from conftest import test_path


def test_calculate_path():
    an_id: str = "12345678901234567890123456789012"
    expected: str = "1/2/3/4/5/6/7/8/9/0/1/2/3/4/5/6/7/8/9/0/1/2/3/4/5/6/7/8/9/0/1/2/"
    assert Path(test_path, expected) == repositories.calculate_path(identifier=an_id)
