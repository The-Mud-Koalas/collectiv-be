from django.db import transaction
from django.views.decorators.http import require_POST, require_GET
from event.models import BaseEventParticipationSerializer, BaseEventSerializer, ParticipationSerializerWithEventData
from rest_framework.decorators import api_view
from rest_framework.response import Response
from communalspace.decorators import firebase_authenticated
from participation.services import (
    contribution,
    participation,
    participation_attendance,
    volunteer_attendance,
    viewing_participation,
)

import json


@require_POST
@api_view(['POST'])
@firebase_authenticated()
@transaction.atomic()
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
    participation.handle_register_user_participation_to_initiative(request_data, request.user)
    response_data = {'message': 'Participant is successfully added'}
    return Response(data=response_data)


@require_POST
@api_view(['POST'])
@firebase_authenticated()
@transaction.atomic()
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
@transaction.atomic()
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
    response_data = {'message': 'User left event successfully'}
    return Response(data=response_data)


@require_POST
@api_view(['POST'])
@firebase_authenticated()
@transaction.atomic()
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
    check_in_data = participation_attendance.handle_participation_self_check_in_confirmation(request_data, request.user)
    response_data = {
        'message': 'Participant successfully checked in',
        'data': check_in_data
    }
    return Response(data=response_data)


@require_POST
@api_view(['POST'])
@firebase_authenticated()
@transaction.atomic()
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
    check_out_data = participation_attendance.handle_participation_self_check_out_confirmation(request_data, request.user)
    response_data = {
        'message': 'Participant successfully checked out',
        'data': check_out_data
    }
    return Response(data=response_data)


@require_POST
@api_view(['POST'])
@firebase_authenticated()
@transaction.atomic()
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
    check_out_data = participation_attendance.handle_participation_automatic_check_out(request_data, request.user)

    if check_out_data:
        response_data = {'checked_out': True, 'data': check_out_data}
    else:
        response_data = {'checked_out': False}

    return Response(data=response_data)


@require_POST
@api_view(['POST'])
@firebase_authenticated()
@transaction.atomic()
def serve_participation_aided_check_in(request):
    """
    This view serves as the endpoint to allow event managers to check in
    user to the event initiative.
    ----------------------------------------------------------
    request-body must contain:
    event_id: UUID string
    latitude: float
    longitude: float
    participant_email_phone: string Registered email or phone number of the participant
    """
    request_data = json.loads(request.body.decode('utf-8'))
    check_in_data = participation_attendance.handle_participation_aided_check_in(request_data, request.user)
    response_data = {
        'message': 'Participant successfully checked in',
        'data': check_in_data
    }
    return Response(data=response_data)


@require_POST
@api_view(['POST'])
@firebase_authenticated()
@transaction.atomic()
def serve_participation_aided_check_out(request):
    """
    This view serves as the endpoint to allow event managers to
    check out users to the event initiative.
    ----------------------------------------------------------
    request-body must contain:
    event_id: UUID string
    latitude: float
    longitude: float
    participant_email_phone: string Registered email or phone number of the participant
    """
    request_data = json.loads(request.body.decode('utf-8'))
    check_out_data = participation_attendance.handle_participation_aided_check_out(request_data, request.user)
    response_data = {
        'message': 'Participant successfully checked out',
        'data': check_out_data
    }
    return Response(data=response_data)


@require_POST
@api_view(['POST'])
@firebase_authenticated()
@transaction.atomic()
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
    check_in_data = volunteer_attendance.handle_volunteer_assisted_check_in(request_data, request.user)
    response_data = {'message': 'Volunteer successfully checked in', 'data': check_in_data}
    return Response(data=response_data)


@require_POST
@api_view(['POST'])
@firebase_authenticated()
@transaction.atomic()
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
    check_out_data = volunteer_attendance.handle_volunteer_self_check_out(request_data, request.user)
    response_data = {'message': 'Volunteer successfully checked out', 'data': check_out_data}
    return Response(data=response_data)


@require_POST
@api_view(['POST'])
@firebase_authenticated()
@transaction.atomic()
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
@transaction.atomic()
def serve_volunteer_mark_participant_contribution(request):
    """
    This view serves as the endpoint for volunteers to mark participant
    contribution.
    ----------------------------------------------------------
    request-body must contain:
    event_id: UUID string
    contributor_email_phone: string
    amount_contributed: integer
    """
    request_data = json.loads(request.body.decode('utf-8'))
    contribution_data = contribution.handle_volunteer_mark_participant_contribution(request_data, request.user)
    response_data = {'message': 'Participant contribution has been added successfully', 'data': contribution_data}
    return Response(data=response_data)


@require_GET
@api_view(['GET'])
@firebase_authenticated()
def serve_get_user_participations(request):
    """
    This view serves as the endpoint to get the
    list of user's participation.
    ----------------------------------------------------------
    request-param may contain:
    type: participant/volunteer
    status: past/on going/future
    """
    request_data = request.GET
    participations = viewing_participation.handle_get_user_participations(request_data, request.user)
    response_data = ParticipationSerializerWithEventData(participations, many=True).data
    return Response(data=response_data)


@require_GET
@api_view(['GET'])
@firebase_authenticated()
def serve_get_user_contributions(request):
    """
    This view serves as the endpoint to get the
    list of user's contribution.
    ----------------------------------------------------------
    """
    participations = viewing_participation.handle_get_user_contributions(request.user)
    response_data = ParticipationSerializerWithEventData(participations, many=True).data
    return Response(data=response_data)


@require_GET
@api_view(['GET'])
@firebase_authenticated()
def serve_get_created_events(request):
    """
    This view serves as the endpoint to get the list of user's
    created event.
    ----------------------------------------------------------
    request-param may contain:
    type: initiative/project
    status: past/on going/future
    """
    request_data = request.GET
    events = viewing_participation.handle_get_created_events(request_data, request.user)
    response_data = BaseEventSerializer(events, many=True).data
    return Response(data=response_data)


@require_GET
@api_view(['GET'])
@firebase_authenticated()
def serve_check_user_registration_to_event(request):
    """
    This view serves as the endpoint to check whether a user has
    already registered in an event.
    ----------------------------------------------------------
    request-param must contain:
    event_id: UUID string
    """
    request_data = request.GET
    user_participation = viewing_participation.handle_check_user_registration_to_event(request_data, request.user)
    if user_participation is None:
        response_data = {'is_registered': False}
    else:
        response_data = {
            'is_registered': True,
            'data': BaseEventParticipationSerializer(user_participation).data
        }

    return Response(data=response_data)







