"""
1. Get list of past event (checked-out) participation--volunteer
2. Get list of ongoing event (check-in but not check-out) participation--volunteer
3. Get list of future events (not checked in but event status is still active) participation--volunteer
"""
from event.models import EventParticipation, ProjectContribution


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






