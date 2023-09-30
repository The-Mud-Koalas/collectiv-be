"""
1. Participant submit review
2. Volunteer submit review
3. Contributor submit review
"""
from .services import review
from communalspace.decorators import firebase_authenticated
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json


@require_POST
@api_view(['POST'])
@firebase_authenticated()
def serve_participant_volunteer_submit_review(request):
    """
    This view serves as the endpoint for participants
    to submit review to the event that they have participated in.
    The review can only be submitted when the participant
    has checked out.
    ----------------------------------------------------------
    request-body must contain:
    event_id: UUID string
    event_rating: integer
    event_comment: string
    """
    request_data = json.loads(request.body.decode('utf-8'))
    review.handle_participant_submit_review(request_data, request.user)
    response_data = {'message': 'Review has been added successfully'}
    return Response(data=response_data)


@require_POST
@api_view(['POST'])
@firebase_authenticated()
def serve_contributor_submit_review(request):
    """
    This view serves as the endpoint for contributors to submit
    review to the project they have contributed to.
     ----------------------------------------------------------
    request-body must contain:
    event_id: UUID string
    event_rating: integer
    event_comment: string
    """
    request_data = json.loads(request.body.decode('utf-8'))
    review.handle_contributor_submit_review(request_data, request.user)
    response_data = {'message': 'Review has been added successfully'}
    return Response(data=response_data)







