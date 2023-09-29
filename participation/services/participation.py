from communalspace.decorators import catch_exception_and_convert_to_invalid_request_decorator
from communalspace.exceptions import InvalidRequestException
from django.core.exceptions import ObjectDoesNotExist
from event.services import utils as event_utils


def validate_event_is_active(event):
    if not event.is_active():
        raise InvalidRequestException('Event is cancelled or has been completed')


def _validate_participation_registration(event, user):
    validate_event_is_active(event)
    user_event_participation = event.get_participation_by_participant(user)
    if user_event_participation is not None:
        raise InvalidRequestException(
            f'User has been registered as {user_event_participation.get_participation_type()} in the event'
        )


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_register_user_participation_to_event(request_data, user):
    event = event_utils.get_event_by_id_or_raise_exception(request_data.get('event_id'))
    _validate_participation_registration(event, user)
    event.add_participant(user)


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_register_user_volunteering_to_event(request_data, user):
    event = event_utils.get_event_by_id_or_raise_exception(request_data.get('event_id'))
    _validate_participation_registration(event, user)
    event.add_volunteer(user)

