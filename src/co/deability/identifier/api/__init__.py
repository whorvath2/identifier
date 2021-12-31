from flask import Flask
from flask_cors import CORS

from co.deability.identifier.api import config
from co.deability.identifier.api.controllers.id_controller import id_blueprint
from co.deability.identifier.errors.BadRepositoryError import BadRepositoryError


def init_app() -> Flask:
    app: Flask = Flask(__name__)
    app.url_map.strict_slashes = False
    app.config.from_pyfile("config.py")

    CORS(app)
    _register_error_handlers(app)
    _register_blueprints(app)
    _initialize_data_store()
    return app


def _register_error_handlers(app) -> None:
    pass


def _register_blueprints(app) -> None:
    app.register_blueprint(id_blueprint)


def _initialize_data_store() -> None:
    try:
        config.BASE_PATH.mkdir(parents=True, exist_ok=True)
    except FileExistsError:
        raise BadRepositoryError()
