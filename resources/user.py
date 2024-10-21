from flask_smorest import Blueprint, abort
from schemas import UserSchema
from flask.views import MethodView
from models import UserModel
from passlib.hash import pbkdf2_sha256
from env_config import MAILGUN_DOMAIN, MAILGUN_API_KEY
import requests

from blocklist import BLOCKLIST
from db import db
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, create_refresh_token, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError

blp = Blueprint("users", __name__, description="Operations on users")


def send_simple_message(to,subject,body):
    return requests.post(
        f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
        auth=("api", f"{MAILGUN_API_KEY}"),
        data={"from": f"Mail User <mailgun@{MAILGUN_DOMAIN}>",
              "to": [to],
              "subject": subject,
              "text": body})


@blp.route("/register")
class UserRegister(MethodView):

    @blp.arguments(UserSchema)
    # @blp.response()
    def post(self, user_data):
        if UserModel.query.filter(UserModel.username == user_data['username']).first():
            abort(409, message='user with that username exists already')

        username = user_data['username']
        password = pbkdf2_sha256.hash(user_data['password'])
        user = UserModel(username=username, password=password)

        db.session.add(user)
        db.session.commit()

        return {"message": "User created"}, 201


@blp.route("/login")
class UserLogin(MethodView):

    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(UserModel.username == user_data['username']).first()

        if not user:
            abort(404, message="user not found")

        if pbkdf2_sha256.verify(user_data['password'], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)
            '''access_token structure when decoded:
            {
                "fresh":false, 
                "iat":123,
                "jti":cf2cd-eab-df4-dfdf,
                "type":"access",
                "sub":1,
                "nbf":16599744953,
                "exp":16599748883
            }'''
            return {"access_token": access_token, "refresh_token": refresh_token}
        else:
            abort(401, message="Wrong password")


@blp.route("/refresh")
class TokenRefresh(MethodView):

    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(current_user, fresh=False)
        return {"access_token": new_token}


@blp.route("/logout")
class UserLogout(MethodView):

    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out"}


@blp.route("/user/<int:user_id>")
class User(MethodView):

    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user

    @jwt_required(fresh=True)
    def delete(self, user_id):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin privileges required for deletion.")
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted"}
