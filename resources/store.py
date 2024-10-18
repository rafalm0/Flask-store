import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from models import StoreModel
from db import db
from schemas import StoreSchema

blp = Blueprint("stores", __name__, description="Operations on stores")


@blp.route("/store/<string:store_id>")
class Store(MethodView):

    @blp.response(200, StoreSchema)
    def get(self, store_id):
        item = StoreModel.query.get_or_404(store_id)
        raise NotImplementedError("Later")

    def delete(self, store_id):
        item = StoreModel.query.get_or_404(store_id)
        raise NotImplementedError("Later")


@blp.route("/store")
class StoreList(MethodView):
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()

    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self,
             store_data):  # the method only has this other param because marshmallow is feeding it with the blp.schema
        item = StoreModel(**store_data)  # just passing the arguments to create the item

        try:
            db.session.add(item)
            db.session.commit()
        except IntegrityError:
            abort(400,message="Store name already exists")
        except SQLAlchemyError:
            abort(500, message="Error creating item IN post /ITEM")

        return item
