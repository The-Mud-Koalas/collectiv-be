"""
1. Get list of past event (checked-out) participation--volunteer
2. Get list of ongoing event (check-in but not check-out) participation--volunteer
3. Get list of future events (not checked in but event status is still active) participation--volunteer
"""
from communalspace.decorators import catch_exception_and_convert_to_invalid_request_decorator
from django.core.exceptions import ObjectDoesNotExist
from event.choices import ParticipationType, ParticipationStatus, EventStatus
from event.models import (
    Event,
    InitiativeParticipation,
    VolunteerParticipation,
    AttendableEventParticipation,
    ContributionParticipation,
)
from event.services import utils as event_utils


def _get_attendable_user_participations_by_type(user, participation_type):
    if participation_type == ParticipationType.PARTICIPANT:
        return InitiativeParticipation.objects.filter(participant=user)
    elif participation_type == ParticipationType.VOLUNTEER:
        return VolunteerParticipation.objects.filter(participant=user)
    else:
        return AttendableEventParticipation.objects.filter(participant=user)


def _get_event_status_selector_from_participation_status(participation_status):
    if participation_status == ParticipationStatus.PAST:
        return [EventStatus.COMPLETED.value, EventStatus.CANCELLED.value]

    elif participation_status == ParticipationStatus.ON_GOING:
        return [EventStatus.ON_GOING.value]

    elif participation_status == ParticipationStatus.FUTURE:
        return [EventStatus.SCHEDULED.value]

    else:
        return EventStatus.values


def _filter_user_participations_by_status(attendable_participations, participation_status):
    matching_participations = []
    desired_event_status = _get_event_status_selector_from_participation_status(participation_status)
    for attendable_participation in attendable_participations:
        event_of_participation = attendable_participation.get_event()

        if event_of_participation.get_status() in desired_event_status:
            matching_participations.append(attendable_participation)

    return matching_participations


def handle_get_user_participations(request_data, user):
    attendable_user_participations = (_get_attendable_user_participations_by_type(user, request_data.get('type'))
                                      .order_by('-registration_time'))
    return _filter_user_participations_by_status(attendable_user_participations, request_data.get('status'))


def handle_get_user_contributions(user):
    return (ContributionParticipation.objects.filter(participant=user)
            .order_by('-registration_time'))


def handle_get_created_events(request_data, user):
    desired_event_status = _get_event_status_selector_from_participation_status(request_data.get('status'))
    return Event.objects.filter(creator=user, status__in=desired_event_status)


@catch_exception_and_convert_to_invalid_request_decorator((ObjectDoesNotExist,))
def handle_check_user_registration_to_event(request_data, user):
    event = event_utils.get_event_by_id_or_raise_exception(request_data.get('event_id'))
    return event.get_all_type_participation_by_participant(user)




