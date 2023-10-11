from communalspace import utils as app_utils
from communalspace.decorators import catch_exception_and_convert_to_invalid_request_decorator
from communalspace.exceptions import InvalidRequestException, RestrictedAccessException
from communalspace.settings import GOOGLE_BUCKET_BASE_DIRECTORY, GOOGLE_STORAGE_BUCKET_NAME
from communalspace.storage import google_storage
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from google.api_core import exceptions as google_exceptions
from numbers import Number
from space.services import utils as space_utils
from . import utils
from ..models import Event, Project, Initiative


def _validate_event_basic_attributes(request_data):
    if not isinstance(request_data.get('name'), str):
        raise InvalidRequestException('Event name must be a string')

    if not app_utils.text_length_is_valid(request_data.get('name').strip(), min_value=3, max_value=50):
        raise InvalidRequestException('Event name must be between 3 to 50 characters')

    if request_data.get('description') and not isinstance(request_data.get('description'), str):
        raise InvalidRequestException('Description must be a string')

    if not isinstance(request_data.get('is_project'), bool):
        raise InvalidRequestException('Is Project must be boolean')


def _validate_event_updatable_attributes(request_data):
    if not app_utils.is_valid_iso_date_string(request_data.get('start_date_time')):
        raise InvalidRequestException('Start date time must be a valid ISO datetime string')

    if not app_utils.is_valid_iso_date_string(request_data.get('end_date_time')):
        raise InvalidRequestException('End date time must be a valid ISO datetime string')

    if app_utils.get_date_from_date_time_string(request_data.get('start_date_time')) < datetime.utcnow():
        raise InvalidRequestException('Start time must not occur on a previous time')

    if (app_utils.get_date_from_date_time_string(request_data.get('start_date_time')) >=
            app_utils.get_date_from_date_time_string(request_data.get('end_date_time'))):
        raise InvalidRequestException('Start time must not occur after the end time')

    if not isinstance(request_data.get('tags'), list):
        raise InvalidRequestException('Tags must be a list')

    for tag_id in request_data.get('tags'):
        if not app_utils.is_valid_uuid_string(tag_id):
            raise InvalidRequestException('Tag ID must be a valid UUID string')


def _validate_additional_project_attributes(request_data):
    if not request_data.get('project_goal'):
        raise InvalidRequestException('Project Goal must exist in a project')

    if not isinstance(request_data.get('project_goal'), Number):
        raise InvalidRequestException('Project Goal must be a number')

    if not request_data.get('goal_kind'):
        raise InvalidRequestException('Goal kind must exist in a project')

    if not isinstance(request_data.get('goal_kind'), str):
        raise InvalidRequestException('Goal kind must be a string')

    if not request_data.get('goal_measurement_unit'):
        raise InvalidRequestException('Goal measurement unit must exist in a project')

    if not isinstance(request_data.get('goal_measurement_unit'), str):
        raise InvalidRequestException('Goal measurement unit must be a string')


def validate_create_event_request(request_data):
    _validate_event_basic_attributes(request_data)
    _validate_event_updatable_attributes(request_data)

    if request_data.get('is_project'):
        _validate_additional_project_attributes(request_data)


def _create_project(request_data, event_category, event_space, creator):
    return Project.objects.create(
        name=request_data.get('name'),
        description=request_data.get('description'),
        start_date_time=app_utils.get_date_from_date_time_string(request_data.get('start_date_time')),
        end_date_time=app_utils.get_date_from_date_time_string(request_data.get('end_date_time')),
        location=event_space,
        creator=creator,
        category=event_category,
        goal=request_data.get('project_goal'),
        measurement_unit=request_data.get('goal_measurement_unit'),
        goal_kind=utils.get_or_create_goal_kind(request_data.get('goal_kind').lower())
    )


def _create_initiative(request_data, event_category, event_space, creator):
    return Initiative.objects.create(
        name=request_data.get('name'),
        description=request_data.get('description'),
        start_date_time=app_utils.get_date_from_date_time_string(request_data.get('start_date_time')),
        end_date_time=app_utils.get_date_from_date_time_string(request_data.get('end_date_time')),
        location=event_space,
        creator=creator,
        category=event_category,
    )


def _create_event(request_data, event_category, event_space, event_tags, creator) -> Event:
    event_is_project = request_data.get('is_project')
    if event_is_project:
        new_event = _create_project(
            request_data,
            event_category,
            event_space,
            creator
        )
    else:
        new_event = _create_initiative(
            request_data,
            event_category,
            event_space,
            creator
        )

    for tag in event_tags:
        new_event.add_tags(tag)

    return new_event


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_create_event(request_data, user):
    validate_create_event_request(request_data)
    request_data = app_utils.trim_all_request_attributes(request_data)
    event_category = utils.get_category_from_id_or_raise_exception(request_data.get('category_id'))
    event_space = space_utils.get_space_by_id_or_raise_exception(request_data.get('location_id'))
    event_tags = utils.convert_tag_ids_to_tags(request_data.get('tags'))
    created_event = _create_event(
        request_data,
        event_category=event_category,
        event_space=event_space,
        event_tags=event_tags,
        creator=user
    )

    return created_event


def _delete_event_image(event):
    try:
        google_storage.delete_file_from_google_bucket(event.get_event_image_directory(), GOOGLE_STORAGE_BUCKET_NAME)

    except google_exceptions.NotFound:
        pass


def _upload_event_image(event, image_file):
    if image_file:
        if event.get_event_image_directory() is not None:
            _delete_event_image(event)

        file_prefix = app_utils.get_prefix_from_file_name(image_file.name)
        image_file_name = f'{GOOGLE_BUCKET_BASE_DIRECTORY}/{event.get_id()}.{file_prefix}'
        google_storage.upload_file_to_google_bucket(image_file_name, GOOGLE_STORAGE_BUCKET_NAME, image_file)
        event.set_event_image(image_file_name)


def _validate_event_ownership(event, user):
    if event.get_creator() != user:
        raise RestrictedAccessException(f'User {user.get_name()} is not the creator of event {event.get_name()}')


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_upload_event_image(request_data, image_file, user):
    event = utils.get_event_by_id_or_raise_exception(request_data.get('event_id'))
    _validate_event_ownership(event, user)
    _upload_event_image(event, image_file)









