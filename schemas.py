from marshmallow import Schema, fields


class PlainItemSchema(Schema):
    id = fields.Str(dump_only=True)  # means that we generate this, so we never receive it
    name = fields.Str(required=True)
    price = fields.Float(required=True)


class ItemSchema(PlainItemSchema):
    store_id = fields.Str(required=True, load_only=True)
    store = fields.Nested(PlainItemSchema(), dump_only=True)


class ItemUpdateSchema(Schema):
    name = fields.Str()
    price = fields.Float()
    store_id = fields.Int()


class PlainStoreSchema(Schema):
    id = fields.Str(dump_only=True)  # Alternative is Load only where we never need to send to client this
    name = fields.Str(required=True)


class StoreSchema(PlainStoreSchema):
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
