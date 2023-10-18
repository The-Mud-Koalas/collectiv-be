from . import utils
from users.models import User
from communalspace import utils as app_utils
from datetime import datetime
from django.db import models
from event.models import (
    Event,
    VolunteerParticipation,
    InitiativeParticipation,
    ContributionParticipation
)


def handle_get_user_wrap(user):
    previous_month = app_utils.get_previous_month_index(datetime.utcnow().month)

    last_month_created_events_count = Event.objects.filter(creator=user, start_date_time__month=previous_month).count()

    last_month_volunteer_count = VolunteerParticipation.objects.filter(
        participant=user,
        first_participation_time__month=previous_month,
    ).count()

    last_month_volunteering_duration = VolunteerParticipation.objects.filter(
        participant=user,
        first_participation_time__month=previous_month,
    ).aggregate(total_volunteering_duration=models.Sum('overall_duration_in_seconds'))

    last_month_initiative_count = InitiativeParticipation.objects.filter(
        participant=user,
        first_participation_time__month=previous_month,
    ).count()

    last_month_initiative_duration = InitiativeParticipation.objects.filter(
        participant=user,
        first_participation_time__month=previous_month
    ).aggregate(total_initiative_duration=models.Sum('overall_duration_in_seconds'))

    last_month_contributions = (ContributionParticipation.objects.filter(
        participant=user,
        first_participation_time__month=previous_month
    ).values(measurement_unit=models.F('event__measurement_unit'), goal_kind=models.F('event__goal_kind'))
     .order_by('measurement_unit', 'event__goal_kind')
     .annotate(total_contribution=models.Sum('total_contribution')))

    overall_rank = utils.compute_user_rank(user)

    return {
        'last_month_created_events_count': last_month_created_events_count,
        'last_month_volunteer_count': last_month_volunteer_count,
        'last_month_volunteering_duration': last_month_volunteering_duration,
        'last_month_initiative_count': last_month_initiative_count,
        'last_month_initiative_duration': last_month_initiative_duration,
        'last_month_contributions': last_month_contributions,
        'last_month_overall_rank': overall_rank,
        'total_users': User.objects.count(),
    }




