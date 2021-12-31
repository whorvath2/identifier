import time
from datetime import datetime

from flask import Blueprint, jsonify, make_response, request, Response

id_blueprint: Blueprint = Blueprint("identifier", __name__, url_prefix="/identifier")


@id_blueprint.get("/")
def health_check():
    format: str = "%a, %d %b %Y %H:%M:%S +0000"
    content: dict = {
        "timestamp": time.strftime(format, time.gmtime()),
        "status": "OK",
    }
    return make_response(jsonify(content), 200)
