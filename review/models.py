from django.db import models


class ParticipationReview(models.Model):
    participation = models.ForeignKey('event.EventParticipation', on_delete=models.CASCADE)
    event_rating = models.SmallIntegerField()
    event_comment = models.TextField(null=True)

