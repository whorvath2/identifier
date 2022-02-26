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
