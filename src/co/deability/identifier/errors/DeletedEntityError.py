from http import HTTPStatus

from co.deability.identifier.errors.IdentifierError import IdentifierError


class DeletedEntityError(IdentifierError):
    """
    Raised when an operation is attempted on an entity that has previously been deleted.
    """

    def __init__(self, message: str):
        super().__init__(message=message, error_code=HTTPStatus.BAD_REQUEST)
