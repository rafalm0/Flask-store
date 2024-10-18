import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from schemas import ItemSchema, ItemUpdateSchema
from models import ItemModel
from db import db

from sqlalchemy.exc import SQLAlchemyError

blp = Blueprint("item", __name__, description="Operations on items")



@blp.route("/item/<string:item_id>")
class Item(MethodView):

    @blp.response(200, ItemSchema)
    def get(self, item_id):
        item = ItemModel.query.get_or_404(item_id)  # get uses arg as primary key or returns 404
        return item

    def delete(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {"message": "Item deleted"}

    @blp.arguments(ItemUpdateSchema)  # this is passing data through marshmellow before the function
    @blp.response(200, ItemSchema)  # while this passes the output through marshmellow before sending to client
    def put(self, item_data, item_id):  # the new argument from marshmallow comes in front
        item = ItemModel.query.get(item_id)
        if item:  # if exist updates
            item.price = item_data['price']
            item.name = item_data['name']
        else:  # if it does not then try to create (if it has store it will succeed)
            item = ItemModel(id=item_id, **item_data)  # item_data is in json, while item_id is in url

        db.session.add(item)
        db.session.commit()

        return item


@blp.route("/item")
class ItemList(MethodView):
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()

    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema())
    def post(self,
             item_data):  # the method only has this other param because marshmallow is feeding it with the blp.schema
        item = ItemModel(**item_data)  # just passing the arguments to create the item

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="Error creating item IN post /ITEM")

        return item
