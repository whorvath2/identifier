from http import HTTPStatus

from co.deability.identifier.errors.IdentifierError import IdentifierError


class IllegalArgumentError(IdentifierError):
    """
    Thrown when an illegal argument is passed to a function.
    """

    def __init__(self, message: str):
        super().__init__(message=message, error_code=HTTPStatus.INTERNAL_SERVER_ERROR)
