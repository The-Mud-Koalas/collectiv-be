from .models import EventReportSerializer
from .services import report
from communalspace.decorators import firebase_authenticated
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json


@require_POST
@api_view(['POST'])
@firebase_authenticated()
def serve_submit_event_report(request):
    """
    This view serves as the endpoint for application users to
    report an event.
    ----------------------------------------------------------
    request-body must contain:
    event_id: UUID string
    remarks: string
    """
    request_data = json.loads(request.body.decode('utf-8'))
    submitted_report = report.handle_submit_event_report(request_data, request.user)
    response_data = {
        "message": "Report is successfully submitted",
        "report_data": EventReportSerializer(submitted_report).data
    }
    return Response(data=response_data)



