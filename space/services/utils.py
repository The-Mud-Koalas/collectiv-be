from communalspace import utils as app_utils
from django.core.exceptions import ObjectDoesNotExist
from typing import Optional
from . import utils
from ..models import Location
import math


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


def haversine(lat1, long1, lat2, long2):
    earth_radius = 6371

    # Converting degrees to radians
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    long1 = math.radians(long1)
    long2 = math.radians(long2)

    distance_latitude = lat1 - lat2
    distance_longitude = long1 - long2

    a = math.sin(distance_latitude / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(distance_longitude / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return earth_radius * c


def get_nearby_locations(locations, latitude, longitude, radius_tolerance):
    nearby_locations = []
    for location in locations:
        distance_between_space_and_coordinate = utils.haversine(
            latitude,
            longitude,
            location.latitude,
            location.longitude
        )

        if distance_between_space_and_coordinate <= radius_tolerance:
            nearby_locations = app_utils.insert_to_list_with_key(
                nearby_locations,
                location,
                key=lambda x: utils.haversine(latitude, longitude, x.latitude, x.longitude)
            )

    return nearby_locations


def parse_lat_long(lat_long_data):
    try:
        return [
            float(lat_long_data.get('latitude')),
            float(lat_long_data.get('longitude'))
        ]

    except (ValueError, TypeError):
        raise ValueError('Latitude and Longitude must be a valid floating point number')
