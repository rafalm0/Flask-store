from db import db


class StoreModel(db.Model):  # this import of db model and create a column with rows defined by this object
    __tablename__ = "stores"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(80), unique=True, nullable=False)
    items = db.relationship("ItemModel", back_populates="store", lazy="dynamic") # lazy avoids constant pulling of items on the object
