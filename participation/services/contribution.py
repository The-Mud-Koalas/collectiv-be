from .attendance_helper import validate_event_is_on_going, validate_assisting_user_is_manager_of_event, handle_reward_grant
from communalspace.decorators import catch_exception_and_convert_to_invalid_request_decorator
from communalspace.exceptions import InvalidRequestException
from communalspace.firebase_admin import firebase as firebase_utils
from django.core.exceptions import ObjectDoesNotExist
from event.services import utils as event_utils
from event.choices import EventType
from users.services import utils as user_utils


def validate_event_is_project(event):
    if event.get_type() != EventType.PROJECT:
        raise InvalidRequestException(f'Event with id {event.get_id()} is not a project')


def validate_contributor_has_not_contributed(project, contributor):
    if project.get_contribution_by_contributor(contributor) is not None:
        raise InvalidRequestException('Contributor has contributed to the project')


def _validate_mark_participation_contribution_request(request_data):
    if not isinstance(request_data.get('amount_contributed'), int):
        raise InvalidRequestException('Amount contributed must be an integer')

    if request_data.get('amount_contributed') <= 0:
        raise InvalidRequestException('Amount contributed must be a positive integer')


def get_contribution_data(new_amount_contributed, contribution_participation):
    return {
        'amount_contributed': new_amount_contributed,
        'total_amount_contributed': contribution_participation.get_total_contribution()
    }


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_volunteer_mark_participant_contribution(request_data, volunteer_user):
    _validate_mark_participation_contribution_request(request_data)
    project = event_utils.get_project_by_id_or_raise_exception_thread_safe(request_data.get('event_id'))
    validate_event_is_on_going(project)
    validate_assisting_user_is_manager_of_event(project, volunteer_user)

    contributor_id = firebase_utils.get_user_id_from_email_or_phone_number(request_data.get('contributor_email_phone'))
    contributor = user_utils.get_user_by_id_or_raise_exception(contributor_id)

    contribution_participation = project.register_contribution(contributor, request_data.get('amount_contributed'))
    contribution_data = get_contribution_data(request_data.get('amount_contributed'), contribution_participation)
    return handle_reward_grant(contributor, contribution_data, contribution_participation)


