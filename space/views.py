from communalspace.decorators import firebase_authenticated
from django.db import transaction
from django.views.decorators.http import require_POST, require_GET
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import LocationSerializer
from .services import space, discover_space
import json


@require_POST
@api_view(['POST'])
@firebase_authenticated()
@transaction.atomic()
def serve_get_or_create_location(request):
    """
    This view serves as the endpoint to register new location.
    If the location matching the latitude and longitude already
    exists, the view will return the existing location.
    ----------------------------------------------------------
    request-data must contain:
    latitude: float
    longitude: float
    name: string
    """
    request_data = json.loads(request.body.decode('utf-8'))
    location = space.handle_get_or_create_location(request_data)
    response_data = LocationSerializer(location).data
    return Response(data=response_data)


@require_GET
@api_view(['GET'])
@firebase_authenticated()
def serve_get_nearby_non_subscribed_locations(request):
    """
    This view serves as the endpoint to get nearby locations that
    the user has not subscribed to. The view only return locations
    that have never been presented to the user.
    ----------------------------------------------------------
    request-param must contain:
    latitude: float
    longitude: float
    """
    request_data = request.GET
    nearby_non_subscribed_locations = discover_space.handle_get_nearby_non_subscribed_locations(
        request_data,
        request.user
    )
    response_data = LocationSerializer(nearby_non_subscribed_locations, many=True).data
    return Response(data=response_data)
