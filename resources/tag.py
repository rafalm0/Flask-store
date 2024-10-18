from flask_smorest import Blueprint, abort
from schemas import TagSchema
from flask.views import MethodView
from models import TagModel, StoreModel

from db import db
from sqlalchemy.exc import SQLAlchemyError

blp = Blueprint("Tags", __name__, description="Operations on tags")


@blp.route("/store/<string:store_id>/tag")
class TagInStore(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store.tags.all()

    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, tag_data, store_id):
        tag = TagModel(**tag_data,store_id=store_id)
        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return tag

@blp.route("/tag/<string:tag_id>")
class Store(MethodView):

    @blp.response(200, TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag

    def delete(self, tag_id):
        tag = StoreModel.query.get_or_404(tag_id)
        db.session.delete(tag)
        db.session.commit()
        return {"message": "tag deleted"}