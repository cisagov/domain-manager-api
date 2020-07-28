from marshmallow import Schema, fields


class DomainSerializer(Schema):
    """
    Domain Models
    """

    name = fields.Str(required=True)
    url = fields.Str(required=True)
    cb_timestamp = fields.DateTime()
    lub_timestamp = fields.DateTime()
