from django.core.exceptions import ObjectDoesNotExist
from typing import Optional, Tuple

from .haversine import haversine
from ..models import Location


def get_space_from_coordinates(latitude: float, longitude: float) -> Optional[Location]:
    matching_space = Location.objects.filter(latitude=latitude, longitude=longitude)
    if len(matching_space) > 0:
        return matching_space[0]

    else:
        return None


def get_space_by_id_or_raise_exception(location_id) -> Optional[Location]:
    matching_space = Location.objects.filter(id=location_id)
    if len(matching_space) > 0:
        return matching_space[0]

    else:
        raise ObjectDoesNotExist(f'Space with id {location_id} does not exist')


def get_nearby_locations(locations, latitude, longitude, radius_tolerance):
    nearby_locations = []
    for location in locations:
        distance_between_space_and_coordinate = haversine(
            latitude,
            longitude,
            location.latitude,
            location.longitude
        )

        if distance_between_space_and_coordinate <= radius_tolerance:
            nearby_locations.append(location)

    nearby_locations = sorted(
        nearby_locations,
        key=lambda x: haversine(latitude, longitude, x.latitude, x.longitude)
    )

    return nearby_locations


def parse_coordinate(lat_long_data) -> Tuple[float, float]:
    try:
        latitude = float(lat_long_data.get('latitude'))
        longitude = float(lat_long_data.get('longitude'))

    except (ValueError, TypeError):
        raise ValueError('Latitude and Longitude must be a valid floating point number')

    if abs(latitude) > 90:
        raise ValueError('Location latitude must be between -90 and 90')

    if abs(longitude) > 180:
        raise ValueError('Location longitude must be between -180 and 180')

    return latitude, longitude


def parse_coordinate_fail_silently(lat_long_data):
    try:
        return parse_coordinate(lat_long_data)

    except:
        return None, None
