from communalspace.exceptions import InvalidRequestException
from numbers import Number
from ..models import Location
from . import utils, haversine


def _validate_create_location_request(request_data: dict):
    if not isinstance(request_data.get('name'), str):
        raise InvalidRequestException('Location name must be a string')

    if not (3 < len(request_data.get('name')) <= 50):
        raise InvalidRequestException('Location name must be between 3 and 50 characters')

    if not isinstance(request_data.get('latitude'), Number):
        raise InvalidRequestException('Location latitude must be a float')

    if not isinstance(request_data.get('longitude'), Number):
        raise InvalidRequestException('Location longitude must be a float')

    if abs(request_data.get('latitude')) > 90:
        raise InvalidRequestException('Location latitude must be between -90 and 90')

    if abs(request_data.get('longitude')) > 180:
        raise InvalidRequestException('Location longitude must be between -180 and 180')

    if request_data.get('description') is not None and not isinstance(request_data.get('description'), str):
        raise InvalidRequestException('Location description must be a string')


def _create_location_from_request_data(request_data: dict) -> Location:
    return Location.objects.create(
        name=request_data.get('name'),
        latitude=request_data.get('latitude'),
        longitude=request_data.get('longitude'),
        description=request_data.get('description', None),
    )


def handle_get_or_create_location(request_data: dict) -> Location:
    _validate_create_location_request(request_data)
    found_location = utils.get_space_from_coordinates(request_data.get('latitude'), request_data.get('longitude'))

    if found_location:
        return found_location

    else:
        return _create_location_from_request_data(request_data)


def handle_get_all_locations():
    return Location.objects.all()


def handle_get_location_by_id(location_id):
    return utils.get_space_by_id_or_raise_exception(location_id)


def handle_get_location_by_latitude_longitude(request_data):
    latitude, longitude = utils.parse_coordinate(request_data)
    all_locations = Location.objects.all()
    sorted_locations = sorted(
        all_locations,
        key=lambda l: haversine.haversine(
            latitude,
            longitude,
            l.latitude,
            l.longitude)
    )

    if len(sorted_locations) > 0:
        return sorted_locations[0]

    else:
        return None
