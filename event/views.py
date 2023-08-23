from communalspace.decorators import firebase_authenticated
from django.db import transaction
from django.views.decorators.http import require_POST, require_GET
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import BaseEventSerializer, TagsSerializer
from .services import event, tags
import json


@require_POST
@api_view(['POST'])
@firebase_authenticated()
@transaction.atomic()
def serve_create_event(request):
    """
    This view serves as the endpoint to create event.
    ----------------------------------------------------------
    request-data must contain:
    name: string
    description: string (optional)
    is_project: boolean
    project_goal: float (optional, required if is_project is true)
    goal_measurement_unit: float (optional, required if is_project is true)
    min_num_of_volunteers: integer

    start_date_time: ISO datetime string
    end_date_time: ISO datetime string

    location_id: UUID string
    tags: list[string] (containing the tags ID for the event)
    """
    request_data = json.loads(request.body.decode('utf-8'))
    created_event = event.handle_create_event(request_data, user=request.user)
    response_data = BaseEventSerializer(created_event).data
    return Response(data=response_data)


@require_GET
@api_view(['GET'])
def serve_get_all_tags(request):
    """
    This view serves as the endpoint to get all registered tags
    ----------------------------------------------------------
    request-param must contain:
    NONE
    """
    all_tags = tags.handle_get_all_tags()
    response_data = TagsSerializer(all_tags, many=True).data
    return Response(data=response_data)


