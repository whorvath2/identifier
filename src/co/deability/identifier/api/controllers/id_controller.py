import time
from typing import Final

from flask import Blueprint, jsonify, make_response, request, Response

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
