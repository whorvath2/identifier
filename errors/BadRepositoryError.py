from http import HTTPStatus

from errors.IdentifierError import IdentifierError


class BadRepositoryError(IdentifierError):
    """
    Thrown when an IdentifierRepository can't be constructed because the minimum requirements
    (such as the base path existing in the file system) haven't been met.
    """

    def __init__(self):
        super().__init__(
            message="The repository is not available because minimum requirements are unmet.",
            error_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
