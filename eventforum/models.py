from django.db import models
from event.models import Event


class ForumType(models.TextChoices):
    VOLUNTEER = 'volunteer', 'Volunteer'
    PARTICIPANT = 'participant', 'Participant'


class Forum(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=ForumType.choices)
