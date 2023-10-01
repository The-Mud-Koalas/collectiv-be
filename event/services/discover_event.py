import space.services.haversine
from communalspace.decorators import catch_exception_and_convert_to_invalid_request_decorator
from communalspace.settings import GOOGLE_STORAGE_BUCKET_NAME
from communalspace.storage import google_storage
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timezone
from space.models import Location
from space.services import utils as space_utils
from typing import List
from users.models import User
from . import utils
from ..models import Event, Tags
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
    events_of_spaces = []
    for space in spaces:
        events_of_spaces.extend(space.get_active_events_of_space())

    return events_of_spaces


def _filter_events_matching_tags(events: List[Event], tags: List[Tags]):
    return [
        event
        for event in events
        if event.get_tags() & tags
    ]


def _get_events_matching_user_interest(events, user):
    user_interests = user.get_interests()
    return _filter_events_matching_tags(events, user_interests)


@catch_exception_and_convert_to_invalid_request_decorator((ValueError,))
def handle_get_interest_based_nearby_events(request_data, user: User):
    subscribed_locations = user.get_subscribed_locations()
    latitude, longitude = space_utils.parse_coordinate(request_data)
    nearby_spaces = space_utils.get_nearby_locations(
        subscribed_locations,
        latitude,
        longitude,
        user.get_preferred_radius()
    )
    nearby_events = _get_active_events_of_spaces(nearby_spaces)
    return _get_events_matching_user_interest(nearby_events, user)


def _get_events_based_on_location(latitude, longitude):
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
        events = (Event.objects.filter(end_date_time__gte=datetime.now(tz=timezone.utc)).order_by('start_date_time'))

    return events


@catch_exception_and_convert_to_invalid_request_decorator((ValueError,))
def handle_search_events(request_data):
    latitude, longitude = space_utils.parse_coordinate_fail_silently(request_data)
    events = _get_events_based_on_location(latitude, longitude)

    if request_data.get('name') is not None:
        events = events.filter(name__icontains=request_data.get('name'))

    if request_data.get('tags') is not None:
        tag_names = request_data.get('tags').split(',')
        tag_names = [tag_name.lower() for tag_name in tag_names]
        tags = utils.convert_tag_names_to_tag(tag_names)
        events = _filter_events_matching_tags(events, tags)

    return events






