from communalspace.decorators import catch_exception_and_convert_to_invalid_request_decorator
from communalspace.exceptions import InvalidRequestException
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
    self_check_out_user
)
from space.services import utils as space_utils


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
    latitude, longitude = space_utils.parse_coordinate(request_data)
    initiative = utils.get_event_by_id_or_raise_exception(request_data.get('event_id'))
    user_participation = initiative.get_participation_by_participant(user)
    _validate_user_is_a_participant(user_participation)
    validate_user_can_check_out(user_participation)
    return _check_out_user_when_outside_event_location(user, initiative, user_participation, latitude, longitude)



