from communalspace.decorators import catch_exception_and_convert_to_invalid_request_decorator
from . import utils
from ..models import Location


def _get_non_notified_nearby_locations(nearby_locations, user):
    user_notified_locations = user.get_notified_locations()
    return list(filter(lambda location: location not in user_notified_locations, nearby_locations))


@catch_exception_and_convert_to_invalid_request_decorator((ValueError,))
def handle_get_nearby_non_subscribed_locations(request_data, user):
    all_locations = Location.objects.all()
    latitude, longitude = utils.parse_lat_long(request_data)
    nearby_locations = utils.get_nearby_locations(
        all_locations,
        latitude,
        longitude,
        user.get_preferred_radius()
    )
    return _get_non_notified_nearby_locations(nearby_locations, user)




