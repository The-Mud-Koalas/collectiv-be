from event.services.create_event import _convert_tag_ids_to_tags
from communalspace import utils as app_utils
from communalspace.decorators import catch_exception_and_convert_to_invalid_request_decorator
from communalspace.exceptions import InvalidRequestException
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from numbers import Number
from space.services import utils as space_utils
from . import utils
from ..models import Event, Project


def _validate_update_event_request(request_data):
    if not isinstance(request_data.get('name'), str):
        raise InvalidRequestException('Event name must be a string')

    if not app_utils.text_length_is_valid(request_data.get('name').strip(), min_value=3, max_value=50):
        raise InvalidRequestException('Event name must be between 3 to 50 characters')

    if request_data.get('description') and not isinstance(request_data.get('description'), str):
        raise InvalidRequestException('Description must be a string')

    if not isinstance(request_data.get('is_project'), bool):
        raise InvalidRequestException('Is Project must be boolean')

    if request_data.get('is_project') and request_data.get('project_goal') is None:
        raise InvalidRequestException('Project Goal must exist in a project')

    if request_data.get('project_goal') is not None and not isinstance(request_data.get('project_goal'), Number):
        raise InvalidRequestException('Project Goal must be a number')

    if request_data.get('is_project') and not request_data.get('goal_measurement_unit'):
        raise InvalidRequestException('Goal measurement unit must exist in a project')

    if not isinstance(request_data.get('goal_measurement_unit'), str):
        raise InvalidRequestException('Goal measurement unit must be a string')

    if not isinstance(request_data.get('min_num_of_volunteers'), int):
        raise InvalidRequestException('Minimum number of volunteers must be an integer')

    if request_data.get('min_num_of_volunteers') < 0:
        raise InvalidRequestException('Minimum number of volunteers must be a non negative number')

    if not app_utils.is_valid_iso_date_string(request_data.get('start_date_time')):
        raise InvalidRequestException('Start date time must be a valid ISO datetime string')

    if not app_utils.is_valid_iso_date_string(request_data.get('end_date_time')):
        raise InvalidRequestException('End date time must be a valid ISO datetime string')

    if app_utils.get_date_from_date_time_string(request_data.get('start_date_time')) < datetime.utcnow():
        raise InvalidRequestException('Start time must not occur on a previous time')

    if (app_utils.get_date_from_date_time_string(request_data.get('start_date_time')) >=
            app_utils.get_date_from_date_time_string(request_data.get('end_date_time'))):
        raise InvalidRequestException('Start time must not occur after the end time')

    if not app_utils.is_valid_uuid_string(request_data.get('location_id')):
        raise InvalidRequestException('Location ID must be a valid UUID string')

    if not isinstance(request_data.get('tags'), list):
        raise InvalidRequestException('Tags must be a list')

    for tag_id in request_data.get('tags'):
        if not app_utils.is_valid_uuid_string(tag_id):
            raise InvalidRequestException('Tag ID must be a valid UUID string')


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
    _validate_update_event_request(request_data)

    event = utils.get_event_by_id_or_raise_exception(request_data.get('event_id'))
    event_space = space_utils.get_space_by_id_or_raise_exception(request_data.get('location_id'))
    event_tags = _convert_tag_ids_to_tags(request_data.get('tags'))

    if request_file:
        event.image = request_file

    return _update_event(event, request_data, event_space, event_tags, creator)
