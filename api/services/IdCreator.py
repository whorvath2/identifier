from os import PathLike

import config
from api.repositories.IdRepository import IdRepository
from api.repositories.IdRepositoryType import IdRepositoryType


class IdCreator:
    def __init__(self, id_repository: IdRepository):
        self.id_repository = id_repository

    def get_new_id(self) -> str:
        return self.id_repository.create_id(retries=config.MAX_RETRIES)
