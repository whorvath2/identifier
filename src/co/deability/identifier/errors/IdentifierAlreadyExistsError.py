from http import HTTPStatus

from co.deability.identifier.errors.IdentifierError import IdentifierError


class IdentifierAlreadyExistsError(IdentifierError):
    """
    Thrown when an attempt is made to serialize an identifier that already exists in an identifier
    repository. Since it already exists, the value is safe to include in the message.
    """

    def __init__(self, identifier: str):
        super().__init__(
            message=f"The supplied identifier {identifier} already exists in the repository.",
            error_code=HTTPStatus.BAD_REQUEST,
        )
