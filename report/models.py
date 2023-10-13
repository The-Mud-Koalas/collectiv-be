from django.db import models
from rest_framework import serializers

class EventReport(models.Model):
    event = models.ForeignKey('event.Event', on_delete=models.CASCADE)
    reporter = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    remarks = models.TextField()


class EventReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventReport
        fields = '__all__'
