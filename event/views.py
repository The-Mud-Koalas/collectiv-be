from communalspace import paginators
from communalspace import utils as app_utils
from communalspace.decorators import firebase_authenticated
from communalspace.serializers import PaginatorSerializer
from django.db import transaction
from django.views.decorators.http import require_POST, require_GET
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import BaseEventSerializer, EventCategorySerializer, TagsSerializer
from .services import (
    category,
    create_event,
    discover_event,
    participation,
    participation_attendance,
    tags,
)
import json


@require_POST
@api_view(['POST'])
def serve_create_event_category(request):
    """
    This view serves as the endpoint to register new event category.
    In the case when the category has been registered, the request will
    be neglected.
    ----------------------------------------------------------
    request-data must contain:
    name: string
    """
    request_data = json.loads(request.body.decode('utf-8'))
    event_category = category.handle_create_event_category(request_data)
    response_data = EventCategorySerializer(event_category).data
    return Response(data=response_data)


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
    created_event = create_event.handle_create_event(request_data, user=request.user)
    response_data = BaseEventSerializer(created_event).data
    return Response(data=response_data)


@require_POST
@api_view(['POST'])
@firebase_authenticated()
def serve_upload_event_image(request):
    """
    This view serves as the endpoint to upload image of event.
    ----------------------------------------------------------
    request data must contain:
    event_id: UUID string
    event_image: Image Blob
    """
    request_data = request.POST.dict()
    request_file = request.FILES.get('event_image')
    create_event.handle_upload_event_image(request_data, image_file=request_file, user=request.user)
    response_data = {'message': 'Image of event is successfully uploaded'}
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


@require_POST
@api_view(['POST'])
def serve_get_or_create_tags(request):
    """
    This view serves as the endpoint to register multiple tags.
    In the case when a tag with the same name exists in the database,
    the new insertion request will be neglected.
    ----------------------------------------------------------
    request-body must contain:
    tags: list of strings
    """
    request_data = json.loads(request.body.decode('utf-8'))
    retrieved_tags = tags.handle_get_or_create_tags(request_data)
    response_data = TagsSerializer(retrieved_tags, many=True).data
    return Response(data=response_data)


@require_GET
@api_view(['GET'])
def serve_get_event_by_id(request, event_id):
    """
    This view serves as the endpoint to get an event based on ID
    ----------------------------------------------------------
    request-context must contain:
    event_id
    """
    event = discover_event.handle_get_event_by_id(event_id)
    response_data = BaseEventSerializer(event).data
    return Response(data=response_data)


@require_GET
@api_view(['GET'])
def serve_get_event_image_by_id(request, event_id):
    """
    This view serves as the endpoint to get the event uploaded
    image based on its ID.
    ----------------------------------------------------------
    request-context must contain:
    event_id
    """
    event_image_file = discover_event.handle_get_event_image_by_id(event_id)
    if event_image_file:
        return app_utils.generate_file_response(event_image_file)

    else:
        return Response(data={'message': 'No image has been uploaded for the event'})


@require_GET
@api_view(['GET'])
@firebase_authenticated()
def serve_get_nearby_events(request):
    """
    This view serves as the endpoint to get the nearby events
    from the given coordinate. This view will be integrated
    with the push notification system to alert user of the
    nearby events.
    ----------------------------------------------------------
    request-param must contain:
    latitude: float
    longitude: float
    """
    request_data = request.GET
    nearby_events = discover_event.handle_get_interest_based_nearby_events(request_data, request.user)
    response_data = BaseEventSerializer(nearby_events, many=True).data
    return Response(data=response_data)


@require_GET
@api_view(['GET'])
def serve_search_events(request):
    """
    This view serves as the endpoint to search for (nearby) events by using
    the user's sent locations. This view also considers name-based and
    tag-based search.

    The results are presented using pagination to reduce the amount of data
    transferred in one fetch.
    ----------------------------------------------------------
    request-param may contain:
    latitude: float
    longitude: float
    name: string
    tags: comma separated strings (example: go-green,body-building)

    limit: integer (number of results to be displayed in one fetch)
    page: integer
    """
    request_data = request.GET
    events = discover_event.handle_search_events(request_data)
    limit, page_number = app_utils.parse_limit_page(request_data.get('limit'), request_data.get('page'))
    paginated_result = paginators.paginate_result(events, limit, page_number)
    data = PaginatorSerializer(paginated_result, BaseEventSerializer).data
    return Response(data=data)


@require_POST
@api_view(['POST'])
@firebase_authenticated()
def serve_register_user_participation_to_event(request):
    """
    This view serves as the endpoint to register user
    as an event participant. The event current status should
    not be completed or cancelled.
    ----------------------------------------------------------
    request-body must contain:
    event_id: UUID string
    """
    request_data = json.loads(request.body.decode('utf-8'))
    participation.handle_register_user_participation_to_event(request_data, request.user)
    response_data = {'message': 'Participant is successfully added'}
    return Response(data=response_data)


@require_POST
@api_view(['POST'])
@firebase_authenticated()
def serve_register_user_volunteer_to_event(request):
    """
    This view serves as the endpoint to register user
    as an event volunteer. The event current status should
    not be completed or cancelled.
    ----------------------------------------------------------
    request-body must contain:
    event_id: UUID string
    """
    request_data = json.loads(request.body.decode('utf-8'))
    participation.handle_register_user_volunteering_to_event(request_data, request.user)
    response_data = {'message': 'Volunteer is successfully added'}
    return Response(data=response_data)


@require_POST
@api_view(['POST'])
@firebase_authenticated()
def serve_participation_self_check_in_confirmation(request):
    """
    This view serves as the endpoint to allow user to perform
    self check in (as a participant) to an event.
    ----------------------------------------------------------
    request-body must contain:
    event_id: UUID string
    latitude: float
    longitude: float
    """
    request_data = json.loads(request.body.decode('utf-8'))
    participation_attendance.handle_participation_self_check_in_confirmation(request_data, request.user)
    response_data = {'message': 'Participant successfully checked in'}
    return Response(data=response_data)


@require_POST
@api_view(['POST'])
@firebase_authenticated()
def serve_participation_self_check_out_confirmation(request):
    """
    This view serves as the endpoint to allow user to perform
    self check out (as a participant) from an event.
    ----------------------------------------------------------
    request-body must contain:
    event_id: UUID string
    latitude: float
    longitude: float
    """
    request_data = json.loads(request.body.decode('utf-8'))
    participation_attendance.handle_participation_self_check_out_confirmation(request_data, request.user)
    response_data = {'message': 'Participant successfully checked out'}
    return Response(data=response_data)


@require_POST
@api_view(['POST'])
@firebase_authenticated()
def serve_participation_automated_check_out(request):
    """
    This view serves as the endpoint to automatically check out user
    when the user exited the location.
    ----------------------------------------------------------
    request-body must contain:
    event_id: UUID string
    latitude: float
    longitude: float
    """
    request_data = json.loads(request.body.decode('utf-8'))
    check_out_status = participation_attendance.handle_participation_automatic_check_out(request_data, request.user)
    response_data = {'checked_out': check_out_status}
    return Response(data=response_data)



