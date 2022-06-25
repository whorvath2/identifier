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
import logging
from functools import cache
from pathlib import Path
from typing import Final
from os import path

from co.deability.identifier import config
from co.deability.identifier.errors.BadRepositoryError import BadRepositoryError
from co.deability.identifier.errors.IdentifierAlreadyExistsError import (
    IdentifierAlreadyExistsError,
)
from co.deability.identifier.errors.IllegalArgumentError import IllegalArgumentError
from co.deability.identifier.errors.IllegalIdentifierError import IllegalIdentifierError
from co.deability.identifier.errors.NoSuchEntityError import NoSuchEntityError

"""
A collection of functions and constants used by different Identifier repository implementations that 
define the core operational philosophy of how Identifier's data IO works.
"""

BASE_PATH: Final[Path] = Path(config.DATA_PATH)
if not BASE_PATH.exists() or not BASE_PATH.is_dir():
    raise BadRepositoryError()

VALID_CHARS: Final[str] = "0123456789abcdef"
TIME_LENGTH: Final[int] = 12
DATA_FILE: Final[str] = ".json"


def calculate_identifier(identifier_path: Path) -> str:
    identifier_path = identifier_path.absolute()
    if not identifier_path.is_dir:
        identifier_path = identifier_path.parent
    if not identifier_path.is_relative_to(BASE_PATH):
        raise IllegalArgumentError(
            message="The path cannot be parsed because it is not relative to BASE_PATH"
        )
    child_path: Path = identifier_path.relative_to(BASE_PATH)
    identifier = str(child_path).replace("/", "")
    assert len(identifier) == config.IDENTIFIER_LENGTH
    return identifier


def calculate_path(identifier: str) -> Path:
    """
    Returns a file path for a directory derived from this instance's base_path and the
    supplied identifier that takes the form of a single-character directory structure.
    E.g., for a UuidRepository instance with a base_path of "/foo/bar" and an identifier
    value of "c963ef49afa5483bb1326e9525727140", the returned value would be
    "/foo/bar/c/9/6/3/e/f/4/9/a/f/a/5/4/8/3/b/b/1/3/2/6/e/9/5/2/5/7/2/7/1/4/0"

    Raises an IllegalIdentifierError if the supplied identifier is not valid
    (see is_valid_identifier, below)

    :param identifier: The identifier to be transmogrified into a file path.
    :return: A file path for a directory that's suitable for serialization to disk.
    """
    if not is_valid_identifier(identifier=identifier):
        raise IllegalIdentifierError()
    return Path(BASE_PATH, "/".join(identifier))


def create_identifier_path(identifier: str) -> Path:
    """
    Returns a path representing a directory in this Identifier instance's file system that has been
    calculated from the supplied identifier and created on disk.

    :param identifier: the identifier to be created on disk.
    :return: a path representing a directory in this Identifier instance's file system that
    represents the supplied identifier and which has been created on disk.
    """

    file_path: Path = calculate_path(identifier=identifier)
    try:
        file_path.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        raise IdentifierAlreadyExistsError(identifier=identifier)
    except Exception as ex:
        message = f"Unable to serialize identifier."
        logging.error(
            msg=message,
            exc_info=ex,
            stack_info=True,
        )
        raise ex
    return file_path


def identifier_exists(identifier: str) -> bool:
    """
    Returns True if the supplied identifier already exists in this instance's repository;
    False otherwise. An identifier exists in an repository if it has already been
    serialized to disk in the form of a directory.

    If the supplied identifier is not valid, an exception will be raised.

    :param identifier: The identifier to be checked to determine whether it is already known to
    this UuidRepository.
    :return: True if the supplied identifier is valid and exists in this identifier repository; False
    otherwise.
    """
    file_path: Path = calculate_path(identifier=identifier)
    return path.exists(file_path)


def is_valid_identifier(identifier: str) -> bool:
    """
    Returns True if the supplied identifier is not None, composed entirely of valid characters,
    and is the correct length; False otherwise.

    :param identifier:
    :return: True if the supplied identifier is valid for this Identifier instance; False otherwise.
    """
    if len(identifier) != config.IDENTIFIER_LENGTH:
        return False
    for c in identifier:
        if c not in VALID_CHARS:
            return False
    return True


def check_identifier(identifier: str) -> None:
    """
    Raises an error if the supplied identifier is not valid or does not exist; otherwise has no effect.

    :param identifier: The identifier to be evaluated as to whether appears in the data
    store backing this identifier instance.
    """

    # No need for validity check here; it's in identifier_exists
    if not identifier_exists(identifier):
        raise NoSuchEntityError(message=f"The supplied identifier is not recognized.")
