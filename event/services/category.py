from communalspace.exceptions import InvalidRequestException
from communalspace import utils as communalspace_utils
from . import utils
from ..models import EventCategory


def _validate_create_event_category_request(request_data):
    if not isinstance(request_data.get('name'), str):
        raise InvalidRequestException('Category name must be a string')

    if len(request_data.get('name')) < 3:
        raise InvalidRequestException('Category name must not be less than 3 characters')


def _create_category_if_not_exist(request_data):
    category_name = request_data.get('name').lower()
    event_category = utils.get_category_from_name(request_data.get('name').lower())

    if event_category is None:
        event_category = EventCategory.objects.create(name=category_name)

    return event_category


def handle_create_event_category(request_data):
    request_data = communalspace_utils.trim_all_request_attributes(request_data)
    _validate_create_event_category_request(request_data)
    event_category = _create_category_if_not_exist(request_data)
    return event_category
