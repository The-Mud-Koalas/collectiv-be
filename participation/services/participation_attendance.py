from communalspace.decorators import catch_exception_and_convert_to_invalid_request_decorator
from communalspace.exceptions import InvalidRequestException
from communalspace.settings import POINTS_PER_ATTENDANCE
from event.services import utils
from event.exceptions import InvalidCheckInCheckOutException
from django.core.exceptions import ObjectDoesNotExist
from space.services import utils as space_utils


def validate_event_is_on_going(event):
    if not event.is_ongoing():
        raise InvalidRequestException('Event has not started or has been completed')


def _validate_user_is_a_participant(participation):
    if participation is None or participation.get_participation_type() != 'participant':
        raise InvalidRequestException('User is not a participant of event')


def _validate_user_is_inside_event_location(event, user_latitude, user_longitude):
    if not event.check_user_is_inside_event(user_latitude, user_longitude):
        raise InvalidRequestException(f'User is currently not inside event location')


def _validate_user_can_check_in(user, participation):
    _validate_user_is_a_participant(participation)

    if user.is_currently_attending_event() or participation.get_is_currently_attending():
        raise InvalidCheckInCheckOutException('User is currently attending an event')


def _check_in_user(user, initiative, participation):
    check_in_data = participation.check_in()
    user.set_currently_attended_event(initiative)
    user.set_currently_attending_role(participation.get_participation_type())
    return check_in_data


@catch_exception_and_convert_to_invalid_request_decorator((
        ObjectDoesNotExist,
        InvalidCheckInCheckOutException,
        ValueError))
def handle_participation_self_check_in_confirmation(request_data, user):
    latitude, longitude = space_utils.parse_coordinate(request_data)
    initiative = utils.get_event_by_id_or_raise_exception(request_data.get('event_id'))
    validate_event_is_on_going(initiative)

    user_participation = initiative.get_participation_by_participant(user)
    _validate_user_can_check_in(user, user_participation)
    _validate_user_is_inside_event_location(initiative, latitude, longitude)
    return _check_in_user(user, initiative, user_participation)


def _validate_user_can_check_out(participation):
    _validate_user_is_a_participant(participation)

    if not participation.get_is_currently_attending():
        raise InvalidCheckInCheckOutException('User is currently not attending event')


def _check_out_user(user, participation):
    check_out_data = participation.check_out()
    user.remove_currently_attended_event()

    if participation.is_eligible_for_reward() and not participation.has_been_rewarded():
        user.add_reward(POINTS_PER_ATTENDANCE)
        participation.set_rewarded(True)
        check_out_data['is_rewarded'] = True
    else:
        check_out_data['is_rewarded'] = False

    return check_out_data


@catch_exception_and_convert_to_invalid_request_decorator((
        ObjectDoesNotExist,
        InvalidCheckInCheckOutException,
        ValueError))
def handle_participation_self_check_out_confirmation(request_data, user):
    initiative = utils.get_event_by_id_or_raise_exception(request_data.get('event_id'))
    user_participation = initiative.get_participation_by_participant(user)
    _validate_user_can_check_out(user_participation)
    return _check_out_user(user, user_participation)


def _check_out_user_when_outside_event_location(event, participation, user_latitude, user_longitude):
    if not event.check_user_is_inside_event(user_latitude, user_longitude):
        participation.check_out()
        return True
    else:
        return False


@catch_exception_and_convert_to_invalid_request_decorator((
        ObjectDoesNotExist,
        InvalidCheckInCheckOutException,
        ValueError))
def handle_participation_automatic_check_out(request_data, user):
    # Validate event exists
    # Validate event is active
    # Validate user is participant
    # Check if user is outside location, checks out user.
    latitude, longitude = space_utils.parse_coordinate(request_data)
    event = utils.get_event_by_id_or_raise_exception(request_data.get('event_id'))
    validate_event_is_on_going(event)

    participation = event.get_participation_by_participant(user)
    _validate_user_is_a_participant(participation)
    return _check_out_user_when_outside_event_location(
        event,
        participation,
        latitude,
        longitude
    )


