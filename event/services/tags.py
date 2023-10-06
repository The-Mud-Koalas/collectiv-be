from communalspace.exceptions import InvalidRequestException
from . import utils
from ..models import Tags


def handle_get_all_tags():
    return Tags.objects.all()


def _validate_get_or_create_tags_request(request_data):
    if not isinstance(request_data.get('tags'), list):
        raise InvalidRequestException('Tags must be a list')

    for tag in request_data.get('tags'):
        if not isinstance(tag, str):
            raise InvalidRequestException('Tags must be a list of strings')


def _get_or_create_tags(tag_names):
    tags = []
    for tag_name in tag_names:
        tag_name = tag_name.strip().lower()
        matching_tag = utils.get_tag_from_name(tag_name)

        if matching_tag is None:
            matching_tag = Tags.objects.create(name=tag_name)

        tags.append(matching_tag)

    return tags


def handle_get_or_create_tags(request_data):
    _validate_get_or_create_tags_request(request_data)
    return _get_or_create_tags(request_data.get('tags'))

