from communalspace.decorators import firebase_authenticated
from django.db import transaction
from django.views.decorators.http import require_POST
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import SpaceSerializer
from .services import space

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
    response_data = SpaceSerializer(location).data
    return Response(data=response_data)


