from django.db import models
from rest_framework import serializers
import uuid


class Location(models.Model):
    id = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4)
    name = models.CharField(max_length=50)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def get_events_of_space(self):
        return self.event_set.all().order_by('name')


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

