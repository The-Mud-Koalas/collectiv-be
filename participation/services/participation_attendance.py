from communalspace.decorators import catch_exception_and_convert_to_invalid_request_decorator
from communalspace.exceptions import InvalidRequestException
from communalspace.firebase_admin import firebase as firebase_utils
from event.exceptions import InvalidCheckInCheckOutException
from event.choices import ParticipationType
from event.services import utils
from django.core.exceptions import ObjectDoesNotExist
from participation.services.attendance_helper import (
    validate_event_is_on_going,
    validate_user_is_inside_event_location,
    validate_user_can_check_in,
    check_in_user,
    validate_user_can_check_out,
    self_check_out_user,
    validate_user_is_a_volunteer,
    check_out_user,
    validate_assisting_user_is_manager_of_event
)
from space.services import utils as space_utils
from users.services import utils as user_utils


def _validate_user_is_a_participant(participation):
    if participation is None or participation.get_participation_type() != ParticipationType.PARTICIPANT:
        raise InvalidRequestException('User is not a participant of event')


@catch_exception_and_convert_to_invalid_request_decorator((
        ObjectDoesNotExist,
        InvalidCheckInCheckOutException,
        ValueError))
def handle_participation_self_check_in_confirmation(request_data, user):
    latitude, longitude = space_utils.parse_coordinate(request_data)
    initiative = utils.get_event_by_id_or_raise_exception(request_data.get('event_id'))
    validate_event_is_on_going(initiative)

    user_participation = initiative.get_participation_by_participant(user)
    _validate_user_is_a_participant(user_participation)
    validate_user_can_check_in(user, user_participation)
    validate_user_is_inside_event_location(initiative, latitude, longitude)

    return check_in_user(user, initiative, user_participation)


@catch_exception_and_convert_to_invalid_request_decorator((
        ObjectDoesNotExist,
        InvalidCheckInCheckOutException,
        ValueError))
def handle_participation_self_check_out_confirmation(request_data, user):
    latitude, longitude = space_utils.parse_coordinate_fail_silently(request_data)
    initiative = utils.get_event_by_id_or_raise_exception(request_data.get('event_id'))
    user_participation = initiative.get_participation_by_participant(user)
    _validate_user_is_a_participant(user_participation)
    validate_user_can_check_out(user_participation)
    return self_check_out_user(user, user_participation, user_latitude=latitude, user_longitude=longitude)


def _check_out_user_when_outside_event_location(user, initiative, participation, user_latitude, user_longitude):
    if not initiative.check_user_is_inside_event(user_latitude, user_longitude):
        return self_check_out_user(user, participation, user_latitude=user_latitude, user_longitude=user_longitude)
    else:
        return False


@catch_exception_and_convert_to_invalid_request_decorator((
        ObjectDoesNotExist,
        InvalidCheckInCheckOutException,
        ValueError))
def handle_participation_automatic_check_out(request_data, user):
    latitude, longitude = space_utils.parse_coordinate_fail_silently(request_data)
    initiative = utils.get_event_by_id_or_raise_exception(request_data.get('event_id'))
    user_participation = initiative.get_participation_by_participant(user)
    _validate_user_is_a_participant(user_participation)
    validate_user_can_check_out(user_participation)
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
    initiative = utils.get_event_by_id_or_raise_exception(request_data.get('event_id'))
    validate_event_is_on_going(initiative)
    validate_volunteer_can_aid_check_in_and_out(initiative, aiding_volunteer, volunteer_latitude, volunteer_longitude)

    checking_in_user_id = firebase_utils.get_user_id_from_email_or_phone_number(
        request_data.get('participant_email_phone')
    )

    checking_in_user = user_utils.get_user_by_id_or_raise_exception(checking_in_user_id)
    user_participation = initiative.get_participation_by_participant(checking_in_user)
    validate_user_can_check_in(checking_in_user, user_participation)
    return check_in_user(checking_in_user, initiative, user_participation)


@catch_exception_and_convert_to_invalid_request_decorator((
        ObjectDoesNotExist,
        InvalidCheckInCheckOutException,
        ValueError))
def handle_participation_aided_check_out(request_data, aiding_volunteer):
    initiative = utils.get_event_by_id_or_raise_exception(request_data.get('event_id'))
    validate_event_is_on_going(initiative)
    volunteer_latitude, volunteer_longitude = space_utils.parse_coordinate(request_data)
    validate_volunteer_can_aid_check_in_and_out(initiative, aiding_volunteer, volunteer_latitude, volunteer_longitude)

    checking_out_user_id = firebase_utils.get_user_id_from_email_or_phone_number(
        request_data.get('participant_email_phone')
    )

    checking_out_user = user_utils.get_user_by_id_or_raise_exception(checking_out_user_id)
    user_participation = initiative.get_participation_by_participant(checking_out_user)
    validate_user_can_check_out(user_participation)
    return check_out_user(checking_out_user, user_participation)






