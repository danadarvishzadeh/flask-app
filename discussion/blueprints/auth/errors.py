from discussion.blueprints.auth import bp
from flask import jsonify, request, json, make_response, current_app
from werkzeug.exceptions import HTTPException


class InvalidCredentials(HTTPException):
    code = 401
    status_code = 401
    def __init__(self, message):
        super().__init__()
        self.message = message


class InvalidToken(Exception):
    code = 401
    status_code = 401
    def __init__(self, message):
        super().__init__()
        self.message = message
        self.name = 'Invalid Token'


@bp.app_errorhandler(InvalidCredentials)
def invalid_auth_data(e):
    response = e.get_response()
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.message,
    })
    response.content_type = "application/json"
    response.status = e.code
    return response

@bp.app_errorhandler(InvalidToken)
def invalid_auth_data(e):
    response = make_response()
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.message,
    })
    response.content_type = "application/json"
    response.status = e.code
    return response
