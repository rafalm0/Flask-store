from flask_smorest import Blueprint, abort
from schemas import UserSchema, UserRegisterSchema
from flask.views import MethodView
from models import UserModel
from sqlalchemy import or_
from passlib.hash import pbkdf2_sha256
import os
if os.path.exists("env_config.py"):
    import env_config
import requests

from dotenv import load_dotenv


from blocklist import BLOCKLIST
from db import db
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, create_refresh_token, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError

blp = Blueprint("users", __name__, description="Operations on users")


def send_simple_message(to, subject, body):
    load_dotenv()
    if os.path.exists("env_config.py"):
        domain = env_config.MAILGUN_DOMAIN
        key = env_config.MAILGUN_API_KEY
    else:
        domain = os.getenv("MAILGUN_DOMAIN")
        key = os.getenv("MAILGUN_API_KEY")
    return requests.post(
        f"https://api.mailgun.net/v3/{domain}/messages",
        auth=("api", f"{key}"),
        data={"from": f"Mail User <mailgun@{domain}>",
              "to": [to],
              "subject": subject,
              "text": body})


@blp.route("/register")
class UserRegister(MethodView):

    @blp.arguments(UserRegisterSchema)
    # @blp.response()
    def post(self, user_data):
        if UserModel.query.filter(or_(UserModel.username == user_data['username'],
                                      UserModel.email == user_data['email'])).first():
            abort(409, message='User with that username or email exists already')

        user = UserModel(username=user_data['username'],
                         password=pbkdf2_sha256.hash(user_data['password']),
                         email=user_data['email'])

        db.session.add(user)
        db.session.commit()

        send_simple_message(to=user.email, subject="Signup", body=f"Successfully signed up. {user.username}")

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
