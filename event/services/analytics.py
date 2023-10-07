from . import utils
from communalspace.decorators import catch_exception_and_convert_to_invalid_request_decorator
from django.core.exceptions import ObjectDoesNotExist


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_get_event_analytics(request_data):
    return utils.get_event_by_id_or_raise_exception(request_data.get('event_id'))

