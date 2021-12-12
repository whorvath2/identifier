import logging


class IdentifierError(BaseException):
    """
    Base class for Identifier-specific exceptions.
    """

    def __init__(self, message: str, error_code: int):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        logging.error(msg=message, exc_info=self, stack_info=__debug__)
        if __debug__:
            print("ERROR: " + message)
