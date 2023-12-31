from communalspace.decorators import catch_exception_and_convert_to_invalid_request_decorator
from communalspace.exceptions import InvalidRequestException
from django.core.exceptions import ObjectDoesNotExist
from event.services import utils as event_utils
from participation.services.participation_helpers import (
    validate_event_is_initiative,
    validate_user_is_not_event_creator
)


def validate_event_is_active(event):
    if not event.is_active():
        raise InvalidRequestException('Event is cancelled or has been completed')


def _validate_initiative_is_accepting_participants(initiative):
    if not initiative.get_participation_registration_enabled():
        raise InvalidRequestException('Event is currently not accepting participants')


def _validate_event_is_accepting_volunteers(event):
    if not event.get_volunteer_registration_enabled():
        raise InvalidRequestException('Event is currently not accepting volunteers')


def _validate_user_is_a_participant_or_volunteer(participation):
    if participation is None:
        raise InvalidRequestException('User is not a participant or volunteer of event')


def _validate_participation_registration(event, participant):
    validate_event_is_active(event)
    user_event_participation = event.get_all_type_participation_by_participant(participant)

    if user_event_participation is not None:
        raise InvalidRequestException(
            f'User has been registered as {user_event_participation.get_participation_type()} in the event'
        )


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_register_user_participation_to_initiative(request_data, user):
    event = event_utils.get_initiative_by_id_or_raise_exception_thread_safe(request_data.get('event_id'))
    validate_user_is_not_event_creator(event, user)
    _validate_initiative_is_accepting_participants(event)
    _validate_participation_registration(event, user)
    event.add_participant(user)


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_register_user_volunteering_to_event(request_data, user):
    event = event_utils.get_event_by_id_or_raise_exception_thread_safe(request_data.get('event_id'))
    validate_user_is_not_event_creator(event, user)
    _validate_event_is_accepting_volunteers(event)
    _validate_participation_registration(event, user)
    event.add_volunteer(user)


def _delete_user_participation_from_event(participation):
    if participation.has_checked_in():
        participation.set_has_left_forum(True)

    else:
        participation.delete_participation()


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_participant_volunteer_leave_events(request_data, user):
    # TODO: FIX
    """
    1. Validate event exists
    2. Validate user participation
    3. If check in is null, delete participation object
    4. If check in is not null, set leave forum
    """
    event = event_utils.get_event_by_id_or_raise_exception_thread_safe(request_data.get('event_id'))
    participation = event.get_participation_by_participant(user)

    _validate_user_is_a_participant_or_volunteer(participation)
    _delete_user_participation_from_event(participation)


