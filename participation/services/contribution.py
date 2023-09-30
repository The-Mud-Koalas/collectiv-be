from .participation_attendance import validate_event_is_on_going
from .volunteer_attendance import validate_assisting_user_is_manager_of_event
from communalspace.decorators import catch_exception_and_convert_to_invalid_request_decorator
from communalspace.exceptions import InvalidRequestException
from django.core.exceptions import ObjectDoesNotExist
from event.services import utils as event_utils
from users.services import utils as user_utils


def _validate_event_is_project(event):
    if event.get_type() != 'project':
        raise InvalidRequestException(f'Event with id {event.get_id()} is not a project')


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
    _validate_event_is_project(project)
    validate_assisting_user_is_manager_of_event(project, volunteer_user)

    contributor = user_utils.get_user_by_id_or_raise_exception(request_data.get('contributor_user_id'))
    project.add_contributor(contributor)


