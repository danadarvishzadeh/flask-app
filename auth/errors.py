from views import auth
from api.errors import unauthorized

@auth.app_error_handler
def auth_error():
    return unauthorized('Invalid credentials')