import logging
import uuid
import getpass
import time
from os import path, PathLike
from pathlib import Path
from typing import Final

from co.deability.identifier.api import config
from co.deability.identifier.errors.BadProcessError import BadProcessError
from co.deability.identifier.errors.BadRepositoryError import BadRepositoryError
from co.deability.identifier.errors.IllegalArgumentError import IllegalArgumentError
from co.deability.identifier.errors.IllegalIdentifierError import IllegalIdentifierError
from co.deability.identifier.errors.UnsupportedOperationError import (
    UnsupportedOperationError,
)
from co.deability.identifier.api.repositories.IdRepositoryType import IdRepositoryType
from co.deability.identifier.errors.TooManyRetriesError import TooManyRetriesError

VALID_CHARS: Final[str] = "0123456789abcdef"


def _is_valid(identifier: str) -> bool:
    """
    Returns True if identifier is 32 characters long and composed entirely of numbers (0-9) and
    lower-case letters in the range a-f; False otherwise.

    This function was built under the assumption that the identifier is based on the string
    representation of a uuid.uuid4() call after the dashes (-) have been removed from the string;
    hence the length and content constraints. Also see VALID_CHARS, above, and _generate_id(),
    below.

    :param identifier: The identifier to be validated.
    :return: True if identifier is 32 characters long and composed entirely of numbers (0-9) and
    lower-case letters in the range a-f; False otherwise.

    """
    if len(identifier) != 32:
        return False
    for c in identifier:
        if c not in VALID_CHARS:
            return False
    return True


def _generate_id() -> str:
    """
    Returns a string representation of a UUID for use as an identifier for entities. The
    identifier will be 32 characters long, each of which will be either a number (0-9) or a
    lower case letter in the range a-f. See VALID_CHARS, above.

    :return: A string that can be used to uniquely identify an entity.
    """
    return str(uuid.uuid4()).replace("-", "", 4)


class IdRepository:
    """
    A repository for creating new identifiers that are guaranteed to have never been
    returned previously by a WRITER instance. IdRepositories use the filesystem as their backing
    data store, which obviates numerous problems related to performance and transaction ACID-ity.
    """

    _readers: list["IdRepository"] = None
    _writer: "IdRepository" = None
    _reader_index: int = 0
    _serialization_failures: int = 0  # A crude indicator of what's going on that can be
    # included in log messages. May be removed or replaced in a future release.

    def __init__(
        self,
        repository_type: IdRepositoryType,
        base_path: (str, PathLike) = config.BASE_PATH,
    ) -> None:
        if not isinstance(repository_type, IdRepositoryType):
            raise IllegalArgumentError("type must be an IdRepositoryType.")
        if not base_path or not isinstance(base_path, (str, PathLike)):
            raise IllegalArgumentError(
                "base_path must be a non-empty string or PathLike object."
            )
        self.type = repository_type
        self.base_path: Path = Path(base_path)

        if not self.base_path.exists() or not self.base_path.is_dir():
            raise BadRepositoryError()
        if not self.base_path.owner() == getpass.getuser():
            raise BadProcessError()

    def _path_calculator(self, identifier: str) -> Path:
        """
        Returns a file path for a directory derived from this instance's base_path and the
        supplied identifier that takes the form of a single-character directory structure.
        E.g., for an IdRepository instance with a base_path of "/foo/bar" and an identifier
        value of "c963ef49afa5483bb1326e9525727140", the returned value would be
        "/foo/bar/c/9/6/3/e/f/4/9/a/f/a/5/4/8/3/b/b/1/3/2/6/e/9/5/2/5/7/2/7/1/4/0"

        :param identifier: The identifier to be transmogrified into a file path.
        :return: A file path for a directory that's suitable for serialization to disk.
        """
        return Path(self.base_path, "/".join(identifier))

    def create_id(self, retries: int = 0) -> str:
        """
        Returns an identifier that has been serialized out to disk and is guaranteed to
        have never been returned from this application before, so long as the disk to which
        it's connected is the same across runs of the application.

        Exceptions will be raised under the following conditions:
          * retries is None, not an integer, or is an integer less than zero;
          * an identifier cannot be serialized within the supplied number (retries) of attempts;
          * this IdRepository instance's type is not IdRepositoryType.WRITER

        :param retries: The number of times to attempt to create an identifier and
        serialize it to disk before erroring out.
        :return: The serialized identifier.
        """
        if not isinstance(retries, int) or retries < 0:
            raise IllegalArgumentError(
                message="retries must be an integer greater than or equal to zero."
            )
        if self.type != IdRepositoryType.WRITER:
            raise UnsupportedOperationError()
        new_id: str = _generate_id()
        while retries >= 0:
            if self._serialize(identifier=new_id):
                return new_id
            new_id = _generate_id()
            retries -= 1
            time.sleep(0.01)  # Give the CPU a break
        raise TooManyRetriesError(retries=retries)

    def exists(self, identifier: str) -> bool:
        """
        Returns True if the supplied identifier already exists in this IdRepository instance;
        False otherwise. An identifier exists in an IdRepository if it has already been
        serialized to disk in the form of a directory.

        If the supplied identifier is not valid, an exception will be raised.

        :param identifier: The identifier to be checked to determine whether it is already known to
        this IdRepository.
        :return: True if the supplied identifier is valid and exists in this IdRepository; False
        otherwise.
        """
        if not _is_valid(identifier=identifier):
            raise IllegalIdentifierError()
        file_path: Path = self._path_calculator(identifier=identifier)
        return path.exists(file_path)

    def _serialize(self, identifier: str) -> bool:
        """
        Returns True if the supplied identifier is not already in the system and is successfully
        serialized to disk; False otherwise.

        IMPORTANT: exceptions are caught and logged, and are not 'bubbled up', as this function's
        success or failure is what we care about internally.

        :param identifier: The identifier to be stored on disk.
        :return: True if the supplied identifier is not already in the system and is successfully
        serialized to disk; False otherwise.
        """

        assert _is_valid(identifier=identifier)

        file_path: Path = self._path_calculator(identifier=identifier)
        if file_path.exists():
            return False
        try:
            file_path.mkdir(parents=True, exist_ok=False)
            return True
        except FileExistsError:
            logging.warning(msg=f"Identifier {identifier} already exists.")
        except Exception as ex:
            self._serialization_failures += 1
            message = (
                f"Unable to serialize identifier {identifier}. Total serialization "
                f"failures: {self._serialization_failures}"
            )
            logging.error(
                msg=message,
                exc_info=ex,
                stack_info=True,
            )
        return False

    def __new__(cls, *args, **kwargs) -> "IdRepository":
        """
        Returns a singleton if the caller requests a WRITER; otherwise returns a new or existing
        READER instance. (Existing reader instances are selected in round-robin fashion.)
        """
        if cls._writer is None and kwargs["repository_type"] is IdRepositoryType.WRITER:
            cls._writer = super(IdRepository, cls).__new__(cls)
            return cls._writer

        else:
            if cls._readers is None:
                cls._readers = []
            elif len(cls._readers) == config.MAX_READER_COUNT:
                cls._reader_index = (
                    0
                    if cls._reader_index == config.MAX_READER_COUNT - 1
                    else (cls._reader_index + 1)
                )
                reader = cls._readers[cls._reader_index]
                return reader

            new_reader = super(IdRepository, cls).__new__(cls)
            cls._readers.append(new_reader)
            return new_reader
