# TODO: FIX CONTRIBUTION
from .participation_attendance import validate_event_is_on_going
from .volunteer_attendance import validate_assisting_user_is_manager_of_event
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


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_volunteer_mark_participant_contribution(request_data, volunteer_user):
    """
    1. Validate event exists and is a project.
    2. Validate event is on going
    3. Validate volunteer user is a manager of event
    4. Validate user exists
    5. Mark contribution
    """
    project = event_utils.get_event_by_id_or_raise_exception(request_data.get('project_id'))
    validate_event_is_on_going(project)
    validate_event_is_project(project)
    validate_assisting_user_is_manager_of_event(project, volunteer_user)

    contributor_user_id = firebase_utils.get_user_id_from_email_or_phone_number(
        request_data.get('contributor_email_phone')
    )
    contributor = user_utils.get_user_by_id_or_raise_exception(contributor_user_id)
    project.add_contributor(contributor)


