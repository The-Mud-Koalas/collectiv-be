from .models import UserSerializer
from .services import user
from communalspace.decorators import firebase_authenticated
from django.db import transaction
from django.views.decorators.http import require_POST, require_GET
from event.models import TagsSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
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
    full_name: string
    preferred_radius: integer
    location_track: boolean
    """
    request_data = json.loads(request.body.decode('utf-8'))
    user.handle_update_user_data(request.user, request_data)
    response_data = {'message': 'User data and preferences is successfully updated'}
    return Response(data=response_data)


@require_POST
@api_view(['POST'])
@firebase_authenticated()
@transaction.atomic()
def serve_update_user_location_tracking_preference(request):
    """
    This view serves as the endpoint to update the user's
    location tracking preference.
    ----------------------------------------------------------
    location_track: boolean
    """
    request_data = json.loads(request.body.decode('utf-8'))
    user.handle_update_user_location_tracking_preference(request_data, request.user)
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


@require_GET
@api_view(['GET'])
@firebase_authenticated()
def serve_get_user_interests(request):
    """
    This view serves as the endpoint to get the list of user's
    interests.
    """
    user_interests = user.handle_get_user_interest(request.user)
    response_data = TagsSerializer(user_interests, many=True).data
    return Response(data=response_data)


@require_POST
@api_view(['POST'])
@firebase_authenticated()
def serve_subscribe_to_tags(request):
    """
    This view serves as the endpoint to update user subscribed tags.
    ----------------------------------------------------------
    request-body must contain:
    tags: List of tag IDs

    {
        "tags": [
            "b2a602fa-656a-4a26-adcd-9ca2b77859f1",
            "3b8a53b4-522c-42b1-82e5-35c79391fc96",
        ]
    }
    """
    request_data = json.loads(request.body.decode('utf-8'))
    user.handle_subscribe_to_tags(request_data, request.user)
    response_data = {'message': 'User interest is successfully updated'}
    return Response(data=response_data)


@require_GET
@api_view(['GET'])
@firebase_authenticated()
def serve_get_user_current_event(request):
    """
    This view serves as the endpoint to get user's current
    attended event.
    ----------------------------------------------------------
    """
    response_data = user.handle_get_user_current_event(request.user)
    return Response(data=response_data)


@require_POST
@api_view(['POST'])
@firebase_authenticated()
def serve_update_user_prompted_location_tracking(request):
    """
    This view serves as the endpoint to update whether the user
    has been prompted for location tracking.
    ----------------------------------------------------------
    request-param must contain:
    has_been_prompted: Boolean
    """
    request_data = json.loads(request.body.decode('utf-8'))
    user.handle_update_user_prompted_location_tracking(request_data, request.user)
    response_data = {'message': 'User location tracking prompt status is successfully updated'}
    return Response(data=response_data)




