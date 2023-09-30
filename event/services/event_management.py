from . import utils
from ..models import EventStatus
from communalspace.decorators import catch_exception_and_convert_to_invalid_request_decorator
from communalspace.exceptions import InvalidRequestException, RestrictedAccessException
from django.core.exceptions import ObjectDoesNotExist


def _validate_event_ownership(event, user):
    if event.get_creator() != user:
        raise RestrictedAccessException(f'User {user.get_user_id()} is not the owner of event {event.get_id()}')


def _validate_update_status_transition(event, new_status):
    if event.get_status() == EventStatus.SCHEDULED.value and \
            new_status not in (EventStatus.ON_GOING.value, EventStatus.CANCELLED.value):
        raise InvalidRequestException('Scheduled events can only be updated to On Going or Cancelled')

    if event.get_status() == EventStatus.ON_GOING.value and new_status != EventStatus.COMPLETED.value:
        raise InvalidRequestException('On Going events can only be updated to Completed')

    if event.get_status() == EventStatus.COMPLETED.value:
        raise InvalidRequestException('Completed event can no longer be updated')


def _handle_send_cancellation_notification(event):
    pass


def update_event_status(event, new_status):
    """
    Update event status.
    If new status is cancelled, email user
    """
    event.set_status(new_status)

    if new_status == EventStatus.CANCELLED.value:
        _handle_send_cancellation_notification(event)


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_update_event_status(request_data, user):
    event = utils.get_event_by_id_or_raise_exception(request_data.get('event_id'))
    _validate_event_ownership(event, user)
    _validate_update_status_transition(event, request_data.get('new_status'))


