from . import utils
from .utils import convert_tag_ids_to_tags
from ..models import Event, Project, Initiative
from ..choices import EventType
from .create_event import (
    validate_event_time_range,
    validate_event_ownership,
    validate_event_updatable_attributes,
    validate_additional_project_attributes,
    validate_additional_initiative_attributes,
)
from rest_framework.response import Response
from communalspace import utils as app_utils
from communalspace.decorators import catch_exception_and_convert_to_invalid_request_decorator
from django.core.exceptions import ObjectDoesNotExist
from space.services import utils as space_utils


def check_event_ownership(event, user):
    """
    Check if the user is the owner of the event

    :param event: event id
    :param user: user id
    :return: True if user is the owner of the event, False otherwise
    """
    event = Event.objects.get(id=event)
    return event.creator == user


def _update_event(event, request_data, event_tags) -> Event:
    """
    Update event details

    :param event: event id
    :param request_data: request data
    :param event_space: event space
    :param event_tags: event tags
    :param creator: creator id
    :return: updated event
    """
    event.start_date_time = app_utils.get_date_from_date_time_string(request_data.get('start_date_time', event.start_date_time))
    event.end_date_time = app_utils.get_date_from_date_time_string(request_data.get('end_date_time', event.end_date_time))
    event.category = utils.get_category_from_id_or_raise_exception(request_data.get('category_id', event.category.id))
    event.volunteer_registration_enabled = request_data.get('volunteer_registration_enabled', event.volunteer_registration_enabled)

    if isinstance(event, Project):
        event.goal_kind = utils.get_or_create_goal_kind(request_data.get('goal_kind', event.goal_kind.kind))
        event.goal = request_data.get('project_goal', event.goal)
        event.measurement_unit = request_data.get('goal_measurement_unit', event.measurement_unit)

    if isinstance(event, Initiative):
        event.participation_registration_enabled = request_data.get('participation_registration_enabled', event.initiative.participation_registration_enabled)

    if event_tags:
        event.tags.clear()
        for tag in event_tags:
            event.add_tags(tag)

    event.save()
    return event


def _validate_update_event_request(event, request_data):
    validate_event_updatable_attributes(request_data)
    start_time = app_utils.get_date_from_date_time_string(request_data.get('start_date_time'))
    end_time = app_utils.get_date_from_date_time_string(request_data.get('end_date_time'))

    if start_time == event.get_start_date_time():
        validate_event_time_range(start_time, end_time, check_future=False)
    else:
        validate_event_time_range(start_time, end_time, check_future=True)

    if event.get_type() == EventType.PROJECT:
        validate_additional_project_attributes(request_data)
    else:
        validate_additional_initiative_attributes(request_data)


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_update_event(event_id, request_data, user) -> Response:
    """
    Update event details

    :param event_id: event id
    :param request_data: request data
    :param user: user id
    :return: updated event
    """
    event = utils.get_event_by_id_or_raise_exception_thread_safe(event_id)
    validate_event_ownership(event, user)
    _validate_update_event_request(event, request_data)
    event_tags = convert_tag_ids_to_tags(request_data.get('tags'))
    return _update_event(event, request_data, event_tags)
