from django.core.exceptions import ObjectDoesNotExist
from ..models import Tags, Event


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


def parse_lat_long(lat_long_data):
    try:
        return [
            float(lat_long_data.get('latitude')),
            float(lat_long_data.get('longitude'))
        ]

    except (ValueError, TypeError):
        raise ValueError('Latitude and Longitude must be a valid floating point number')


