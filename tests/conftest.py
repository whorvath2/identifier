import os
import pathlib
import shutil
import sys

# add the parent directory to the path
import pytest

myPath = os.path.dirname(os.path.abspath(__file__))  # noqa: E402
sys.path.insert(0, myPath + "/../")  # noqa: E402

import api


@pytest.fixture()
def mock_id_repository_root(request):
    print("Setup")
    temp_path = "./temp/"
    os.makedirs(name=temp_path, mode=500, exist_ok=True)
    yield pathlib.Path(temp_path)

    def path():
        return temp_path

    def teardown():
        print("Teardown")
        shutil.rmtree(path=temp_path, ignore_errors=False)

    request.addfinalizer(teardown)

    return "resource"
