from flask_smorest import Blueprint, abort
from schemas import UserSchema
from flask.views import MethodView
from models import UserModel
from passlib.hash import pbkdf2_sha256

from db import db
from sqlalchemy.exc import SQLAlchemyError

blp = Blueprint("users", __name__, description="Operations on users")


@blp.route("/register")
class UserRegister(MethodView):

    @blp.arguments(UserSchema)
    # @blp.response()
    def post(self, user_data):
        if UserModel.query.filter(UserModel == user_data['username']).first():
            abort(404, message='user with that username exists already')

        username = user_data['username']
        password = pbkdf2_sha256.hash(user_data['password'])
        user = UserModel(username=username, password=password)

        db.session.add(user)
        db.session.commit()

        return {"message": "User created"}, 201


@blp.route("/user/<int:user_id>")
class Store(MethodView):

    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user

    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted"}

