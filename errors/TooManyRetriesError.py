from http import HTTPStatus

from errors.IdentifierError import IdentifierError


class TooManyRetriesError(IdentifierError):
    """
    Thrown when one or more attempts have been made to create a serialized identifier and all
    have failed.
    """

    def __init__(self, retries: int):
        super().__init__(
            message=f"An identifier could not be created after {retries} attempts.",
            error_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
