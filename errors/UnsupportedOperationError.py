from http import HTTPStatus

from errors.IdentifierError import IdentifierError


class UnsupportedOperationError(IdentifierError):
    """
    Thrown when a function is called that is not supported by the class in which it resides.
    """

    def __init__(self):
        super().__init__(
            message="This operation is not supported",
            error_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
