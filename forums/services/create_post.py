from django.core.exceptions import ObjectDoesNotExist

from communalspace import utils as app_utils
from communalspace.decorators import catch_exception_and_convert_to_invalid_request_decorator
from communalspace.exceptions import InvalidRequestException
from users.models import User
from forums.models import Forum
from forums.models import ForumPost


def _validate_create_forum_post_request(request_data):
    if not isinstance(request_data.get('content'), str) or not request_data.get('content').strip():
        raise InvalidRequestException('Content must be a non-empty string.')

    author_id = request_data.get('author_id')
    if not isinstance(author_id, str) or len(author_id) > 30:
        raise InvalidRequestException('Author ID must be a valid string of max length 30.')

    if not app_utils.is_valid_uuid_string(request_data.get('forum_id')):
        raise InvalidRequestException('Forum ID must be a valid UUID string.')

    if not isinstance(request_data.get('is_anonymous', False), bool):
        raise InvalidRequestException('Is Anonymous must be boolean.')


def _create_forum_post(request_data, author, forum) -> ForumPost:
    post = ForumPost.objects.create(
        content=request_data.get('content'),
        author=author,
        forum=forum,
        is_anonymous=request_data.get('is_anonymous', False)
    )
    return post


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_create_forum_post(request_data, user):
    _validate_create_forum_post_request(request_data)
    request_data = app_utils.trim_all_request_attributes(request_data)

    author = User.objects.get(pk=request_data.get('author_id'))
    forum = Forum.objects.get(pk=request_data.get('forum_id'))

    created_post = _create_forum_post(request_data, author=author, forum=forum)
    return created_post
