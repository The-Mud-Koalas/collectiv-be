from django.db import models


class EventStatus(models.TextChoices):
    SCHEDULED = 'Scheduled'
    ON_GOING = 'On Going'
    COMPLETED = 'Completed'
    CANCELLED = 'Cancelled'


class AttendanceActivityType(models.TextChoices):
    CHECK_IN = 'check-in'
    CHECK_OUT = 'check-out'


class EventType:
    INITIATIVE = 'initiative'
    PROJECT = 'project'


class TransactionType:
    INCREASE = 'increase'
    DECREASE = 'decrease'


class ParticipationType:
    PARTICIPANT = 'participant'
    VOLUNTEER = 'volunteer'
    CONTRIBUTOR = 'contributor'


class ParticipationStatus:
    PAST = 'past'
    ON_GOING = 'on going'
    FUTURE = 'future'
