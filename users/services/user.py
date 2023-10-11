from communalspace.decorators import catch_exception_and_convert_to_invalid_request_decorator
from communalspace.exceptions import InvalidRequestException
from event.services import utils as event_utils
from django.core.exceptions import ObjectDoesNotExist


def _validate_update_user_data_request(request_data):
    """
    Check if full name is string, with length more than 3 and less than 50, and is not null
    Check if preferred radius is a positive integer
    Check if location-track is a boolean
    """
    if not request_data.get('full-name'):
        raise InvalidRequestException('Full name must not be null')

    if not isinstance(request_data.get('full-name'), str):
        raise InvalidRequestException('Full name must be a string')

    if not (3 <= len(request_data.get('full-name')) <= 50):
        raise InvalidRequestException('Full name must have a minimum length of 3 and a maximum length of 50')

    if not isinstance(request_data.get('preferred-radius'), int):
        raise InvalidRequestException('Preferred radius must be an integer')

    if request_data.get('preferred-radius') <= 0:
        raise InvalidRequestException('Preferred radius must be a positive integer')

    if not isinstance(request_data.get('location-track'), bool):
        raise InvalidRequestException('Location tracking preference must be a boolean')


def _update_user_data(user, request_data):
    user.set_full_name(request_data.get('full-name'))
    user.set_preferred_radius(request_data.get('preferred-radius'))
    user.set_location_track(request_data.get('location-track'))


def handle_update_user_data(user, request_data):
    _validate_update_user_data_request(request_data)
    _update_user_data(user, request_data)


def handle_get_user_interest(user):
    return user.get_interests()


def _validate_subscribe_to_tags_request(request_data):
    if not isinstance(request_data.get('tags'), list):
        raise InvalidRequestException('Tags must be a list (of tag IDs)')


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_subscribe_to_tags(request_data, user):
    _validate_subscribe_to_tags_request(request_data)
    interests = event_utils.convert_tag_ids_to_tags(request_data.get('tags'))
    user.set_interests(interests)


def handle_get_user_current_event(user):
    base_data = {'is_currently_attending_event': user.is_currently_attending_event()}

    if base_data.get('is_currently_attending_event'):
        base_data['data'] = {
            'current_attended_event_id': user.get_currently_attended_event_id(),
            'current_attended_event_role': user.get_currently_attending_role(),
        }

    return base_data
