import datetime

from communalspace import utils as app_utils
from communalspace.settings import MINIMUM_SECONDS_FOR_REWARD_ELIGIBILITY
from django.db import models
from django.db.models.functions import Trunc
from event.choices import (
    EventStatus,
    AttendanceActivityType,
    EventType,
    ParticipationType
)
from polymorphic.managers import PolymorphicManager
from polymorphic.models import PolymorphicModel
from rest_framework import serializers
from review.models import ParticipationReview
from space.models import LocationSerializer

import uuid


class EventManager(PolymorphicManager):
    def filter_active(self):
        return self.filter(status__in=(EventStatus.SCHEDULED, EventStatus.ON_GOING))


class EventParticipationManager(PolymorphicManager):
    def filter_by_event(self, event):
        event_participation_ids = [
            *InitiativeParticipation
            .objects
            .filter(event__id=event.get_id())
            .values_list('id', flat=True),
            *VolunteerParticipation
            .objects
            .filter(event__id=event.get_id())
            .values_list('id', flat=True),
            *ContributionParticipation
            .objects
            .filter(event__id=event.get_id())
            .values_list('id', flat=True)
        ]

        return self.filter(id__in=event_participation_ids)


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


class EventCategory(models.Model):
    id = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4)
    name = models.CharField(max_length=50)

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name


class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = '__all__'


class Event(PolymorphicModel):
    id = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4)
    name = models.CharField(max_length=50)
    description = models.TextField(null=True)
    start_date_time = models.DateTimeField()
    end_date_time = models.DateTimeField()

    volunteer_registration_enabled = models.BooleanField(default=True)

    current_num_of_participants = models.PositiveIntegerField(default=0)
    current_num_of_volunteers = models.PositiveIntegerField(default=0)

    location = models.ForeignKey('space.Location', on_delete=models.RESTRICT)
    creator = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey('event.EventCategory', on_delete=models.RESTRICT)
    status = models.CharField(max_length=10, choices=EventStatus.choices, default=EventStatus.SCHEDULED)
    tags = models.ManyToManyField('event.Tags')

    event_image_directory = models.TextField(null=True, default=None)

    # Analytics attributes
    average_sentiment_score = models.FloatField(default=None, null=True)
    number_of_sentiments_submitted = models.PositiveIntegerField(default=0)

    average_event_rating = models.FloatField(default=None, null=True)
    number_of_ratings_submitted = models.PositiveIntegerField(default=0)

    objects = EventManager()

    def save(self, *args, **kwargs):
        is_new = not self.pk
        super(Event, self).save(*args, **kwargs)

        if is_new:
            from forums.models import Forum
            Forum.objects.create(id=uuid.uuid4(), event=self)

    def get_type(self):
        raise NotImplementedError

    def get_participation_by_participant(self, participant):
        raise NotImplementedError

    def add_participant(self, participant):
        raise NotImplementedError

    def get_all_participants(self):
        raise NotImplementedError

    def get_or_create_forum(self):
        return self.forum_set.get_or_create()[0]

    def get_forum_sentiment_score(self):
        return self.get_or_create_forum().get_average_forum_sentiment_score()

    def update_average_sentiment_score(self, new_sentiment_score):
        self.average_sentiment_score = app_utils.update_average(
            new_sentiment_score,
            self.average_sentiment_score,
            self.number_of_sentiments_submitted
        )
        self.number_of_sentiments_submitted += 1
        self.save()
        return self.average_sentiment_score

    def update_average_event_rating(self, new_event_rating):
        self.average_event_rating = app_utils.update_average(
            new_event_rating,
            self.average_event_rating,
            self.number_of_ratings_submitted
        )
        self.number_of_ratings_submitted += 1
        self.save()
        return self.average_event_rating

    def get_volunteer_registration_enabled(self):
        return self.volunteer_registration_enabled

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

    def get_location_name(self):
        return self.location.get_name()

    def get_creator(self):
        return self.creator

    def get_creator_id(self):
        return self.creator.get_user_id()

    def get_creator_name(self):
        return self.creator.get_full_name()

    def get_category(self):
        return self.category

    def get_category_name(self):
        return self.get_category().get_name()

    def get_start_date_time(self):
        return self.start_date_time

    def get_end_date_time(self):
        return self.end_date_time

    def get_start_date_time_iso_format(self):
        return self.start_date_time.isoformat()

    def get_end_date_time_iso_format(self):
        return self.end_date_time.isoformat()

    def get_tags(self):
        return self.tags.all()

    def decrement_participant(self):
        if self.current_num_of_participants > 0:
            self.current_num_of_participants -= 1
            self.save()

    def get_all_volunteers(self):
        return self.volunteerparticipation_set.all()

    def get_all_type_participants(self):
        return EventParticipation.objects.filter_by_event(event=self)

    def get_all_type_participants_user_id_name_pair(self):
        return self.get_all_type_participants().values(
            user_id=models.F('participant__user_id'),
            full_name=models.F('participant__full_name')
        )

    def get_reviews(self):
        reviews = ParticipationReview.objects.none()
        for participation in self.get_all_type_participants():
            reviews = reviews | participation.get_reviews()

        return reviews

    def get_all_type_participation_by_participant(self, participant):
        return self.get_volunteer_participation_by_participant(volunteer=participant) or \
               self.get_participation_by_participant(participant=participant)

    def check_all_type_participation(self, participant):
        return self.get_all_type_participation_by_participant(participant=participant).exists()

    def get_volunteer_participation_by_participant(self, volunteer):
        return self.volunteerparticipation_set.filter(participant=volunteer).first()

    def add_volunteer(self, volunteer):
        event_participation = self.volunteerparticipation_set.create(participant=volunteer)
        self.current_num_of_volunteers += 1
        self.save()

        return event_participation

    def decrement_volunteer(self):
        if self.current_num_of_volunteers > 0:
            self.current_num_of_volunteers -= 1
            self.save()

    def is_active(self):
        return self.status in (EventStatus.SCHEDULED, EventStatus.ON_GOING)

    def is_ongoing(self):
        return self.status == EventStatus.ON_GOING

    def check_user_is_inside_event(self, user_latitude, user_longitude):
        return self.location.coordinate_is_inside_location(user_latitude, user_longitude)

    def check_user_is_near_event(self, user_latitude, user_longitude):
        return self.location.coordinate_is_near_location(user_latitude, user_longitude)

    def check_user_can_act_as_manager(self, user):
        """
        1. User is the creator of event, or
        2. User is a volunteer and has been granted access by other granter (and is currently attending)
        """
        if user == self.get_creator():
            return True

        participation = self.get_volunteer_participation_by_participant(user)
        return isinstance(participation, VolunteerParticipation) and participation.can_act_as_manager()

    def set_status(self, status):
        self.status = status
        self.save()

    def get_num_of_volunteers(self):
        return self.current_num_of_volunteers

    def get_num_of_participants(self):
        return self.current_num_of_participants

    def get_event_registration_per_day(self):
        return (self.get_all_type_participants()
                .annotate(registration_date=Trunc('registration_time', 'day'))
                .values('registration_date')
                .annotate(count=models.Count('registration_date'))
                .order_by('registration_date'))


class Initiative(Event):
    participation_registration_enabled = models.BooleanField(default=True)
    average_participant_attendance_duration = models.FloatField(default=0)
    number_of_durations_counted = models.PositiveIntegerField(default=0)

    def get_type(self):
        return EventType.INITIATIVE

    def get_participation_registration_enabled(self):
        return self.participation_registration_enabled

    def add_participant(self, participant):
        initiative_participation = self.initiativeparticipation_set.create(participant=participant)
        self.current_num_of_participants += 1
        self.save()

        return initiative_participation

    def get_participation_by_participant(self, participant):
        return self.initiativeparticipation_set.filter(participant=participant).first()

    def get_all_participants(self):
        return self.initiativeparticipation_set.all()

    def update_average_participant_attendance_duration(self, old_duration, new_duration):
        current_duration_total = self.number_of_durations_counted * self.average_participant_attendance_duration
        if self.number_of_durations_counted == 0 or old_duration == 0:
            new_duration_total = current_duration_total + new_duration
            self.average_participant_attendance_duration = new_duration_total / (self.number_of_durations_counted + 1)
            self.number_of_durations_counted += 1

        else:
            new_duration_total = current_duration_total - old_duration + new_duration
            self.average_participant_attendance_duration = new_duration_total / self.number_of_durations_counted

        self.save()
        return self.average_participant_attendance_duration

    def get_participants_average_attendance_duration(self):
        return self.average_participant_attendance_duration


class GoalKind(models.Model):
    kind = models.CharField(primary_key=True)

    def get_kind(self):
        return self.kind


class GoalKindSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalKind
        fields = '__all__'


class Project(Event):
    goal = models.FloatField()
    progress = models.FloatField(default=0)
    measurement_unit = models.CharField(max_length=30)
    goal_kind = models.ForeignKey('event.GoalKind', on_delete=models.RESTRICT, null=True, default=None)

    def get_type(self):
        return EventType.PROJECT

    def get_participation_by_participant(self, participant):
        return self.contributionparticipation_set.filter(participant=participant).first()

    def get_goal(self):
        return self.goal

    def get_goal_kind(self):
        return self.goal_kind.get_kind()

    def get_progress(self):
        return self.progress

    def get_measurement_unit(self):
        return self.measurement_unit

    def increase_progress(self, amount_to_increase):
        self.progress = self.progress + amount_to_increase
        self.save()

    def add_participant(self, participant):
        contributor_participation, created = self.contributionparticipation_set.get_or_create(participant=participant)

        if created:
            self.current_num_of_participants += 1
            self.save()

        return contributor_participation

    def register_contribution(self, contributing_user, amount_contributed):
        contribution_participation = self.add_participant(contributing_user)
        self.increase_progress(amount_contributed)
        contribution_participation.register_contribution(amount_contributed)
        return contribution_participation

    def get_activities(self):
        return ContributionActivity.objects.filter(participation__event=self).order_by('-timestamp')

    def get_all_participants(self):
        return self.contributionparticipation_set.all()


class EventParticipation(PolymorphicModel):
    participant = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    registration_time = models.DateTimeField(auto_now=True)
    first_participation_time = models.DateTimeField(null=True, default=None)
    has_left_forum = models.BooleanField(default=False)
    rewarded = models.BooleanField(default=False)
    submitted_review = models.BooleanField(default=False)

    objects = EventParticipationManager()

    def get_event(self) -> Event:
        raise NotImplementedError

    def get_participation_type(self):
        raise NotImplementedError

    def delete_participation(self):
        raise NotImplementedError

    def is_eligible_for_reward(self):
        raise NotImplementedError

    def can_submit_review(self):
        return not self.has_submitted_review()

    def set_submitted_review(self, submitted_review):
        self.submitted_review = submitted_review
        self.save()

    def has_been_rewarded(self):
        return self.rewarded

    def has_submitted_review(self):
        return self.submitted_review

    def set_rewarded(self, rewarded):
        self.rewarded = rewarded
        self.save()

    def add_activity(self, activity_type):
        return self.attendanceactivity_set.create(type=activity_type)

    def get_activities(self):
        return self.attendanceactivity_set.all().order_by('-timestamp')

    def get_has_left_forum(self):
        return self.has_left_forum

    def set_has_left_forum(self, has_left_forum):
        self.has_left_forum = has_left_forum
        self.save()

    def create_review(self, rating, comment, sentiment_score=0):
        self.set_submitted_review(True)
        self.get_event().update_average_event_rating(rating)
        self.get_event().update_average_sentiment_score(sentiment_score)

        return ParticipationReview.objects.create(
            participation=self,
            event_rating=rating,
            event_comment=comment,
            sentiment_score=sentiment_score
        )

    def get_reviews(self):
        return self.participationreview_set.all()

    def get_review(self):
        return self.get_reviews().first()

    def get_participant(self):
        return self.participant


class AttendableEventParticipation(EventParticipation):
    is_currently_attending = models.BooleanField(default=False)
    overall_duration_in_seconds = models.FloatField(default=0)
    has_attended = models.BooleanField(default=False)
    has_violated_geofencing_rule = models.BooleanField(default=False)

    def get_event(self):
        raise NotImplementedError

    def get_participation_type(self):
        raise NotImplementedError

    def delete_participation(self):
        raise NotImplementedError

    def can_submit_review(self):
        return self.has_attended and not self.has_submitted_review()

    def set_attended(self, attended):
        self.has_attended = attended
        self.save()

    def set_violated_geofencing_rule(self):
        self.has_violated_geofencing_rule = True
        self.save()

    def get_has_violated_geofencing_rule(self):
        return self.has_violated_geofencing_rule

    def is_eligible_for_reward(self):
        return (self.overall_duration_in_seconds >= MINIMUM_SECONDS_FOR_REWARD_ELIGIBILITY and
                not self.has_violated_geofencing_rule and not self.has_been_rewarded())

    def get_is_currently_attending(self):
        return self.is_currently_attending

    def check_in(self):
        if self.first_participation_time is None:
            self.first_participation_time = datetime.datetime.utcnow()

        self.set_attended(True)
        check_in_activity = self.add_activity(AttendanceActivityType.CHECK_IN.value)
        self.is_currently_attending = True
        self.save()

        return {
            'check_in_time': check_in_activity.get_timestamp_iso_format()
        }

    def check_out(self):
        check_out_activity = self.add_activity(AttendanceActivityType.CHECK_OUT.value)
        check_in_activity = (self.get_activities()
                             .filter(type=AttendanceActivityType.CHECK_IN.value)
                             .order_by('-timestamp')
                             .first())

        attendance_duration = (check_out_activity.get_timestamp() - check_in_activity.get_timestamp()).total_seconds()
        self.overall_duration_in_seconds += attendance_duration
        self.is_currently_attending = False

        self.save()
        return {
            'check_in_time': check_in_activity.get_timestamp_iso_format(),
            'check_out_time': check_out_activity.get_timestamp_iso_format(),
            'duration_in_seconds': attendance_duration,
            'total_duration_in_seconds': self.overall_duration_in_seconds,
        }

    def get_attendance_duration(self):
        return self.overall_duration_in_seconds


class InitiativeParticipation(AttendableEventParticipation):
    event = models.ForeignKey('event.Initiative', on_delete=models.CASCADE)

    def check_out(self):
        previous_attendance_duration = self.get_attendance_duration()
        check_out_data = super().check_out()
        new_attendance_duration = self.get_attendance_duration()
        self.get_event().update_average_participant_attendance_duration(
            previous_attendance_duration,
            new_attendance_duration
        )
        return check_out_data

    def get_event(self):
        return self.event

    def get_participation_type(self):
        return ParticipationType.PARTICIPANT

    def delete_participation(self):
        self.event.decrement_participant()
        self.delete()

    def _user_is_compliance_to_geofencing_rule_while_checking_out(self, latitude, longitude):
        return latitude is not None \
               and longitude is not None and \
               self.get_event().check_user_is_near_event(latitude, longitude)

    def self_check_out(self, latitude=None, longitude=None):
        check_out_data = self.check_out()
        if not self._user_is_compliance_to_geofencing_rule_while_checking_out(latitude, longitude) or \
                self.get_event().get_status() != EventStatus.ON_GOING.value:
            self.set_violated_geofencing_rule()

        return {
            **check_out_data,
            'violated_geofencing_rule': self.get_has_violated_geofencing_rule(),
        }


class VolunteerParticipation(AttendableEventParticipation):
    event = models.ForeignKey('event.Event', on_delete=models.CASCADE)
    granted_manager_access = models.BooleanField(default=False)

    def get_event(self):
        return self.event

    def get_participation_type(self):
        return ParticipationType.VOLUNTEER

    def has_manager_access(self):
        return self.granted_manager_access

    def can_act_as_manager(self):
        return self.granted_manager_access and self.get_is_currently_attending()

    def delete_participation(self):
        self.event.decrement_volunteer()
        self.delete()

    def set_as_manager(self, granted_manager_access):
        self.granted_manager_access = granted_manager_access
        self.save()


class ContributionParticipation(EventParticipation):
    event = models.ForeignKey('event.Project', on_delete=models.CASCADE)
    total_contribution = models.PositiveIntegerField(default=0)

    def get_event(self):
        return self.event

    def is_eligible_for_reward(self):
        return not self.has_been_rewarded()

    def get_participation_type(self):
        return ParticipationType.CONTRIBUTOR

    def get_total_contribution(self):
        return self.total_contribution

    def delete_participation(self):
        raise NotImplementedError('Contribution participation cannot be deleted')

    def register_contribution(self, contributed_amount):
        if self.first_participation_time is None:
            self.first_participation_time = datetime.datetime.utcnow()

        self.contributionactivity_set.create(contribution=contributed_amount)
        self.total_contribution += contributed_amount
        self.save()

    def get_contributions(self):
        return self.contributionactivity_set.all().order_by('-timestamp')


class ContributionActivity(models.Model):
    participation = models.ForeignKey('event.ContributionParticipation', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)
    contribution = models.PositiveIntegerField(default=0)


class ContributionActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContributionActivity
        fields = [
            'timestamp',
            'contribution',
        ]


class ContributionParticipationSerializer(serializers.ModelSerializer):
    activities = serializers.SerializerMethodField(method_name='get_activity_data')

    def get_activity_data(self, instance):
        return ContributionActivitySerializer(instance.get_contributions(), many=True).data

    class Meta:
        model = ContributionParticipation
        fields = [
            'total_contribution',
            'activities',
        ]


class EventParticipationSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField(method_name='get_type')

    def get_type(self, instance):
        return instance.get_participation_type()

    class Meta:
        model = EventParticipation
        fields = [
            'type',
            'participant',
            'registration_time',
            'has_left_forum',
            'rewarded',
            'submitted_review',
        ]


class BaseAttendableEventParticipationSerializer(serializers.ModelSerializer):
    activities = serializers.SerializerMethodField(method_name='get_activity_data')

    def get_activity_data(self, instance):
        return AttendanceActivitySerializer(instance.get_activities(), many=True).data

    class Meta:
        model = AttendableEventParticipation
        fields = [
            'is_currently_attending',
            'overall_duration_in_seconds',
            'has_attended',
            'activities',
        ]


class AttendableEventParticipationSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        base_participation_data = BaseAttendableEventParticipationSerializer(instance).data
        if isinstance(instance, VolunteerParticipation):
            base_participation_data['granted_manager_access'] = instance.has_manager_access()
            base_participation_data['can_act_as_manager'] = instance.can_act_as_manager()

        return base_participation_data

    class Meta:
        model = AttendableEventParticipation
        fields = '__all__'


class BaseEventParticipationSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        base_participation_data = EventParticipationSerializer(instance).data

        if isinstance(instance, AttendableEventParticipation):
            return {
                **base_participation_data,
                **AttendableEventParticipationSerializer(instance).data
            }

        else:
            return {
                **base_participation_data,
                **ContributionParticipationSerializer(instance).data
            }

    class Meta:
        model = EventParticipation
        fields = '__all__'


class ParticipationSerializerWithEventData(serializers.ModelSerializer):
    def to_representation(self, instance):
        event_data = BaseEventSerializer(instance.get_event()).data
        participation_data = BaseEventParticipationSerializer(instance).data

        return {
            'event': event_data,
            **participation_data
        }

    class Meta:
        model = EventParticipation
        fields = '__all__'


class AttendanceActivity(models.Model):
    participation = models.ForeignKey('event.AttendableEventParticipation', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)
    type = models.CharField(choices=AttendanceActivityType.choices, max_length=15)

    def get_timestamp(self):
        return self.timestamp

    def get_timestamp_iso_format(self):
        return self.timestamp.isoformat()


class AttendanceActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceActivity
        fields = '__all__'


class TransactionHistory(models.Model):
    project = models.ForeignKey('event.Project', on_delete=models.CASCADE)
    transaction_time = models.DateTimeField(auto_now=True)
    transaction_value = models.FloatField()


class TransactionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionHistory
        fields = '__all__'


class BaseEventSerializer(serializers.ModelSerializer):
    event_type = serializers.SerializerMethodField(method_name='get_event_type')
    event_location = serializers.SerializerMethodField(method_name='get_event_location_data')
    event_category = serializers.SerializerMethodField(method_name='get_category_data')
    event_creator_id = serializers.SerializerMethodField(method_name='get_event_creator_user_id')
    event_start_date_time = serializers.SerializerMethodField(method_name='get_start_date_time_iso_format')
    event_end_date_time = serializers.SerializerMethodField(method_name='get_end_date_time_iso_format')
    event_tags = serializers.SerializerMethodField(method_name='get_tags_names')
    forum_sentiment_score = serializers.SerializerMethodField(method_name='get_forum_sentiment_score')

    def get_forum_sentiment_score(self, event):
        return event.get_forum_sentiment_score()

    def get_event_type(self, event):
        return event.get_type()

    def get_event_location_data(self, event):
        return LocationSerializer(event.get_location()).data

    def get_category_data(self, event):
        return EventCategorySerializer(event.get_category()).data

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
            'volunteer_registration_enabled',
            'current_num_of_volunteers',
            'current_num_of_participants',
            'status',
            'event_type',
            'event_location',
            'event_category',
            'event_creator_id',
            'event_start_date_time',
            'event_end_date_time',
            'event_tags',
            'average_sentiment_score',
            'average_event_rating',
            'forum_sentiment_score',
        ]


class InitiativeSerializer(serializers.ModelSerializer):
    def to_representation(self, initiative):
        serialized_data = BaseEventSerializer(initiative).data
        serialized_data['participation_registration_enabled'] = initiative.get_participation_registration_enabled()
        serialized_data['average_participant_attendance_duration'] = \
            initiative.get_participants_average_attendance_duration()

        return serialized_data

    class Meta:
        model = Initiative
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    def to_representation(self, project):
        serialized_data = BaseEventSerializer(project).data
        serialized_data['goal'] = project.get_goal()
        serialized_data['goal_kind'] = project.get_goal_kind()
        serialized_data['measurement_unit'] = project.get_measurement_unit()
        serialized_data['progress'] = project.get_progress()
        serialized_data['transactions'] = ContributionActivitySerializer(project.get_activities(), many=True).data
        return serialized_data

    class Meta:
        model = Project
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    def to_representation(self, event):
        if isinstance(event, Initiative):
            serialized_data = InitiativeSerializer(event).data

        else:
            serialized_data = ProjectSerializer(event).data

        return serialized_data

    class Meta:
        model = Event
        fields = '__all__'
