"""
1. Get list of past event (checked-out) participation--volunteer
2. Get list of ongoing event (check-in but not check-out) participation--volunteer
3. Get list of future events (not checked in but event status is still active) participation--volunteer
"""
from event.choices import ParticipationType, ParticipationStatus, EventStatus
from event.models import (
    EventParticipation,
    InitiativeParticipation,
    VolunteerParticipation,
    AttendableEventParticipation,
    ContributionParticipation,
    ProjectContribution
)


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


def handle_get_past_participations(request_data, user):
    user_past_participations = (EventParticipation.objects
                                .filter(participant=user)
                                .filter(check_out_time__isnull=False))
    return [
        user_past_participation
        for user_past_participation in user_past_participations
        if user_past_participation.get_participation_type() == request_data.get('type')
    ]


def handle_get_ongoing_participations(request_data, user):
    user_ongoing_participations = (EventParticipation.objects
                                   .filter(participant=user)
                                   .filter(check_in_time__isnull=False)
                                   .filter(check_out_time__isnull=True))

    return [
        user_ongoing_participation
        for user_ongoing_participation in user_ongoing_participations
        if user_ongoing_participation.get_participation_type() == request_data.get('type')
    ]


def handle_get_future_participations(request_data, user):
    user_future_participations = (EventParticipation.objects
                                  .filter(participant=user)
                                  .filter(check_in_time__isnull=True))

    return [
        user_future_participation
        for user_future_participation in user_future_participations
        if user_future_participation.get_participation_type() == request_data.get('type')
    ]


def handle_get_user_contribution(user):
    return ProjectContribution.objects.filter(contributor=user)
