from http import HTTPStatus

from errors.IdentifierError import IdentifierError


class IllegalIdentifierError(IdentifierError):
    """
    Thrown when...
    """

    def __init__(self, message: str):
        super().__init__(
            message="The supplied identifier includes illegal characters.",
            error_code=HTTPStatus.BAD_REQUEST,
        )
