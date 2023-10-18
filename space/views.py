from communalspace.decorators import firebase_authenticated
from django.db import transaction
from django.views.decorators.http import require_POST, require_GET
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import LocationSerializer
from .services import space, discover_space
import json


@require_GET
@api_view(['GET'])
def serve_get_all_locations(request):
    all_locations = space.handle_get_all_locations()
    response_data = LocationSerializer(all_locations, many=True).data
    return Response(data=response_data)


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
    description: string (optional)
    """
    request_data = json.loads(request.body.decode('utf-8'))
    location = space.handle_get_or_create_location(request_data)
    response_data = LocationSerializer(location).data
    return Response(data=response_data)


@require_GET
@api_view(['GET'])
def serve_get_location_by_latitude_longitude(request):
    """
    This view serves as the endpoint to get the location matching
    latitude and longitude.
    ----------------------------------------------------------
    request-data must contain:
    latitude: float
    longitude: float
    """
    request_data = request.GET
    location = space.handle_get_location_by_latitude_longitude(request_data)
    response_data = LocationSerializer(location).data if location is not None else None
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


@require_POST
@api_view(['POST'])
@firebase_authenticated()
@transaction.atomic()
def serve_subscribe_or_neglect_location(request):
    """
    This view serves as the endpoint for users to subscribe to new
    location.
    ----------------------------------------------------------
    request-data must contain:
    location_id: UUID string
    subscribe: boolean
    """
    request_data = json.loads(request.body.decode('utf-8'))
    discover_space.handle_subscribe_or_neglect_location(request_data, request.user)
    response_data = {'message': 'Location preference is successfully saved'}
    return Response(data=response_data)


@require_GET
@api_view(['GET'])
@firebase_authenticated()
def serve_get_list_of_subscribed_locations(request):
    """
    This view serves as the endpoint to get the list of user's
    subscribed locations.
    ----------------------------------------------------------
    request-data must contain:
    None
    """
    subscribed_locations = discover_space.handle_get_list_of_subscribed_locations(request.user)
    response_data = LocationSerializer(subscribed_locations, many=True).data
    return Response(data=response_data)


@require_GET
@api_view(['GET'])
def serve_get_location_by_id(request, location_id):
    """
    This view serves as the endpoint to get the details of
    a location, given its ID.
    """
    location = space.handle_get_location_by_id(location_id)
    response_data = LocationSerializer(location).data
    return Response(data=response_data)

