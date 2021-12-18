import os
import pathlib
import shutil
import sys

# add the parent directory to the path
import pytest

from api.repositories.IdRepository import IdRepository
from api.repositories.IdRepositoryType import IdRepositoryType

myPath = os.path.dirname(os.path.abspath(__file__))  # noqa: E402
sys.path.insert(0, myPath + "/../")  # noqa: E402


@pytest.fixture()
def mock_id_repository_root(request):
    print("Setup")
    temp_path = "./temp/"
    os.makedirs(name=temp_path, mode=500, exist_ok=True)
    yield pathlib.Path(temp_path)

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
