from http import HTTPStatus

from co.deability.identifier.errors.IdentifierError import IdentifierError


class BadRequestError(IdentifierError):
    """
    Thrown when a request is not processable due to missing or malformed data, malformed query
    parameters, etc.
    """

    def __init__(self, message: str):
        super().__init__(message=message, error_code=HTTPStatus.BAD_REQUEST)
