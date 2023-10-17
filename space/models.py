from communalspace.settings import AREA_RADIUS, AREA_BUFFER_RADIUS
from django.db import models
from rest_framework import serializers
from space.services.haversine import haversine
import uuid


class Location(models.Model):
    id = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4)
    name = models.CharField(max_length=50)
    latitude = models.FloatField()
    longitude = models.FloatField()
    description = models.TextField(default=None, null=True)

    def get_name(self):
        return self.name

    def get_active_events_of_space(self):
        return self.event_set.filter_active().order_by('start_date_time')

    def get_all_events_of_space(self):
        return self.event_set.all().order_by('start_date_time')

    def coordinate_is_inside_location(self, latitude, longitude):
        distance_from_location = haversine(
            self.latitude,
            self.longitude,
            latitude,
            longitude
        )

        return distance_from_location <= AREA_RADIUS

    def coordinate_is_near_location(self, latitude, longitude):
        distance_from_location = haversine(
            self.latitude,
            self.longitude,
            latitude,
            longitude
        )

        return distance_from_location <= AREA_BUFFER_RADIUS


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

