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
import time
from http import HTTPStatus
from typing import Final

from flask import Blueprint, jsonify, make_response, request

from co.deability.identifier.api.services import id_service
from co.deability.identifier.api.services.id_service import IdCreator
from co.deability.identifier import config

id_blueprint: Blueprint = Blueprint("identifier", __name__, url_prefix="/identifier")
ID_CREATOR: Final[IdCreator] = IdCreator()


@id_blueprint.get("/")
def health_check():
    dt_format: str = "%a, %d %b %Y %H:%M:%S +0000"
    content: dict = {
        "build id": f"{config.BUILD_ID}",
        "timestamp": time.strftime(dt_format, time.gmtime()),
        "status": "OK",
    }
    # Use assertion to allow config exposure in pre-production environments
    assert (
        content.update(
            {
                "config": {
                    "ROOT_LOG_LEVEL": f"{config.ROOT_LOG_LEVEL}",
                    "APP_LOG_LEVEL": f"{config.APP_LOG_LEVEL}",
                    "IDENTIFIER_DATA_PATH": f"{config.IDENTIFIER_DATA_PATH}",
                    "MAX_READER_COUNT": f"{config.MAX_READER_COUNT}",
                    "MAX_WRITE_RETRIES": f"{config.MAX_WRITE_RETRIES}",
                }
            }
        )
        is None
    )
    return make_response(jsonify(content), HTTPStatus.OK)


@id_blueprint.get("/new")
def get_new_id():
    return make_response(jsonify(ID_CREATOR.get_new_id()), HTTPStatus.CREATED)


@id_blueprint.get("/exists/<identifier>")
def check_id_exists(identifier: str):
    return make_response(
        jsonify(id_service.exists(identifier=identifier)), HTTPStatus.OK
    )


@id_blueprint.post("/data/add/<identifier>")
def add_data(identifier: str):
    return make_response(
        jsonify(ID_CREATOR.add_data(data=request.json, identifier=identifier)),
        HTTPStatus.OK,
    )


@id_blueprint.get("/data/current/<identifier>")
def get_current_data(identifier: str):
    return make_response(
        jsonify(id_service.get_current_data(identifier=identifier)), HTTPStatus.OK
    )


@id_blueprint.get("/data/all/<identifier>")
def get_all_data(identifier: str):
    return make_response(
        jsonify(id_service.get_all_data(identifier=identifier)), HTTPStatus.OK
    )
