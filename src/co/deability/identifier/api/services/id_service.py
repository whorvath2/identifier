from co.deability.identifier.api import config
from co.deability.identifier.api.repositories.id_repository import (
    IdRepository,
    IdRepositoryType,
)


class IdCreator:
    def __init__(
        self,
        id_repository: IdRepository = IdRepository(
            repository_type=IdRepositoryType.WRITER
        ),
    ):
        self.id_repository = id_repository

    def get_new_id(self) -> dict:
        new_id: str = self.id_repository.create_id(retries=config.MAX_RETRIES)
        return {"created": new_id}
