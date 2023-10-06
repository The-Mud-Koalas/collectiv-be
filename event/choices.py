from django.db import models


class EventStatus(models.TextChoices):
    SCHEDULED = 'Scheduled'
    ON_GOING = 'On Going'
    COMPLETED = 'Completed'
    CANCELLED = 'Cancelled'
