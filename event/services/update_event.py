from communalspace import utils as app_utils, utils
from event.models import Event, Project
from event.services.create_event import _convert_tag_ids_to_tags
from event.services.utils import get_event_by_id_or_raise_exception

def _update_event(event, request_data, event_space=None, event_tags=None) -> Event:
    event.name = request_data.get('name', event.name)
    event.description = request_data.get('description', event.description)
    event.min_num_of_volunteers = request_data.get('min_num_of_volunteers', event.min_num_of_volunteers)
    event.start_date_time = app_utils.get_date_from_date_time_string(
        request_data.get('start_date_time', event.start_date_time))
    event.end_date_time = app_utils.get_date_from_date_time_string(
        request_data.get('end_date_time', event.end_date_time))
    event.location = event_space if event_space else event.location

    if isinstance(event, Project):
        event.goal = request_data.get('project_goal', event.goal)
        event.measurement_unit = request_data.get('goal_measurement_unit', event.measurement_unit)

    if event_tags:
        event.clear_tags()
        for tag in event_tags:
            event.add_tags(tag)

    event.save()
    return event


def handle_update_event(request_data, request_file=None, user=None) -> Event:
    event = get_event_by_id_or_raise_exception(request_data.get('event_id'))
    event_space = utils.get_space_by_id_or_raise_exception(request_data.get('location_id'))
    event_tags = _convert_tag_ids_to_tags(request_data.get('tags'))
    updated_event = _update_event(event, request_data, event_space, event_tags)
    if request_file:
        updated_event.update_event_image(request_file)
    return updated_event