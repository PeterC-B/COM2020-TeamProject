from marshmallow import Schema, fields

class RouteQuerySchema(Schema):
    query_id = fields.UUID()
    user_id = fields.UUID(allow_none=True)
    start = fields.Str()
    end = fields.Str()
    weights_json = fields.Dict()
    chosen_route_rank = fields.Int()
    chosen_route_path = fields.List(fields.Int())
    timestamp = fields.DateTime()
    name = fields.String()