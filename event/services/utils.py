from django.core.exceptions import ObjectDoesNotExist
from ..models import Tags


def get_tag_by_id_or_raise_exception(tag_id):
    matching_tag = Tags.objects.filter(id=tag_id)

    if len(matching_tag) > 0:
        return matching_tag[0]
    else:
        raise ObjectDoesNotExist(f'Tag with id {tag_id} does not exist')
