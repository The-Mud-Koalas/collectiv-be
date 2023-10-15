from communalspace import utils as app_utils
from communalspace.exceptions import InvalidRequestException, RestrictedAccessException
from .forum_auth import check_authorization
from event.services import utils as event_utils


def _validate_post_range(request_data):
    if request_data.get("before") is not None and not app_utils.is_valid_iso_date_string(request_data.get("before")):
        raise InvalidRequestException("'before' is not a valid date string")
    if request_data.get("after") is not None and not app_utils.is_valid_iso_date_string(request_data.get("after")):
        raise InvalidRequestException("'after' is not a valid date string")
    if request_data.get("limit") is not None:
        try:
            int(request_data.get("limit"))
        except:
            raise InvalidRequestException("'limit' is not a valid integer")


def find_post_in_range(request_data, user, event_id):
    _validate_post_range(request_data)
    if not check_authorization(user, event_id):
        raise RestrictedAccessException('user is not part of event with id ' + event_id)

    request_limit = request_data.get("limit")
    limit = int(request_limit) if request_limit is not None else None
    request_after = request_data.get("after")
    after = app_utils.get_date_from_date_time_string(request_after) if request_after is not None else None
    request_before = request_data.get("before")
    before = app_utils.get_date_from_date_time_string(request_before) if request_before is not None else None

    event = event_utils.get_event_by_id_or_raise_exception(event_id)
    forum = event.get_or_create_forum()

    posts = forum.forumpost_set.all()
    if before:
        posts = posts.filter(posted_at__lt=before)
    if after:
        posts = posts.filter(posted_at__gt=after)
    if limit:
        posts = posts.order_by("-posted_at")[:limit]

    return posts
