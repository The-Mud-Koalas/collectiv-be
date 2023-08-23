from firebase_admin import auth, exceptions as firebase_exceptions
from .exceptions import UnauthorizedException, InvalidRequestException
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


def catch_exception_and_convert_to_invalid_request_decorator(exception_types: tuple):
    """
    This function is a decorator to service functions that need to convert
    ObjectDoesNotExist exception to InvalidRequestException.
    This decorator will catch ObjectDoesNotExist exceptions and raise
    an InvalidRequestException to be caught in the caller function.
    """
    def decorator(func_to_decorate):
        def decorated_function(*args, **kwargs):
            try:
                return func_to_decorate(*args, **kwargs)
            except exception_types as exception:
                raise InvalidRequestException(str(exception))
        return decorated_function
    return decorator
