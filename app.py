import secrets
import uuid
from flask import Flask, request
from flask_smorest import abort, Api
from flask_jwt_extended import JWTManager
import os

from db import db
import models  # importing models imports the __init__ therefore imports all of them as a package
# models need to be already imported before sqlchemy


from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint



def create_app(db_url=None):
    app = Flask(__name__)

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config['SQLALCHEMY_TACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = '261696634396203470738536034261566624783'

    db.init_app(app)

    with app.app_context(): # creating all tables initially
        db.create_all()

    api = Api(app)

    jwt = JWTManager(app)

    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)


    return app
