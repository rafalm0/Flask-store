from marshmallow import Schema, fields

'''Schemas for the objects, in python we'll have the plain values with only their fixed values, and super objects
for versions that include more and could be related to other objects or key'''


class PlainItemSchema(Schema):
    id = fields.Str(dump_only=True)  # means that we generate this, so we never receive it
    name = fields.Str(required=True)
    price = fields.Float(required=True)


class ItemSchema(PlainItemSchema):
    store_id = fields.Str(required=True, load_only=True)
    store = fields.Nested(PlainItemSchema(), dump_only=True)


class PlainTagSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str()


class ItemUpdateSchema(Schema):
    name = fields.Str()
    price = fields.Float()
    store_id = fields.Int()


class PlainStoreSchema(Schema):
    id = fields.Int(dump_only=True)  # Alternative is Load only where we never need to send to client this
    name = fields.Str(required=True)


class TagSchema(PlainTagSchema):
    store_id = fields.Str(load_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)


class StoreSchema(PlainStoreSchema):
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)
