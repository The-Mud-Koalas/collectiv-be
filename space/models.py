from space.services.haversine import haversine
from datetime import datetime, timezone
from django.db import models
from rest_framework import serializers
import uuid


class Location(models.Model):
    id = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4)
    name = models.CharField(max_length=50)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def get_active_events_of_space(self):
        return (self.event_set.all()
                    .filter(end_date_time__gte=datetime.now(tz=timezone.utc))
                    .order_by('start_date_time'))

    def coordinate_is_inside_location(self, latitude, longitude, tolerance=0.1):
        distance_from_location = haversine(
            self.latitude,
            self.longitude,
            latitude,
            longitude
        )

        return distance_from_location <= tolerance


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

