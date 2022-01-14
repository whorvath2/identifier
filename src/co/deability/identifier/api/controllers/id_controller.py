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
from typing import Final

from flask import Blueprint, jsonify, make_response

from co.deability.identifier.api.services.id_service import IdCreator

id_blueprint: Blueprint = Blueprint("identifier", __name__, url_prefix="/identifier")
id_creator: Final[IdCreator] = IdCreator()


@id_blueprint.get("/")
def health_check():
    format: str = "%a, %d %b %Y %H:%M:%S +0000"
    content: dict = {
        "timestamp": time.strftime(format, time.gmtime()),
        "status": "OK",
    }
    return make_response(jsonify(content), 200)


@id_blueprint.get("/new")
def get_new_id():
    return make_response(jsonify(id_creator.get_new_id()), 200)
