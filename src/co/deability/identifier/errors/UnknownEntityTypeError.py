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
from http import HTTPStatus

from co.deability.identifier.errors.IdentifierError import IdentifierError


class UnknownEntityTypeError(IdentifierError):
    """
    Raised when a post request is made to add an entity in which the client-specified entity type is not
    known and cannot be validated.
    """

    def __init__(self):
        super().__init__(
            message="The entity type is not recognized.",
            error_code=HTTPStatus.NOT_FOUND,
        )
