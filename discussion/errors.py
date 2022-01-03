from flask import current_app, json, jsonify, make_response, request
from marshmallow.exceptions import ValidationError
from sqlalchemy.exc import IntegrityError as v
from werkzeug.exceptions import Forbidden, HTTPException

from discussion.blueprints.api import bp


class InvalidCredentials(HTTPException):
    code = 401

    def __init__(self, message):
        super().__init__()
        self.message = message


class InvalidToken(Exception):
    code = 401

    def __init__(self, message):
        super().__init__()
        self.message = message
        self.name = 'Invalid Token'


class JsonIntegrityError(HTTPException):
    code = 400

    def __init__(self):
        super().__init__()
        self.message = 'Your input was invalid.'


class JsonPermissionDenied(Forbidden):
    code = 403

    def __init__(self, message):
        super().__init__()
        self.message = message


class JsonValidationError(HTTPException):
    code = 400

    def __init__(self, e):
        super().__init__()
        self.message = e.messages


class ResourceDoesNotExists(HTTPException):
    code = 400

    def __init__(self):
        super().__init__()
        self.message = 'The resource you searched for is does not exists.'


class ActionIsNotPossible(HTTPException):
    code = 400

    def __init__(self, message):
        super().__init__()
        self.message = message


class InvalidAttemp(HTTPException):
    code = 500

    def __init__(self):
        super().__init__()
        self.message = 'Server responded with an error.'


@current_app.errorhandler(ActionIsNotPossible)
@current_app.errorhandler(ResourceDoesNotExists)
@current_app.errorhandler(JsonIntegrityError)
@current_app.errorhandler(JsonPermissionDenied)
@current_app.errorhandler(InvalidAttemp)
@current_app.errorhandler(InvalidCredentials)
@current_app.errorhandler(InvalidToken)
@current_app.errorhandler(JsonValidationError)
def error(e):
    response = make_response()
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.message,
    })
    response.content_type = "application/json"
    response.status = e.code
    return response