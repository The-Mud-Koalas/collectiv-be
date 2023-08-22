from django.db import models
from rest_framework import serializers
import uuid


class Space(models.Model):
    id = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4)
    name = models.CharField(max_length=50)
    latitude = models.FloatField()
    longitude = models.FloatField()


class SpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Space
        fields = '__all__'

