import secrets
import uuid
from flask import Flask, request, jsonify
from flask_smorest import abort, Api
from flask_jwt_extended import JWTManager
import os
from flask_migrate import Migrate
from dotenv import dotenv_values

from db import db
import models  # importing models imports the __init__ therefore imports all of them as a package
# models need to be already imported before sqlchemy

from blocklist import BLOCKLIST
from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint


def create_app(db_url=None):
    app = Flask(__name__)
    env_config = dotenv_values()

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url or env_config['DATABASE_URL'] or "sqlite:///data.db"
    app.config['SQLALCHEMY_TACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = '261696634396203470738536034261566624783'

    print(f"Deployment database on {app.config['SQLALCHEMY_DATABASE_URI']}")
    # ------------------------- populating db with tables ------------------------
    db.init_app(app)
    with app.app_context():  # creating all tables initially
        db.create_all()


    # --------------------------------- flask migrate ---------------------

    migrate = Migrate(app,db)

    # ---------------------------- app initialization -------------------
    api = Api(app)

    # ---------------------------- jwt config and methods-----------------------------------
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_clocklist(jwt_header, jwt_payload):
        return jwt_payload['jti'] in BLOCKLIST

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        if identity == 1:
            return {"is_admin": True}
        else:
            return {"is_admin": True} # admin not required for deletion

    @jwt.revoked_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (jsonify({"message": "Token revoked, user loged out", "error": "token_revoked"}), 401)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (jsonify({"message": "Token expired", "error": "token_expired"}), 401)

    @jwt.needs_fresh_token_loader
    def token_not_fresh_token_callback(jwt_header, jwt_payload):
        return (jsonify({"message": "Token is not fresh", "error": "fresh_token_required"}), 401)

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (jsonify({"message": "Signature failed", "error": "invalid_token"}), 401)

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (jsonify({"message": "No signature in request", "error": "authorization_required"}), 401)

    # -------------------------- blueprint registers --------------------------

    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)

    return app
