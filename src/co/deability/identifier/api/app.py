from flask import Flask
from flask_cors import CORS
from co.deability.identifier.api import init_app

app: Flask = init_app()
cors = CORS(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
