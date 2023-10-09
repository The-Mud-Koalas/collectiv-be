from . import utils
from ..choices import EventStatus, TransactionType
from communalspace.decorators import catch_exception_and_convert_to_invalid_request_decorator
from communalspace.exceptions import InvalidRequestException, RestrictedAccessException
from django.core.exceptions import ObjectDoesNotExist
from participation.services.contribution import validate_event_is_project
import numbers


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
    """
    This function is responsible for sending the cancellation notification
    to the volunteers and participants registered to the event.
    """
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
    event = utils.get_event_by_id_or_raise_exception_thread_safe(request_data.get('event_id'))
    _validate_event_ownership(event, user)
    _validate_update_status_transition(event, request_data.get('new_status'))
    update_event_status(event, request_data.get('new_status'))


def _validate_update_project_progress_request(request_data):
    if not isinstance(request_data.get('amount_to_update'), numbers.Number):
        raise InvalidRequestException('Amount to update must be a number')

    if request_data.get('amount_to_update') <= 0:
        raise InvalidRequestException('Amount to update must be greater than 0')


def _update_project_progress(event, amount_to_update, update_type):
    if update_type == TransactionType.INCREASE:
        event.increase_progress(amount_to_update)

    else:
        event.decrease_progress(amount_to_update)


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_update_project_progress(request_data, user):
    _validate_update_project_progress_request(request_data)
    project = utils.get_project_by_id_or_raise_exception_thread_safe(request_data.get('event_id'))
    _validate_event_ownership(project, user)
    project.register_contribution(user, request_data.get('amount_to_update'))
    return {
        'progress': project.get_progress()
    }
