from http import HTTPStatus

from co.deability.identifier.errors.IdentifierError import IdentifierError


class LockedIdentifierError(IdentifierError):
    """
    Thrown when a lock file exists longer than the maximum expiration time allowed.
    """

    def __init__(self, identifier: str):
        super().__init__(
            message=f"The identifier {identifier} has a stale lock that "
            f"requires manual intervention.",
            error_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
