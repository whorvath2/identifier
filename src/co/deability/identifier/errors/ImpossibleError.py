from http import HTTPStatus

from co.deability.identifier.errors.IdentifierError import IdentifierError


class ImpossibleError(IdentifierError):
    """
    Thrown when an error occurs as a result of a bug in the software (which is, of course,
    impossible, since we write bug-free code.)
    """

    def __init__(self, message: str):
        super().__init__(message=message, error_code=HTTPStatus.INTERNAL_SERVER_ERROR)
