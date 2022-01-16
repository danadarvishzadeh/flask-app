from flasgger import Schema, fields



class ErrorSchema(Schema):

    code = fields.String()
    message = fields.String()
    description = fields.String()


class OkResponse(Schema):

    response = fields.String(default='Ok.')