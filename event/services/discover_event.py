from communalspace.decorators import catch_exception_and_convert_to_invalid_request_decorator
from communalspace.settings import GOOGLE_STORAGE_BUCKET_NAME
from communalspace.storage import google_storage
from django.core.exceptions import ObjectDoesNotExist
from .utils import get_event_by_id_or_raise_exception
import mimetypes


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_get_event_by_id(event_id):
    return get_event_by_id_or_raise_exception(event_id)


def handle_get_event_image_by_id(event_id):
    event = get_event_by_id_or_raise_exception(event_id)
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
