from db import db


class StoreModel(db.Model):  # this import of db model and create a column with rows defined by this object
    __tablename__ = "stores"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(80), unique=True, nullable=False)
    tags = db.relationship("TagModel", back_populates="store", lazy="dynamic")
    items = db.relationship("ItemModel", back_populates="store", lazy="dynamic", cascade="all, delete")
    # https://docs.sqlalchemy.org/en/20/orm/cascades.html

    '''lazy avoids contant refreshing data instead of only when needed, and cascade deletes the child when parant
    is deleted, therefore here items are deleted if their store is deleted'''
