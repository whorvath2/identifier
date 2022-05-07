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
import sys
from http import HTTPStatus

from co.deability.identifier.errors.IdentifierError import IdentifierError


class EnvironmentError(IdentifierError):
    """
    Thrown when the Identifier API is being run in a malformed environment.
    """

    def __init__(self, explanation: str):
        super().__init__(
            message=f"Identifier cannot start: {explanation}",
            error_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
        sys.exit(explanation)
