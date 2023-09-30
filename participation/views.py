from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view
from rest_framework.response import Response
from communalspace.decorators import firebase_authenticated
from participation.services import (
    contribution,
    participation,
    participation_attendance,
    volunteer_attendance,
)

import json


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


@require_POST
@api_view(['POST'])
@firebase_authenticated()
def serve_volunteer_assisted_check_in(request):
    """
    This view serves as the endpoint to allow event managers to
    check in volunteers.

    The event manager must be in the event location when checking
    -in the volunteer. (tentative).
    ----------------------------------------------------------
    request-body must contain:
    event_id: UUID string
    volunteer_email_phone: string
    """
    request_data = json.loads(request.body.decode('utf-8'))
    volunteer_attendance.handle_volunteer_assisted_check_in(request_data, request.user)
    response_data = {'message': 'Volunteer successfully checked in'}
    return Response(data=response_data)


@require_POST
@api_view(['POST'])
@firebase_authenticated()
def serve_volunteer_self_check_out(request):
    """
    This view serves as the endpoint to allow volunteers
    to check out. Different from participant, they can check out
    anytime and anywhere, given that they might need to leave the space
    for the purpose of the event.

    It is their duration of volunteering that will be reported as a measure
    of communal space health.
    ----------------------------------------------------------
    request-body must contain:
    event_id: UUID string
    """
    request_data = json.loads(request.body.decode('utf-8'))
    volunteer_attendance.handle_volunteer_self_check_out(request_data, request.user)
    response_data = {'message': 'Volunteer successfully checked out'}
    return Response(data=response_data)


@require_POST
@api_view(['POST'])
@firebase_authenticated()
def serve_volunteer_grant_managerial_role(request):
    """
    This view serves as the endpoint to allow event managers (i.e. creator/volunteer
    that has been granted managerial role to grant managerial role to other
    volunteers.
    ----------------------------------------------------------
    request-body must contain:
    event_id: UUID string
    volunteer_email_phone: string
    """
    request_data = json.loads(request.body.decode('utf-8'))
    volunteer_attendance.handle_volunteer_grant_managerial_role(request_data, request.user)
    response_data = {'message': 'Manager role has been successfully granted to user'}
    return Response(data=response_data)


@require_POST
@api_view(['POST'])
@firebase_authenticated()
def serve_volunteer_mark_participant_contribution(request):
    """
    This view serves as the endpoint for volunteers to mark participant
    contribution.
    ----------------------------------------------------------
    request-body must contain:
    project_id: UUID string
    contributor_email_phone: string
    """
    request_data = json.loads(request.body.decode('utf-8'))
    contribution.handle_volunteer_mark_participant_contribution(request_data, request.user)
    response_data = {'message': 'Participant contribution has been added successfully'}
    return Response(data=response_data)


@require_POST
@api_view(['POST'])
@firebase_authenticated()
def serve_participant_volunteer_leave_events(request):
    """
    This view serves as the endpoint for participant and volunteers
    to leave the events that they are currently participating on.
    ----------------------------------------------------------
    request-body must contain:
    event_id: UUID string
    """
    request_data = json.loads(request.body.decode('utf-8'))
    participation.handle_participant_volunteer_leave_events(request_data, request.user)
    response_data = {'message': 'User participation is deleted successfully'}
    return Response(data=response_data)


