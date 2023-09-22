from django.core.exceptions import ObjectDoesNotExist
from ..models import Event, EventCategory, Tags


def get_tag_by_id_or_raise_exception(tag_id):
    matching_tag = Tags.objects.filter(id=tag_id)

    if len(matching_tag) > 0:
        return matching_tag[0]
    else:
        raise ObjectDoesNotExist(f'Tag with id {tag_id} does not exist')


def get_event_by_id_or_raise_exception(event_id):
    matching_event = Event.objects.filter(id=event_id)

    if len(matching_event) > 0:
        return matching_event[0]
    else:
        raise ObjectDoesNotExist(f'Event with id {event_id} does not exist')


def convert_tag_names_to_tag(tag_names):
    return Tags.objects.filter(name__in=tag_names)


def get_tag_from_name(tag_name):
    matching_tag = Tags.objects.filter(name=tag_name)

    if len(matching_tag) > 0:
        return matching_tag[0]

    return None


def get_category_from_name(category_name):
    matching_category = EventCategory.objects.filter(name=category_name)

    if len(matching_category) > 0:
        return matching_category[0]

    return None
