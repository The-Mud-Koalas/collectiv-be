from communalspace import utils as app_utils
from communalspace.decorators import catch_exception_and_convert_to_invalid_request_decorator
from communalspace.exceptions import InvalidRequestException, RestrictedAccessException
from django.core.exceptions import ObjectDoesNotExist
from review.services import sentiment
from forums.models import ForumPost
from event.services import utils as event_utils


def _validate_create_forum_post_request(request_data, author_id, event_id):
    if not isinstance(request_data.get('content'), str) or not request_data.get('content').strip():
        raise InvalidRequestException('Content must be a non-empty string.')

    if not app_utils.is_valid_uuid_string(event_id):  # check the forum_id from URL
        raise InvalidRequestException('Event ID must be a valid UUID string.')

    if not isinstance(request_data.get('is_anonymous', False), bool):
        raise InvalidRequestException('Is Anonymous must be boolean.')


def _create_forum_post(request_data, author, role, forum) -> ForumPost:
    forum_post_sentiment_score = sentiment.compute_sentiment_score_from_text(request_data.get('content'))
    return forum.create_post(
        content=request_data.get('content'),
        author=author,
        author_role=role,
        is_anonymous=request_data.get('is_anonymous', False),
        sentiment_score=forum_post_sentiment_score
    )


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_create_forum_post(request_data, author, event_id):
    _validate_create_forum_post_request(request_data, author, event_id)
    event = event_utils.get_event_by_id_or_raise_exception(event_id)
    is_creator = event.get_creator() == author
    participation = event.get_all_type_participation_by_participant(author)
    if participation is None and not is_creator:
        raise RestrictedAccessException('user is not part of event with id ' + event_id)
    if participation is not None and participation.get_has_left_forum():
        raise RestrictedAccessException('user has left forum of event with id ' + event_id)
    role = participation.get_participation_type() if not is_creator else "creator"
    forum = event.get_or_create_forum()
    return _create_forum_post(request_data, author, role, forum)
