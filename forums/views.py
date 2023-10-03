from django.views.decorators.http import require_POST
from django.db import transaction

from communalspace.decorators import firebase_authenticated
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import ForumPostSerializer
from .services import create_post
import json


@require_POST
@api_view(['POST'])
@firebase_authenticated()
@transaction.atomic()
def serve_create_forum_post(request):
    """
    This view serves as the endpoint to create a forum post.
    ----------------------------------------------------------
    request-data must contain:
    event_id: UUID string
    content: string
    anonymous: boolean

    * The user information will be taken from the firebase authentication.
    """
    request_data = json.loads(request.body.decode('utf-8'))
    created_post = create_post.handle_create_forum_post(request_data, user=request.user)
    response_data = ForumPostSerializer(created_post).data
    return Response(data=response_data)
