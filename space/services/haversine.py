import math


def haversine(lat1, long1, lat2, long2):
    # Radius in KM
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
