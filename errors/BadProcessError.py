from http import HTTPStatus

from errors.IdentifierError import IdentifierError


class BadProcessError(IdentifierError):
    """
    Thrown when an IdRepository detects that the user owning the process under which it is running
    is not the same as the owner of the file structure it is using for storage.
    """

    def __init__(self):
        super().__init__(
            message="The IdRepository's process is running under an invalid account.",
            error_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
