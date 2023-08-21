from firebase_admin import auth, exceptions as firebase_exceptions
from .exceptions import UnauthorizedException
from .utils import get_id_token_from_authorization_header
from users import utils as users_utils


def firebase_authenticated():
    def decorator(view_function_to_decorate):
        def decorated_view_function(*args, **kwargs):
            try:
                request = args[0]
                id_token = get_id_token_from_authorization_header(request.headers.get('Authorization'))
                decoded_token = auth.verify_id_token(id_token)
                request.user = users_utils.get_or_create_user_by_id(decoded_token.get('user_id'))
                return view_function_to_decorate(*args, **kwargs)

            except firebase_exceptions.InvalidArgumentError:
                raise UnauthorizedException('Invalid token provided')

        return decorated_view_function

    return decorator
