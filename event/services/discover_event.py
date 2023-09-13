from communalspace.decorators import catch_exception_and_convert_to_invalid_request_decorator
from communalspace.settings import GOOGLE_STORAGE_BUCKET_NAME
from communalspace.storage import google_storage
from django.core.exceptions import ObjectDoesNotExist
from space.services import utils as space_utils
from users.models import User
from . import utils
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


def _get_events_of_spaces(spaces):
    events_of_spaces = []
    for space in spaces:
        events_of_spaces.extend(space.get_events_of_space())

    return events_of_spaces


def _get_events_matching_user_interest(events, user):
    user_interests = user.get_interests()

    matching_events = []
    for event in events:
        event_tags = event.get_tags()
        if event_tags & user_interests:
            matching_events.append(event)

    return matching_events


@catch_exception_and_convert_to_invalid_request_decorator((ValueError,))
def handle_get_interest_based_nearby_events(request_data, user: User):
    subscribed_locations = user.get_subscribed_locations()
    latitude, longitude = space_utils.parse_lat_long(request_data)
    nearby_spaces = space_utils.get_nearby_locations(
        subscribed_locations,
        latitude,
        longitude,
        user.get_preferred_radius()
    )
    nearby_events = _get_events_of_spaces(nearby_spaces)
    return _get_events_matching_user_interest(nearby_events, user)
