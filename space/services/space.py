from communalspace.exceptions import InvalidRequestException
from numbers import Number
from ..models import Location
from . import utils


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


def _create_location_from_request_data(request_data: dict) -> Location:
    return Location.objects.create(
        name=request_data.get('name'),
        latitude=request_data.get('latitude'),
        longitude=request_data.get('longitude')
    )


def handle_get_or_create_location(request_data: dict) -> Location:
    _validate_create_location_request(request_data)
    found_location = utils.get_space_from_coordinates(request_data.get('latitude'), request_data.get('longitude'))

    if found_location:
        return found_location

    else:
        return _create_location_from_request_data(request_data)

