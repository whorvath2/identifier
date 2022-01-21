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
import pytest

from co.deability.identifier.api.services.id_service import IdCreator
from co.deability.identifier.errors.IllegalArgumentError import IllegalArgumentError


def test_get_new_id(mock_id_repository_writer):
    creator = IdCreator(id_repository=mock_id_repository_writer)
    new_id = creator.get_new_id()
    assert new_id is not None


def test_construction(mock_id_repository_reader):
    with pytest.raises(IllegalArgumentError):
        IdCreator(id_repository=mock_id_repository_reader)
