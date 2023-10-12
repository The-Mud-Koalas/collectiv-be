from . import utils, cancellation_email
from ..choices import EventStatus, TransactionType
from communalspace.decorators import catch_exception_and_convert_to_invalid_request_decorator
from communalspace.exceptions import InvalidRequestException, RestrictedAccessException
from communalspace.firebase_admin import firebase as firebase_utils
from communalspace.utils import convert_user_id_to_email_or_phone_number
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from participation.services.contribution import validate_event_is_project
import numbers


def validate_event_ownership(event, user):
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

    if event.get_status() == EventStatus.CANCELLED.value:
        raise InvalidRequestException('Cancelled event can no longer be updated')


def _handle_send_cancellation_notification(event):
    """
    This function is responsible for sending the cancellation notification
    to the volunteers and participants registered to the event.
    """
    event_participants_id_name_pair = event.get_all_type_participants_user_id_name_pair()
    event_participants_user_data_with_email = firebase_utils.embed_emails_to_user_data(event_participants_id_name_pair)
    event_participants_user_data_with_email = [
        user_data
        for user_data in event_participants_user_data_with_email
        if user_data.get('email') is not None
    ]
    cancellation_email.send_cancellation_email(event, event_participants_user_data_with_email)


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
    validate_event_ownership(event, user)
    _validate_update_status_transition(event, request_data.get('new_status'))
    update_event_status(event, request_data.get('new_status'))


def _validate_update_project_progress_request(request_data):
    if request_data.get('type') not in ('increase', 'decrease'):
        raise InvalidRequestException('Update type must be increase/decrease')

    if not isinstance(request_data.get('amount_to_update'), numbers.Number):
        raise InvalidRequestException('Amount to update must be a number')

    if request_data.get('amount_to_update') <= 0:
        raise InvalidRequestException('Amount to update must be greater than 0')


def _update_project_progress(event, amount_to_update, update_type):
    if update_type == TransactionType.INCREASE:
        event.increase_progress(amount_to_update)

    else:
        event.decrease_progress(amount_to_update)


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist, ValueError))
def handle_update_project_progress(request_data, user):
    event = utils.get_event_by_id_or_raise_exception_thread_safe(request_data.get('event_id'))
    validate_event_is_project(event)
    validate_event_ownership(event, user)
    _validate_update_project_progress_request(request_data)
    _update_project_progress(
        event,
        request_data.get('amount_to_update'),
        request_data.get('type')
    )


def _validate_user_is_manager_of_event(event, user):
    if not event.check_user_can_act_as_manager(user):
        raise RestrictedAccessException(
            'User has not been granted manager access or is currently not checked in'
        )


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_get_event_volunteers(request_data, user):
    event = utils.get_event_by_id_or_raise_exception(request_data.get('event_id'))
    _validate_user_is_manager_of_event(event, user)
    volunteers = (event.get_all_volunteers()
                  .annotate(
                        user_id=models.F('participant'),
                        volunteer_name=models.F('participant__full_name'),
                        has_manager_access=models.F('granted_manager_access'))
                  .values('user_id', 'volunteer_name', 'has_manager_access'))

    return convert_user_id_to_email_or_phone_number(volunteers)

