from communalspace import utils as app_utils
from communalspace.exceptions import InvalidRequestException
from communalspace.decorators import catch_exception_and_convert_to_invalid_request_decorator
from django.core.exceptions import ObjectDoesNotExist
from . import utils
from ..models import Location


def _get_non_notified_nearby_locations(nearby_locations, user):
    user_notified_locations = user.get_notified_locations()
    return list(filter(lambda location: location not in user_notified_locations, nearby_locations))


@catch_exception_and_convert_to_invalid_request_decorator((ValueError,))
def handle_get_nearby_non_subscribed_locations(request_data, user):
    all_locations = Location.objects.all()
    latitude, longitude = utils.parse_coordinate(request_data)
    nearby_locations = utils.get_nearby_locations(
        all_locations,
        latitude,
        longitude,
        user.get_preferred_radius()
    )
    return _get_non_notified_nearby_locations(nearby_locations, user)


def validate_subscribe_or_neglect_location_request(request_data):
    if not app_utils.is_valid_uuid_string(request_data.get('location_id')):
        raise InvalidRequestException('Location ID must be a valid UUID string')

    if not isinstance(request_data.get('subscribe'), bool):
        raise InvalidRequestException('Subscribe must be a valid boolean')


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_subscribe_or_neglect_location(request_data, user):
    validate_subscribe_or_neglect_location_request(request_data)
    location = utils.get_space_by_id_or_raise_exception(request_data.get('location_id'))
    user.add_to_notified_locations(location, request_data.get('subscribe'))


def handle_get_list_of_subscribed_locations(user):
    return user.get_subscribed_locations()
