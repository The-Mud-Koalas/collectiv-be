from communalspace import utils as app_utils
from communalspace.decorators import catch_exception_and_convert_to_invalid_request_decorator
from django.core.exceptions import ObjectDoesNotExist
from space.services import utils as space_utils
from . import utils
from .utils import convert_tag_ids_to_tags
from ..models import Event, Project

from .create_event import validate_create_event_request



def _update_event(event, request_data, event_space, event_tags, creator) -> Event:
    event.name = request_data.get('name', event.name)
    event.description = request_data.get('description', event.description)
    event.min_num_of_volunteers = request_data.get('min_num_of_volunteers', event.min_num_of_volunteers)
    event.start_date_time = app_utils.get_date_from_date_time_string(
        request_data.get('start_date_time', event.start_date_time))
    event.end_date_time = app_utils.get_date_from_date_time_string(
        request_data.get('end_date_time', event.end_date_time))
    event.location = event_space if event_space else event.location
    event.creator = creator

    if isinstance(event, Project):
        event.goal = request_data.get('project_goal', event.goal)
        event.measurement_unit = request_data.get('goal_measurement_unit', event.measurement_unit)

    if event_tags:
        event.clear_tags()
        for tag in event_tags:
            event.add_tags(tag)

    event.save()
    return event


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_update_event(request_data, request_file, creator) -> Event:
    validate_create_event_request(request_data)

    event = utils.get_event_by_id_or_raise_exception(request_data.get('event_id'))
    event_space = space_utils.get_space_by_id_or_raise_exception(request_data.get('location_id'))
    event_tags = convert_tag_ids_to_tags(request_data.get('tags'))

    if request_file:
        event.image = request_file

    return _update_event(event, request_data, event_space, event_tags, creator)
