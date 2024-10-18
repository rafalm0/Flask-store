from db import db


class TagModel(db.Model):  # this import of db model and create a column with rows defined by this object
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    store_id = db.Column(db.String(), db.ForeignKey("stores.id"), nullable=False)
    store = db.relationship("StoreModel", back_populates="tags")

