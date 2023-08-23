from django.core.exceptions import ObjectDoesNotExist
from typing import Optional
from ..models import Space


def get_space_from_coordinates(latitude: float, longitude: float) -> Optional[Space]:
    matching_space = Space.objects.filter(latitude=latitude, longitude=longitude)
    if len(matching_space) > 0:
        return matching_space[0]

    else:
        return None


def get_space_by_id_or_raise_exception(location_id) -> Optional[Space]:
    matching_space = Space.objects.filter(id=location_id)
    if len(matching_space) > 0:
        return matching_space[0]

    else:
        raise ObjectDoesNotExist(f'Space with id {location_id} does not exist')
