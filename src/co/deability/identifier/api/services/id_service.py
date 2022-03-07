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
from typing import Any

from co.deability.identifier import config
from co.deability.identifier.api.repositories.id_repository import (
    IdRepository,
    IdRepositoryType,
)
from co.deability.identifier.errors.IllegalArgumentError import IllegalArgumentError


class IdCreator:
    def __init__(
        self,
        id_repository: IdRepository = IdRepository(
            repository_type=IdRepositoryType.WRITER
        ),
    ):
        if not id_repository.get_type() == IdRepositoryType.WRITER:
            raise IllegalArgumentError(
                message="The supplied repository is not a supported type."
            )
        self.id_repository = id_repository

    def get_new_id(self) -> dict:
        return {
            "created": self.id_repository.create_id(retries=config.MAX_WRITE_RETRIES)
        }

    def add_data(self, data: dict[str, Any], identifier: str) -> dict[str, Any]:
        return self.id_repository.add_data(
            data=data, identifier=identifier
        ).get_current_data(identifier=identifier)


def get_current_data(identifier: str) -> dict[str, Any]:
    return {f"{identifier}": _get_reader().get_current_data(identifier=identifier)}


def exists(identifier: str) -> dict:
    return {f"{identifier} exists": _get_reader().exists(identifier=identifier)}


def _get_reader() -> IdRepository:
    return IdRepository(repository_type=IdRepositoryType.READER)
