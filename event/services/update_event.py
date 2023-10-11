from rest_framework.response import Response
from communalspace import utils as app_utils
from communalspace.decorators import catch_exception_and_convert_to_invalid_request_decorator
from django.core.exceptions import ObjectDoesNotExist
from space.services import utils as space_utils
from . import utils
from .utils import convert_tag_ids_to_tags
from ..models import Event, Project, Initiative
from .create_event import validate_create_event_request

def check_event_ownership(event, user):
    """
    Check if the user is the owner of the event

    :param event: event id
    :param user: user id
    :return: True if user is the owner of the event, False otherwise
    """
    event = Event.objects.get(id=event)
    print(event.creator)
    if event.creator != user:
        return False
    return True


def _update_event(event, request_data, event_space, event_tags, creator) -> Event:
    """
    Update event details

    :param event: event id
    :param request_data: request data
    :param event_space: event space
    :param event_tags: event tags
    :param creator: creator id
    :return: updated event
    """
    event.name = request_data.get('name', event.name)
    event.description = request_data.get('description', event.description)
    event.start_date_time = app_utils.get_date_from_date_time_string(
        request_data.get('start_date_time', event.start_date_time))
    event.end_date_time = app_utils.get_date_from_date_time_string(
        request_data.get('end_date_time', event.end_date_time))
    event.location = event_space if event_space else event.location
    event.creator = creator
    event.category = utils.get_category_from_id_or_raise_exception(request_data.get('category_id', event.category.id))
    event.volunteer_registration_enabled = request_data.get('volunteer_registration_enabled',
                                                            event.volunteer_registration_enabled)
    if isinstance(event, Project):
        event.goal_kind = utils.get_or_create_goal_kind(request_data.get('goal_kind', event.goal_kind.kind))
        event.goal = request_data.get('project_goal', event.goal)
        event.measurement_unit = request_data.get('goal_measurement_unit', event.measurement_unit)

    if isinstance(event, Initiative):
        event.participation_registration_enabled = request_data.get('participation_registration_enabled',
                                                                                event.initiative.participation_registration_enabled)
        print(request_data.get('participation_registration_enabled'))
    if event_tags:
        event.tags.clear()
        for tag in event_tags:
            event.add_tags(tag)

    event.save()
    return event


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_update_event(event_id, request_data, request_file, user) -> Response:
    """
    Update event details

    :param event_id: event id
    :param request_data: request data
    :param request_file: request file
    :param user: user id
    :return: updated event
    """
    if not check_event_ownership(event_id, user):
        return Response({'message': 'You are not the owner of this event'}, status=403)
    else:
        validate_create_event_request(request_data)
        event = utils.get_event_by_id_or_raise_exception(event_id)
        event_space = space_utils.get_space_by_id_or_raise_exception(request_data.get('location_id'))
        event_tags = convert_tag_ids_to_tags(request_data.get('tags'))

    if request_file:
        event.image = request_file

    return _update_event(event, request_data, event_space, event_tags, user)
