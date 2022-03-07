from http import HTTPStatus

from co.deability.identifier.errors.IdentifierError import IdentifierError


class NoSuchEntityError(IdentifierError):
    """
    Thrown when an identifier is supplied by a client that doesn't exist in the context of
    the current Identifier instance.
    """

    def __init__(self, message: str):
        super().__init__(message=message, error_code=HTTPStatus.BAD_REQUEST)
