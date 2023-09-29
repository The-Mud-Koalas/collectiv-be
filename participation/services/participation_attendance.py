from .participation import validate_event_is_active
from event.services import utils
from event.exceptions import InvalidCheckInCheckOutException
from communalspace.decorators import catch_exception_and_convert_to_invalid_request_decorator
from communalspace.exceptions import InvalidRequestException
from django.core.exceptions import ObjectDoesNotExist
from space.services import utils as space_utils


def _validate_user_is_a_participant(participation):
    if participation is None or participation.get_participation_type() != 'participant':
        raise InvalidRequestException('User is not a participant of event')


def _validate_user_is_inside_event_location(event, user_latitude, user_longitude):
    if not event.check_user_is_inside_event(user_latitude, user_longitude):
        raise InvalidRequestException(f'User is currently not inside event location')


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist, ValueError))
def handle_participation_self_check_in_confirmation(request_data, user):
    # Validate event exists
    # Validate event is active
    # Validate user is participant
    # Validate user is inside location
    # Check in user
    latitude, longitude = space_utils.parse_coordinate(request_data)
    event = utils.get_event_by_id_or_raise_exception(request_data.get('event_id'))
    validate_event_is_active(event)
    _validate_user_is_inside_event_location(event, latitude, longitude)

    participation = event.get_participation_by_participant(user)
    _validate_user_is_a_participant(participation)

    participation.check_in()


@catch_exception_and_convert_to_invalid_request_decorator((
        ObjectDoesNotExist,
        InvalidCheckInCheckOutException,
        ValueError))
def handle_participation_self_check_out_confirmation(request_data, user):
    # Validate event exists
    # Validate event is active
    # Validate user is participant
    # Validate user is inside location
    # Check out user
    latitude, longitude = space_utils.parse_coordinate(request_data)
    event = utils.get_event_by_id_or_raise_exception(request_data.get('event_id'))
    validate_event_is_active(event)
    _validate_user_is_inside_event_location(event, latitude, longitude)

    participation = event.get_participation_by_participant(user)
    _validate_user_is_a_participant(participation)

    participation.check_out()


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
    validate_event_is_active(event)

    participation = event.get_participation_by_participant(user)
    _validate_user_is_a_participant(participation)
    return _check_out_user_when_outside_event_location(
        event,
        participation,
        latitude,
        longitude
    )


