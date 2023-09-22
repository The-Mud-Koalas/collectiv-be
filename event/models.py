from django.db import models
from polymorphic.models import PolymorphicModel
from rest_framework import serializers
from space.models import LocationSerializer
import uuid


class Tags(models.Model):
    id = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4)
    name = models.CharField(max_length=30)

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]


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

    def get_participation_by_participant(self, participant):
        matching_participation = self.eventparticipation_set.filter(participant=participant)

        if len(matching_participation) > 0:
            return matching_participation[0]

        else:
            return None

    def check_participation(self, participant):
        return self.get_participation_by_participant(participant=participant) is not None

    def add_participant(self, participant):
        event_participation = EventParticipation.objects.create(
            event=self,
            participant=participant,
            participation_type=EventParticipationType.PARTICIPANT
        )

        return event_participation

    def add_volunteer(self, volunteer):
        event_participation = EventParticipation.objects.create(
            event=self,
            participant=volunteer,
            participation_type=EventParticipationType.VOLUNTEER
        )

        return event_participation

    def is_active(self):
        return self.status in (EventStatus.SCHEDULED, EventStatus.ON_GOING)


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
    event_tags = serializers.SerializerMethodField(method_name='get_tags_names')

    def get_event_location_data(self, event):
        return LocationSerializer(event.get_location()).data

    def get_event_creator_user_id(self, event):
        return event.get_creator_id()

    def get_start_date_time_iso_format(self, event):
        return event.get_start_date_time_iso_format()

    def get_end_date_time_iso_format(self, event):
        return event.get_end_date_time_iso_format()

    def get_tags_names(self, event):
        return TagsSerializer(event.get_tags(), many=True).data

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
            'event_end_date_time',
            'event_tags'
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


class EventParticipationType(models.TextChoices):
    PARTICIPANT = 'participant'
    VOLUNTEER = 'volunteer'


class EventParticipation(models.Model):
    event = models.ForeignKey('event.Event', on_delete=models.CASCADE)
    participant = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    registration_date = models.DateTimeField(auto_now=True)

    event_rating = models.SmallIntegerField(null=True)
    event_review = models.TextField(null=True)
    does_attend = models.BooleanField(default=False)

    participation_type = models.CharField(choices=EventParticipationType.choices)

    class Meta:
        indexes = [
            models.Index(fields=['event', 'participant'])
        ]

    def get_participation_type(self):
        return self.participation_type
