from communalspace.decorators import firebase_authenticated
from django.db import transaction
from django.views.decorators.http import require_POST, require_GET
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import UserSerializer
from .services import user
import json


@require_POST
@api_view(['POST'])
@firebase_authenticated()
@transaction.atomic()
def serve_update_user_data(request):
    """
    This view serve as the endpoint to update user basic data
    and preference.
    ----------------------------------------------------------
    request-data must contain:
    full-name: string
    preferred-radius: integer
    location-track: boolean
    """
    request_data = json.loads(request.body.decode('utf-8'))
    user.handle_update_user_data(request.user, request_data)
    response_data = {'message': 'User data and preferences is successfully updated'}
    return Response(data=response_data)


@require_GET
@api_view(['GET'])
@firebase_authenticated()
def serve_get_user_data(request):
    """
    This view serve as the endpoint to get the request user data
    ----------------------------------------------------------
    """
    response_data = UserSerializer(request.user).data
    return Response(data=response_data)
