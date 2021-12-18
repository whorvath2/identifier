from flask import Flask
from flask_cors import CORS

import config
from errors.BadRepositoryError import BadRepositoryError


def init_app() -> Flask:
    app: Flask = Flask(__name__)
    app.url_map.strict_slashes = False
    app.config.from_pyfile("config.py")

    CORS(app)
    _register_error_handlers(app)
    _register_blueprints(app)
    return app


def initialize_data_store(app):
    try:
        config.BASE_PATH.mkdir(mode=700, parents=True, exist_ok=True)
    except FileExistsError:
        raise BadRepositoryError()


def _register_error_handlers(app):
    pass


def _register_blueprints(app):
    pass
