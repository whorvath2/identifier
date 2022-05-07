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
from typing import Any, Final

from co.deability.identifier import config
from co.deability.identifier.api.repositories.id_repository import (
    IdRepository,
    IdRepositoryType,
)
from co.deability.identifier.errors.BadRequestError import BadRequestError
from co.deability.identifier.errors.IllegalArgumentError import IllegalArgumentError

WRITER_REPOSITORY: Final[IdRepository] = IdRepository(
    repository_type=IdRepositoryType.WRITER
)


def create_new_id(id_repository: IdRepository = WRITER_REPOSITORY) -> dict:
    return {"created": id_repository.create_id(retries=config.MAX_WRITE_RETRIES)}


def add_data(
    data: dict[str, Any],
    identifier: str,
    id_repository: IdRepository = WRITER_REPOSITORY,
) -> dict[str, Any]:
    if not data:
        raise BadRequestError(message="The data is missing or empty.")
    id_repository.add_data(data=data, identifier=identifier)
    return get_current_data(identifier=identifier)


def get_current_data(identifier: str) -> dict[str, Any]:
    data: Any = _get_reader().get_current_data(identifier=identifier)
    if not data:
        data = {}
    return {f"{identifier}": data}


def get_all_data(identifier: str) -> dict[str, Any]:
    return {f"{identifier}": _get_reader().get_all_data(identifier=identifier)}


def exists(identifier: str) -> dict:
    return {f"{identifier} exists": _get_reader().exists(identifier=identifier)}


def _get_reader() -> IdRepository:
    return IdRepository(repository_type=IdRepositoryType.READER)


class IdCreator:
    """
    Service class that supports use of a specific IdRepository instance, which must be an
    IdRepositoryType.WRITER type.
    """

    def __init__(
        self,
        id_repository: IdRepository = WRITER_REPOSITORY,
    ):
        if not id_repository.get_type() == IdRepositoryType.WRITER:
            raise IllegalArgumentError(
                message="The supplied repository is not a supported type."
            )
        self.id_repository = id_repository

    def get_new_id(self) -> dict:
        return create_new_id(id_repository=self.id_repository)

    def add_data(self, data: dict[str, Any], identifier: str) -> dict[str, Any]:
        return add_data(
            data=data, identifier=identifier, id_repository=self.id_repository
        )
