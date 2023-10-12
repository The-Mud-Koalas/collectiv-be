from .attendance_helper import (
    validate_event_is_on_going,
    validate_user_is_a_volunteer,
    validate_user_can_check_in,
    validate_assisting_user_is_manager_of_event,
    validate_user_is_attending_event,
    check_in_user,
    check_out_user,
)
from communalspace.decorators import catch_exception_and_convert_to_invalid_request_decorator
from communalspace.firebase_admin import firebase as firebase_utils
from django.core.exceptions import ObjectDoesNotExist
from event.choices import ParticipationType
from event.exceptions import InvalidCheckInCheckOutException
from event.services import utils as event_utils
from users.services import utils as user_utils


def _validate_user_is_a_volunteer(participation):
    if participation is None or participation.get_participation_type() != ParticipationType.VOLUNTEER:
        raise InvalidCheckInCheckOutException('User is not a volunteer of event')


@catch_exception_and_convert_to_invalid_request_decorator((
        ObjectDoesNotExist,
        InvalidCheckInCheckOutException,
        ValueError))
def handle_volunteer_assisted_check_in(request_data, assisting_user):
    event = event_utils.get_event_by_id_or_raise_exception(request_data.get('event_id'))
    validate_event_is_on_going(event)
    validate_assisting_user_is_manager_of_event(event, assisting_user)

    checking_in_user_id = firebase_utils.get_user_id_from_email_or_phone_number(
        request_data.get('volunteer_email_phone')
    )

    checking_in_user = user_utils.get_user_by_id_or_raise_exception(checking_in_user_id)

    volunteer_participation = event.get_volunteer_participation_by_participant(checking_in_user)
    _validate_user_is_a_volunteer(volunteer_participation)
    validate_user_can_check_in(checking_in_user, volunteer_participation)
    return check_in_user(checking_in_user, event, volunteer_participation)


@catch_exception_and_convert_to_invalid_request_decorator((
        ObjectDoesNotExist,
        InvalidCheckInCheckOutException,
        ValueError))
def handle_volunteer_self_check_out(request_data, user):
    event = event_utils.get_event_by_id_or_raise_exception(request_data.get('event_id'))
    volunteer_participation = event.get_volunteer_participation_by_participant(user)

    validate_user_is_a_volunteer(volunteer_participation)
    validate_user_is_attending_event(volunteer_participation)

    return check_out_user(user, volunteer_participation)


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_volunteer_grant_managerial_role(request_data, manager_user):
    event = event_utils.get_event_by_id_or_raise_exception(request_data.get('event_id'))
    validate_event_is_on_going(event)
    validate_assisting_user_is_manager_of_event(event, manager_user)

    volunteer_user_id = firebase_utils.get_user_id_from_email_or_phone_number(request_data.get('volunteer_email_phone'))
    granted_user = user_utils.get_user_by_id_or_raise_exception(volunteer_user_id)
    volunteer_participation = event.get_volunteer_participation_by_participant(granted_user)

    validate_user_is_a_volunteer(volunteer_participation)
    validate_user_is_attending_event(volunteer_participation)

    volunteer_participation.set_as_manager()



