from django.db import models


class ParticipationVolunteeringReview(models.Model):
    participation = models.ForeignKey('event.EventParticipation', on_delete=models.CASCADE)
    event_rating = models.SmallIntegerField()
    event_comment = models.TextField(null=True)


class ContributionReview(models.Model):
    contribution = models.ForeignKey('event.ProjectContribution', on_delete=models.CASCADE)
    event_rating = models.SmallIntegerField()
    event_comment = models.TextField(null=True)
