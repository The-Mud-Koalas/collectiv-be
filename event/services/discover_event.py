from . import utils
from ..models import Event
from ..choices import EventType
from communalspace.decorators import catch_exception_and_convert_to_invalid_request_decorator
from communalspace.settings import GOOGLE_STORAGE_BUCKET_NAME
from communalspace.storage import google_storage
from django.core.exceptions import ObjectDoesNotExist
from space.models import Location
from space.services import utils as space_utils
from users.models import User

import space.services.haversine
import mimetypes


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_get_event_by_id(event_id):
    return utils.get_event_by_id_or_raise_exception(event_id)


def handle_get_event_image_by_id(event_id):
    event = utils.get_event_by_id_or_raise_exception(event_id)
    event_image_directory = event.get_event_image_directory()

    if event_image_directory:
        event_image_extension = mimetypes.guess_type(event_image_directory)[0]
        return google_storage.download_file_from_google_bucket(
            event_image_directory,
            GOOGLE_STORAGE_BUCKET_NAME,
            target_file_name=event_image_directory.split('/')[-1],
            content_type=event_image_extension
        )

    else:
        return None


def _get_active_events_of_spaces(spaces):
    events_of_spaces = Event.objects.none()
    for space_ in spaces:
        events_of_spaces = events_of_spaces | space_.get_active_events_of_space()

    return events_of_spaces


@catch_exception_and_convert_to_invalid_request_decorator((ValueError,))
def handle_get_interest_based_nearby_active_events(request_data, user: User):
    subscribed_locations = user.get_subscribed_locations()
    latitude, longitude = space_utils.parse_coordinate(request_data)
    nearby_spaces = space_utils.get_nearby_locations(
        subscribed_locations,
        latitude,
        longitude,
        user.get_preferred_radius()
    )
    nearby_events = _get_active_events_of_spaces(nearby_spaces)
    return nearby_events.filter(tags__in=user.get_interests())


def _get_active_events_based_on_coordinate(latitude, longitude):
    if latitude is not None and longitude is not None:
        all_locations = Location.objects.all()
        sorted_locations = sorted(
            all_locations,
            key=lambda l: space.services.haversine.haversine(
                latitude,
                longitude,
                l.latitude,
                l.longitude)
        )
        events = _get_active_events_of_spaces(sorted_locations)

    else:
        events = Event.objects.filter_active().order_by('start_date_time')

    return events


def _filter_events_based_on_search_parameter(events, search_parameter):
    if search_parameter.get('status') is not None:
        events = events.filter(status__iexact=search_parameter.get('status'))

    if search_parameter.get('category_id') is not None:
        events = events.filter(category__id=search_parameter.get('category_id'))

    if search_parameter.get('tags') is not None:
        tag_names = search_parameter.get('tags').split(',')
        events = events.filter(tags__name__in=tag_names)

    if search_parameter.get('type') is not None and search_parameter.get('type').lower() == EventType.INITIATIVE:
        events = utils.filter_initiatives(events)

    if search_parameter.get('type') is not None and search_parameter.get('type').lower() == EventType.PROJECT:
        events = utils.filter_initiatives(events)

    return events


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_get_events_per_location(location_id, request_data):
    location = space_utils.get_space_by_id_or_raise_exception(location_id)
    events_of_space = location.get_all_events_of_space()
    return _filter_events_based_on_search_parameter(events_of_space, request_data)


def handle_search_events_location_wide(request_data):
    latitude, longitude = space_utils.parse_coordinate_fail_silently(request_data)
    events = _get_active_events_based_on_coordinate(latitude, longitude)
    return _filter_events_based_on_search_parameter(events, request_data)


def handle_search_events(request_data):
    if request_data.get('location_id') is not None:
        return handle_get_events_per_location(request_data.get('location_id'), request_data)

    else:
        return handle_search_events_location_wide(request_data)







