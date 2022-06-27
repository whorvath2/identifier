"""
Copyright © 2021 William L Horvath II

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import inspect
from http import HTTPStatus
from typing import Optional, List

from flask import Response, make_response, jsonify
from werkzeug.exceptions import InternalServerError

from co.deability.identifier import config
from co.deability.identifier.errors.IdentifierError import IdentifierError
from co.deability.identifier.errors.ImpossibleError import ImpossibleError
from co.deability.identifier.config import LOG


def handle_assertion_errors(assertion_error: AssertionError) -> Response:
    if config.debug:
        stack: List[inspect.FrameInfo] = inspect.stack()
        internal_message: str = (
            f"Assertion error raised in {stack[1].function} after call from "
            f"{stack[2].function}"
        )
        LOG.error(
            internal_message,
            stack_info=True,
            exc_info=assertion_error,
        )
    message: str = "No additional information was reported."
    if assertion_error.args and assertion_error.args[0]:
        message = assertion_error.args[0]
    new_error: ImpossibleError = ImpossibleError(
        message=f"{message}",
    )
    return handle_identifier_errors(error=new_error)


def handle_identifier_errors(error: IdentifierError) -> Response:
    if isinstance(error, ImpossibleError):
        if config.debug:
            LOG.error(
                f"Coding error caught in {error}",
                exc_info=error,
                stack_info=True,
            )
        else:
            stack: List[inspect.FrameInfo] = inspect.stack()
            LOG.error(
                f"Internal error raised in {stack[1].function} after call "
                f"from {stack[2].function}",
                stack_info=False,
            )
        result = {
            "Error": "An internal error has occurred. Please contact support for assistance."
        }
        return make_response(jsonify(result), HTTPStatus.INTERNAL_SERVER_ERROR)
    else:
        LOG.error(
            f"IdentifierError: {error.message}",
            exc_info=error,
            stack_info=True,
        )
    return make_response(jsonify({"Error": error.message}), error.error_code)


def handle_internal_errors(error: InternalServerError) -> Response:
    original_error: Optional[BaseException] = error.original_exception
    if original_error:
        oe_type: str = str(type(original_error))
        LOG.error(
            msg=f"Internal Server Error based on {oe_type}",
            exc_info=original_error,
            stack_info=True,
        )
        if __debug__ is True:
            return make_response(
                jsonify({"Error": str(original_error)}),
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )
    return make_response(
        jsonify(
            {
                "Error": error.name,
                "Description": error.get_description(),
            }
        ),
        500,
    )


def handle_url_not_found(error) -> Response:
    message = "This URL is not recognized by the Identifier API."
    LOG.warning(msg=message, exc_info=error)
    return make_response(jsonify({"Not Found": message}), HTTPStatus.NOT_FOUND)
