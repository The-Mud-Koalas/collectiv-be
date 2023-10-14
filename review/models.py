from django.db import models


class ParticipationReview(models.Model):
    participation = models.ForeignKey('event.EventParticipation', on_delete=models.CASCADE)
    event_rating = models.SmallIntegerField()
    event_comment = models.TextField(null=True)
    sentiment_score = models.FloatField(default=0)

    def get_rating(self):
        return self.event_rating

    def get_comment(self):
        return self.event_comment

    def set_sentiment_score(self, sentiment_score):
        self.sentiment_score = sentiment_score
        self.save()

    def get_sentiment_score(self):
        return self.sentiment_score

