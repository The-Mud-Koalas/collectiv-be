from analytics.services import analytics
from analytics.models import InitiativeAnalyticsSerializer
from django.views.decorators.http import require_GET
from rest_framework.decorators import api_view
from rest_framework.response import Response


@require_GET
@api_view(['GET'])
def serve_get_event_analytics(request):
    """
    This view serves as the endpoint to get the analytics of an event.
    ----------------------------------------------------------
    request-param must contain:
    event_id: UUID string
    """
    request_data = request.GET
    event = analytics.handle_get_event_analytics(request_data)
    response_data = InitiativeAnalyticsSerializer(event).data
    return Response(data=response_data)
