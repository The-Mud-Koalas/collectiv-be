from communalspace.decorators import catch_exception_and_convert_to_invalid_request_decorator
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from event.choices import EventType
from event.models import EventSerializer, Event, Project, Initiative
from event.services import utils as event_utils
from space.services import utils as space_utils


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_get_complete_event_analytics(event_id):
    event = event_utils.get_event_by_id_or_raise_exception(event_id)
    event_data = EventSerializer(event).data
    if event.get_type() == EventType.INITIATIVE:
        event_data['registration_history'] = [
            {**day_data, 'registration_date': day_data['registration_date']}
            for day_data
            in event.get_event_registration_per_day()
        ]

    return event_data


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_get_total_participants_of_events_in_location(location_id):
    location = space_utils.get_space_by_id_or_raise_exception(location_id)

    events_in_location = Event.objects.filter(location=location)
    initiatives_in_location = Initiative.objects.filter(location=location)
    projects_in_location = Project.objects.filter(location=location)

    volunteers_count_in_location = (events_in_location
                                    .aggregate(total=models.Sum('current_num_of_volunteers'))
                                    .get('total'))

    participants_in_location = (initiatives_in_location
                                .aggregate(total=models.Sum('current_num_of_participants'))
                                .get('total'))

    contributors_in_location = (projects_in_location
                                .aggregate(total=models.Sum('current_num_of_participants'))
                                .get('total'))

    return {
        'location_id': location_id,
        'participation_data': {
            'volunteers_count_in_location': volunteers_count_in_location,
            'participants_in_location': participants_in_location,
            'contributors_in_location': contributors_in_location,
        }
    }


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_get_progresses_of_projects_in_location(location_id):
    location = space_utils.get_space_by_id_or_raise_exception(location_id)
    projects_in_location = Project.objects.filter(location=location)

    return {
        'location_id': location_id,
        'contribution_data': (projects_in_location.values('measurement_unit', 'goal_kind')
                              .order_by('measurement_unit', 'goal_kind')
                              .annotate(total_contribution=models.Sum('progress')))
    }


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_get_ratings_of_all_events_in_location(location_id):
    location = space_utils.get_space_by_id_or_raise_exception(location_id)
    events_in_location = Event.objects.filter(location=location)

    return {
        'location_id': location_id,
        'average_rating': (events_in_location.filter(~models.Q(average_event_rating=0))
                           .aggregate(average_rating=models.Avg('average_event_rating'))
                           .get('average_rating'))
    }


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_get_sentiment_of_all_events_in_location(location_id):
    location = space_utils.get_space_by_id_or_raise_exception(location_id)
    events_in_location = Event.objects.filter(location=location)

    return {
        'location_id': location_id,
        'average_sentiment_score': (events_in_location.filter(~models.Q(average_event_rating=0))
                                    .aggregate(average_sentiment_score=models.Avg('average_sentiment_score'))
                                    .get('average_sentiment_score'))
    }


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_get_location_event_count(location_id):
    location = space_utils.get_space_by_id_or_raise_exception(location_id)
    num_of_initiatives_in_location = Initiative.objects.filter(location=location).count()
    num_of_projects_in_location = Project.objects.filter(location=location).count()

    return {
        'location_id': location_id,
        'event_count_data': {
            'num_of_events_in_location': num_of_initiatives_in_location + num_of_projects_in_location,
            'num_of_initiatives_in_location': num_of_initiatives_in_location,
            'num_of_projects_in_location': num_of_projects_in_location,
        }
    }
