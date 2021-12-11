from flask import Flask
from flask_cors import CORS


def init_app() -> Flask:
    app: Flask = Flask(__name__)
    app.url_map.strict_slashes = False
    app.config.from_pyfile("config.py")

    CORS(app)
    _register_error_handlers(app)
    _register_blueprints(app)
    _initialize_graph_connection()
    _initialize_signing_keys()
    return app
