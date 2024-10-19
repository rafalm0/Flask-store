from db import db


class ItemTags(db.Model):
    __tablename__ = "items_tags"

    item_id = db.Column(db.Integer, db.ForeignKey("item.id"), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey("tag.id"), nullable=False)