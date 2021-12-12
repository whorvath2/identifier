import uuid
from os import path
from pathlib import Path

from errors.BadRepositoryError import BadRepositoryError
from errors.IllegalArgumentError import IllegalArgumentError
from errors.IllegalIdentifierError import IllegalIdentifierError
from errors.UnsupportedOperationError import UnsupportedOperationError
from repositories.IdRepositoryType import IdRepositoryType

VALID_CHARS: str = "0123456789abcdef"


class IdRepository:
    """
    A repository for creating new identifiers and serializing them out to disk, and for
    validating identifier values.
    """

    _readers: list["IdRepository"] = None
    _writer: "IdRepository" = None
    _max_reader_count: int = 1
    _reader_index: int = 0

    def __init__(
        self, type: IdRepositoryType, base_path: str, max_reader_count: int
    ) -> None:
        if max_reader_count <= 0:
            raise IllegalArgumentError("max_reader count must be greater than zero.")
        self.max_reader_count = max_reader_count
        if not isinstance(type, IdRepositoryType):
            raise IllegalArgumentError("type must be an IdRepositoryType.")
        self.type = type
        self.base_path: Path = Path(base_path)
        if not self.base_path.exists():
            raise BadRepositoryError()

    def create_id(self) -> str:
        if self.type != IdRepositoryType.WRITER:
            raise UnsupportedOperationError()
        new_id: str = str(uuid.uuid4()).replace("-", "", 4)
        stored_id: str = self._serialize(identifier=new_id)
        return stored_id

    def exists(self, identifier: str) -> bool:
        if not self.is_valid(identifier=identifier):
            raise IllegalIdentifierError(
                message="The supplied identifier contains illegal characters."
            )
        file_path: Path = Path(self.base_path, "/".join(identifier))
        return path.exists(file_path)

    def is_valid(self, identifier: str) -> bool:
        for c in identifier:
            if c not in VALID_CHARS:
                return False
        return True

    def _serialize(self, identifier: str) -> str:
        file_path: Path = Path(self.base_path, "/", "/".join(identifier))
        if not file_path.exists():
            # exists_ok is True in case of parallel operations
            file_path.mkdir(mode=500, parents=True, exist_ok=True)
        return identifier

    def __new__(cls, *args, **kwargs):
        """
        Returns a singleton if the caller requests a WRITER; otherwise returns a new or existing
        READER instance.
        """
        if cls._writer is None and kwargs["type"] is IdRepositoryType.WRITER:
            cls._writer = super(IdRepository, cls).__new__(cls)
            return cls._writer

        else:
            if cls._readers is None:
                cls._readers = []
            elif len(cls._readers) > cls._max_reader_count:
                reader = cls._readers[cls._reader_index]
                cls._reader_index = (
                    0
                    if cls._reader_index == cls._max_reader_count - 1
                    else (cls._reader_index + 1)
                )
                return reader

            new_reader = super(IdRepository, cls).__new__(cls)
            cls._readers.append(new_reader)
            return new_reader
