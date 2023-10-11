from analytics.services import analytics
from django.views.decorators.http import require_GET
from rest_framework.decorators import api_view
from rest_framework.response import Response


@require_GET
@api_view(['GET'])
def serve_get_complete_event_analytics(request, event_id):
    """
    This view serves as the endpoint to get the analytics of an event.
    ----------------------------------------------------------
    request-path must contain:
    event_id: UUID string
    """
    event_analytics_data = analytics.handle_get_complete_event_analytics(event_id)
    return Response(data=event_analytics_data)


@require_GET
@api_view(['GET'])
def serve_get_total_participants_of_events_in_location(request, location_id):
    """
    This view serves as the endpoint to get the number of
    volunteers, contributors, and participants that have participated
    an event in the location.
    ----------------------------------------------------------
    request-path must contain:
    location_id: UUID string
    """
    participation_data = analytics.handle_get_total_participants_of_events_in_location(location_id)
    return Response(data=participation_data)
