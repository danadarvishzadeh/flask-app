
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Forbidden, HTTPException

__all__ = [
    'InvalidCredentials',
    'InvalidToken',
    'JsonIntegrityError',
    'JsonPermissionDenied',
    'JsonValidationError',
    'ResourceDoesNotExists',
    'ActionIsNotPossible',
    'InvalidAttemp'
]

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
    code = 404

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
