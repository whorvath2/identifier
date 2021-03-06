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
from logging import Logger
from typing import Final

LOG: Final[Logger] = logging.getLogger()


class IdentifierError(Exception):
    """
    Base class for Identifier-specific exceptions.
    """

    def __init__(self, message: str, error_code: int):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        LOG.error(
            msg=f"{message} (Error code: {error_code})",
            exc_info=self,
            stack_info=__debug__,
        )
