from communalspace.decorators import catch_exception_and_convert_to_invalid_request_decorator
from communalspace.firebase_admin import firebase as firebase_utils
from event.exceptions import InvalidCheckInCheckOutException
from event.choices import ParticipationType
from event.services import utils as event_utils
from django.core.exceptions import ObjectDoesNotExist
from participation.services.participation_helpers import (
    validate_event_is_on_going,
    validate_user_is_inside_event_location,
    validate_user_can_check_in,
    check_in_user,
    validate_user_is_attending_event,
    check_out_user,
    validate_assisting_user_is_manager_of_event,
    handle_reward_grant
)
from space.services import utils as space_utils
from users.services import utils as user_utils


def _validate_user_is_a_participant(participation):
    if participation is None or participation.get_participation_type() != ParticipationType.PARTICIPANT:
        raise InvalidCheckInCheckOutException('User is not a participant of event')


@catch_exception_and_convert_to_invalid_request_decorator((
        ObjectDoesNotExist,
        InvalidCheckInCheckOutException,
        ValueError))
def handle_participation_self_check_in_confirmation(request_data, user):
    latitude, longitude = space_utils.parse_coordinate(request_data)
    initiative = event_utils.get_initiative_by_id_or_raise_exception(request_data.get('event_id'))
    validate_event_is_on_going(initiative)

    user_participation = initiative.get_participation_by_participant(user)
    _validate_user_is_a_participant(user_participation)
    validate_user_can_check_in(user, user_participation)
    validate_user_is_inside_event_location(initiative, latitude, longitude)

    return check_in_user(user, initiative, user_participation)


def self_check_out_participant(user, attendable_participation, user_latitude, user_longitude):
    check_out_data = attendable_participation.self_check_out(user_latitude, user_longitude)
    user.remove_currently_attended_event()
    return handle_reward_grant(user, check_out_data, attendable_participation)


@catch_exception_and_convert_to_invalid_request_decorator((
        ObjectDoesNotExist,
        InvalidCheckInCheckOutException,
        ValueError))
def handle_participation_self_check_out_confirmation(request_data, user):
    latitude, longitude = space_utils.parse_coordinate_fail_silently(request_data)
    initiative = event_utils.get_initiative_by_id_or_raise_exception(request_data.get('event_id'))

    user_participation = initiative.get_participation_by_participant(user)
    _validate_user_is_a_participant(user_participation)
    validate_user_is_attending_event(user_participation)
    return self_check_out_participant(user, user_participation, user_latitude=latitude, user_longitude=longitude)


def _check_out_user_when_outside_event_location(user, initiative, participation, user_latitude, user_longitude):
    if not initiative.check_user_is_inside_event(user_latitude, user_longitude):
        return self_check_out_participant(
            user,
            participation,
            user_latitude=user_latitude,
            user_longitude=user_longitude
        )
    else:
        return False


@catch_exception_and_convert_to_invalid_request_decorator((
        ObjectDoesNotExist,
        InvalidCheckInCheckOutException,
        ValueError))
def handle_participation_automatic_check_out(request_data, user):
    latitude, longitude = space_utils.parse_coordinate_fail_silently(request_data)
    initiative = event_utils.get_initiative_by_id_or_raise_exception(request_data.get('event_id'))

    user_participation = initiative.get_participation_by_participant(user)
    _validate_user_is_a_participant(user_participation)
    validate_user_is_attending_event(user_participation)
    return _check_out_user_when_outside_event_location(user, initiative, user_participation, latitude, longitude)


def validate_volunteer_can_aid_check_in_and_out(event, volunteer, volunteer_latitude, volunteer_longitude):
    validate_user_is_inside_event_location(event, volunteer_latitude, volunteer_longitude)
    validate_assisting_user_is_manager_of_event(event, volunteer)


@catch_exception_and_convert_to_invalid_request_decorator((
        ObjectDoesNotExist,
        InvalidCheckInCheckOutException,
        ValueError))
def handle_participation_aided_check_in(request_data, aiding_volunteer):
    volunteer_latitude, volunteer_longitude = space_utils.parse_coordinate(request_data)
    initiative = event_utils.get_initiative_by_id_or_raise_exception(request_data.get('event_id'))
    validate_event_is_on_going(initiative)

    validate_volunteer_can_aid_check_in_and_out(initiative, aiding_volunteer, volunteer_latitude, volunteer_longitude)

    participant_id = firebase_utils.get_user_id_from_email_or_phone_number(request_data.get('participant_email_phone'))
    participant = user_utils.get_user_by_id_or_raise_exception(participant_id)

    user_participation = initiative.get_participation_by_participant(participant)
    _validate_user_is_a_participant(user_participation)
    validate_user_can_check_in(participant, user_participation)
    return check_in_user(participant, initiative, user_participation)


@catch_exception_and_convert_to_invalid_request_decorator((
        ObjectDoesNotExist,
        InvalidCheckInCheckOutException,
        ValueError))
def handle_participation_aided_check_out(request_data, aiding_volunteer):
    initiative = event_utils.get_initiative_by_id_or_raise_exception(request_data.get('event_id'))
    validate_event_is_on_going(initiative)

    volunteer_latitude, volunteer_longitude = space_utils.parse_coordinate(request_data)
    validate_volunteer_can_aid_check_in_and_out(initiative, aiding_volunteer, volunteer_latitude, volunteer_longitude)

    participant_id = firebase_utils.get_user_id_from_email_or_phone_number(request_data.get('participant_email_phone'))
    participant = user_utils.get_user_by_id_or_raise_exception(participant_id)

    user_participation = initiative.get_participation_by_participant(participant)
    _validate_user_is_a_participant(user_participation)
    validate_user_is_attending_event(user_participation)
    return check_out_user(participant, user_participation)

