# DELEGATION FUNCTION TO MARK CHECK IN OF VOLUNTEER AND PARTICIPANT
# CHECK IN VOLUNTEER using delegation mechanism
from .participation_attendance import validate_event_is_on_going
from communalspace.decorators import catch_exception_and_convert_to_invalid_request_decorator
from communalspace.exceptions import RestrictedAccessException, InvalidRequestException
from communalspace.firebase_admin import firebase as firebase_utils
from django.core.exceptions import ObjectDoesNotExist
from event.services import utils as event_utils
from users.services import utils as user_utils


def validate_assisting_user_is_manager_of_event(event, assisting_user):
    if not event.check_user_is_granted_manager_access(assisting_user):
        raise RestrictedAccessException('Assisting user has not been granted manager access')


def _validate_user_is_a_volunteer(participation):
    if participation is None or participation.get_participation_type() != 'volunteer':
        raise InvalidRequestException('User is not a volunteer of event')


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_volunteer_assisted_check_in(request_data, assisting_user):
    """
    1. Validate event exists and active
    2. Validate assisting user is a manager
    3. Validate user exists
    4. Validate user is volunteer of event
    5. Check in user
    """
    event = event_utils.get_event_by_id_or_raise_exception(request_data.get('event_id'))
    validate_event_is_on_going(event)
    validate_assisting_user_is_manager_of_event(event, assisting_user)

    checking_in_user_id = firebase_utils.get_user_id_from_email_or_phone_number(
        request_data.get('volunteer_email_phone')
    )

    checking_in_user = user_utils.get_user_by_id_or_raise_exception(checking_in_user_id)
    participation = event.get_participation_by_participant(checking_in_user)
    _validate_user_is_a_volunteer(participation)

    participation.check_in()


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_volunteer_self_check_out(request_data, user):
    """
    1. Validate event exists and active
    2. Validate user is a volunteer of event
    3. Check out user
    """
    event = event_utils.get_event_by_id_or_raise_exception(request_data.get('event_id'))
    validate_event_is_on_going(event)

    participation = event.get_participation_by_participant(user)
    _validate_user_is_a_volunteer(participation)

    participation.check_out()


def handle_volunteer_grant_managerial_role(request_data, manager_user):
    """
    1. Validate event exists
    2. Validate user is a manager of event
    3. Get volunteer from user id
    4. Validate volunteer already checks in
    5. Grant access to user as manager
    """
    event = event_utils.get_event_by_id_or_raise_exception(request_data.get('event_id'))
    validate_event_is_on_going(event)
    validate_assisting_user_is_manager_of_event(event, manager_user)

    volunteer_user_id = firebase_utils.get_user_id_from_email_or_phone_number(request_data.get('volunteer_email_phone'))
    granted_user = user_utils.get_user_by_id_or_raise_exception(volunteer_user_id)
    participation = event.get_participation_by_participant(granted_user)
    _validate_user_is_a_volunteer(participation)

    participation.set_as_manager()



