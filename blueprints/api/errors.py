from flask import json, make_response, request
from marshmallow.exceptions import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException, Forbidden

from discussion.blueprints.api import bp


class JsonIntegrityError(HTTPException):
    code = 400
    status_code = 400

    def __init__(self):
        super().__init__()
        self.message = 'Your input was invalid.'


class JsonPermissionDenied(Forbidden):
    code = 403
    status_code = 403

    def __init__(self):
        super().__init__()
        self.message = 'You are not allowed.'


class JsonValidationError(HTTPException):
    code = 400
    status_code = 400

    def __init__(self, e):
        super().__init__()
        self.messages = e.messages


class ResourceDoesNotExists(HTTPException):
    code = 400
    status_code = 400

    def __init__(self):
        super().__init__()
        self.message = 'The resource you searched for is does not exists.'


class ActionIsNotPossible(HTTPException):
    code = 400
    status_code = 400

    def __init__(self, message):
        super().__init__()
        self.message = message


class InvalidAttemp(HTTPException):
    code = 500
    status_code = 500

    def __init__(self):
        super().__init__()
        self.message = 'Server responded with an error.'


@bp.errorhandler(InvalidAttemp)
@bp.errorhandler(ActionIsNotPossible)
@bp.errorhandler(ResourceDoesNotExists)
@bp.errorhandler(JsonIntegrityError)
@bp.errorhandler(JsonPermissionDenied)
def not_allowed(e):
    response = make_response()
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.message,
    })
    response.content_type = "application/json"
    response.status = e.code
    return response

@bp.errorhandler(JsonValidationError)
def invalid_input_data(e):
    response = make_response()
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.messages,
    })
    response.content_type = "application/json"
    response.status = e.code
    return response
