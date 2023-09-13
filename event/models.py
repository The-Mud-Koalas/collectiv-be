from django.db import models
from polymorphic.models import PolymorphicModel
from rest_framework import serializers
from space.models import LocationSerializer
import uuid


class Tags(models.Model):
    id = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4)
    name = models.CharField(max_length=30)


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = '__all__'


class EventStatus(models.TextChoices):
    SCHEDULED = 'Scheduled'
    ON_GOING = 'On Going'
    COMPLETED = 'Completed'
    CANCELLED = 'Cancelled'


class Event(PolymorphicModel):
    id = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4)
    name = models.CharField(max_length=50)
    description = models.TextField(null=True)
    min_num_of_volunteers = models.IntegerField(default=0)
    start_date_time = models.DateTimeField()
    end_date_time = models.DateTimeField()

    location = models.ForeignKey('space.Location', on_delete=models.RESTRICT)

    creator = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=10, choices=EventStatus.choices, default=EventStatus.SCHEDULED)
    tags = models.ManyToManyField('event.Tags')

    event_image_directory = models.TextField(null=True, default=None)

    def get_event_image_directory(self):
        return self.event_image_directory

    def set_event_image(self, event_image_directory):
        self.event_image_directory = event_image_directory
        self.save()

    def get_id(self):
        return str(self.id)

    def add_tags(self, tag):
        self.tags.add(tag)
        self.save()

    def get_location(self):
        return self.location

    def get_creator_id(self):
        return self.creator.get_user_id()

    def get_start_date_time_iso_format(self):
        return self.start_date_time.isoformat()

    def get_end_date_time_iso_format(self):
        return self.end_date_time.isoformat()

    def get_tags(self):
        return self.tags.all()


class Project(Event):
    goal = models.FloatField()
    measurement_unit = models.CharField(max_length=30)

    def get_goal(self):
        return self.goal

    def get_measurement_unit(self):
        return self.measurement_unit


class EventSerializer(serializers.ModelSerializer):
    event_location = serializers.SerializerMethodField(method_name='get_event_location_data')
    event_creator_id = serializers.SerializerMethodField(method_name='get_event_creator_user_id')
    event_start_date_time = serializers.SerializerMethodField(method_name='get_start_date_time_iso_format')
    event_end_date_time = serializers.SerializerMethodField(method_name='get_end_date_time_iso_format')

    def get_event_location_data(self, event):
        return LocationSerializer(event.get_location()).data

    def get_event_creator_user_id(self, event):
        return event.get_creator_id()

    def get_start_date_time_iso_format(self, event):
        return event.get_start_date_time_iso_format()

    def get_end_date_time_iso_format(self, event):
        return event.get_end_date_time_iso_format()

    class Meta:
        model = Event
        fields = [
            'id',
            'name',
            'description',
            'min_num_of_volunteers',
            'event_location',
            'event_creator_id',
            'event_start_date_time',
            'event_end_date_time'
        ]


class BaseEventSerializer(serializers.ModelSerializer):
    def to_representation(self, event):
        serialized_data = EventSerializer(event).data
        if isinstance(event, Project):
            serialized_data['goal'] = event.get_goal()
            serialized_data['measurement_unit'] = event.get_measurement_unit()

        return serialized_data

    class Meta:
        model = Event
        fields = '__all__'



