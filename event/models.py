from django.db import models
from event.exceptions import InvalidCheckInCheckOutException
from polymorphic.models import PolymorphicModel
from rest_framework import serializers
from review.models import ParticipationVolunteeringReview, ContributionReview
from space.models import LocationSerializer

import datetime
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


class EventCategory(models.Model):
    id = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4)
    name = models.CharField(max_length=50)


class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = '__all__'


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

    def get_type(self):
        return 'event'

    def get_status(self):
        return self.status

    def set_event_image(self, event_image_directory):
        self.event_image_directory = event_image_directory
        self.save()

    def add_tags(self, tag):
        self.tags.add(tag)
        self.save()

    def get_event_image_directory(self):
        return self.event_image_directory

    def get_name(self):
        return self.name

    def get_id(self):
        return str(self.id)

    def get_location(self):
        return self.location

    def get_creator(self):
        return self.creator

    def get_creator_id(self):
        return self.get_creator().get_user_id()

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
        )

        return event_participation

    def add_volunteer(self, volunteer):
        event_participation = EventVolunteerParticipation.objects.create(
            event=self,
            participant=volunteer,
        )

        return event_participation

    def is_active(self):
        return self.status in (EventStatus.SCHEDULED, EventStatus.ON_GOING)

    def is_ongoing(self):
        return self.status == EventStatus.ON_GOING

    def check_user_is_inside_event(self, user_latitude, user_longitude):
        return self.location.coordinate_is_inside_location(user_latitude, user_longitude)

    def check_user_is_granted_manager_access(self, user):
        """
        1. User is the creator of event, or
        2. User is a volunteer and has been granted access by other granter
        """
        if user == self.get_creator():
            return True

        participation = self.get_participation_by_participant(user)
        return isinstance(participation, EventVolunteerParticipation) and participation.get_granted_manager_access()

    def set_status(self, status):
        self.status = status
        self.save()


class Project(Event):
    goal = models.FloatField()
    progress = models.FloatField(default=0)
    measurement_unit = models.CharField(max_length=30)

    def increase_progress(self, amount_to_increase):
        self.progress = self.progress + amount_to_increase
        self.save()

    def decrease_progress(self, amount_to_decrease):
        if self.progress < amount_to_decrease:
            raise ValueError('Amount to decrease must not exceed the current progress')

        self.progress = self.progress - amount_to_decrease
        self.save()

    def get_type(self):
        return 'project'

    def get_goal(self):
        return self.goal

    def get_measurement_unit(self):
        return self.measurement_unit

    def add_participant(self, participant):
        event_participation = ProjectContribution.objects.create(
            event=self,
            contributor=participant,
        )

        return event_participation

    def get_participation_by_participant(self, participant):
        matching_participation = self.projectcontribution_set.filter(contributor=participant)

        if len(matching_participation) > 0:
            return matching_participation[0]

        else:
            return None


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


class EventParticipation(PolymorphicModel):
    event = models.ForeignKey('event.Event', on_delete=models.CASCADE)
    participant = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    registration_time = models.DateTimeField(auto_now=True)

    check_in_time = models.DateTimeField(null=True)
    check_out_time = models.DateTimeField(null=True)

    has_left_forum = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['event', 'participant'])
        ]

    def get_participation_type(self):
        return 'participant'

    def get_status(self):
        if self.check_out_time is not None:
            return 'past'

        if self.check_in_time is not None and self.check_out_time is None:
            return 'ongoing'

        if self.check_in_time is None:
            return 'future'

    def check_in(self):
        if self.check_in_time is not None:
            raise InvalidCheckInCheckOutException(f'User already checked in at {self.check_in_time}')

        self.check_in_time = datetime.datetime.utcnow()
        self.save()

    def check_out(self):
        if self.check_in_time is None:
            raise InvalidCheckInCheckOutException('Check in time does not exist')

        if self.check_out_time is not None:
            raise InvalidCheckInCheckOutException(f'User already checked out at {self.check_out_time}')

        self.check_out_time = datetime.datetime.utcnow()
        self.save()

    def has_checked_in(self):
        return self.check_in_time is not None

    def has_checked_out(self):
        return self.check_out_time is not None

    def create_review(self, rating, comment):
        review = ParticipationVolunteeringReview.objects.create(
            participation=self,
            event_rating=rating,
            event_comment=comment,
        )

        return review

    def get_has_left_forum(self):
        return self.has_left_forum

    def set_has_left_forum(self, has_left_forum):
        self.has_left_forum = has_left_forum
        self.save()


class EventVolunteerParticipation(EventParticipation):
    granted_manager_access = models.BooleanField(default=False)

    def get_participant_type(self):
        return 'volunteer'

    def get_granted_manager_access(self):
        return self.granted_manager_access

    def set_as_manager(self):
        if self.check_in_time is None:
            raise InvalidCheckInCheckOutException('User must check in before being granted a managerial role')

        self.granted_manager_access = True
        self.save()


class ProjectContribution(models.Model):
    event = models.ForeignKey('event.Project', on_delete=models.CASCADE)
    contributor = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)

    event_rating = models.SmallIntegerField(null=True)
    event_review = models.TextField(null=True)

    contribution_time = models.DateTimeField(auto_now=True)

    def create_review(self, rating, comment):
        return ContributionReview(
            contribution=self,
            event_rating=rating,
            event_comment=comment,
        )


class EventParticipationSerializer(serializers.ModelSerializer):
    event_data = serializers.SerializerMethodField(method_name='get_event_data')
    status = serializers.SerializerMethodField(method_name='get_participation_status')

    def get_participation_status(self, event_participation):
        return event_participation.get_status()

    def get_event_data(self, event_participation):
        return BaseEventSerializer(event_participation.event).data

    class Meta:
        model = EventParticipation
        fields = [
            'event_data',
            'registration_time',
            'status',
            'check_in_time',
            'check_out_time',
            'participant',
            'has_left_forum',
        ]


class BaseEventParticipationSerializer(serializers.ModelSerializer):
    def to_representation(self, event_participation):
        serialized_data = EventParticipationSerializer(event_participation).data
        if isinstance(event_participation, EventVolunteerParticipation):
            serialized_data['granted_manager_access'] = event_participation.get_granted_manager_access()

        return serialized_data

    class Meta:
        model = EventParticipation
        fields = '__all__'
