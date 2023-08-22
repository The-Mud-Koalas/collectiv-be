from typing import Optional
from ..models import Space


def get_location_from_coordinates(latitude: float, longitude: float) -> Optional[Space]:
    matching_space = Space.objects.filter(latitude=latitude, longitude=longitude)
    if len(matching_space) > 0:
        return matching_space[0]

    else:
        return None
