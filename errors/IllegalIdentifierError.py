from http import HTTPStatus

from errors.IdentifierError import IdentifierError


class IllegalIdentifierError(IdentifierError):
    """
    Thrown when...
    """

    def __init__(self):
        super().__init__(
            message="The supplied identifier is invalid.",
            error_code=HTTPStatus.BAD_REQUEST,
        )
