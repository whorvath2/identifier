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
