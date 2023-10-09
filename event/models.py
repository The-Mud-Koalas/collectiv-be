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

    objects = EventManager()

    def get_type(self):
        raise NotImplementedError

    def get_participation_by_participant(self, participant):
        raise NotImplementedError

    def add_participant(self, participant):
        raise NotImplementedError

    def get_all_participants(self):
        raise NotImplementedError

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

    def get_creator(self):
        return self.creator

    def get_creator_id(self):
        return self.get_creator().get_user_id()

    def get_category(self):
        return self.category

    def get_category_name(self):
        return self.get_category().get_name()

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

    def get_all_type_participations(self):
        return EventParticipation.objects.filter_by_event(event=self)

    def get_reviews(self):
        reviews = ParticipationReview.objects.none()
        for participation in self.get_all_type_participations():
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

    # Analytics methods
    def get_event_registration_per_day(self):
        return (self.get_all_type_participations()
                .annotate(registration_date=Trunc('registration_time', 'day'))
                .values('registration_date')
                .annotate(models.Count('registration_date'))
                .order_by('registration_date'))

    def get_event_average_rating(self):
        """
        Return average rating of event
        """
        return (self.get_reviews()
                .aggregate(rating_average=models.Avg('event_rating'))
                .get('rating_average'))


class Initiative(Event):
    participation_registration_enabled = models.BooleanField(default=True)

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

    def get_participants_average_attendance_duration(self):
        return (self.get_all_participants()
                .aggregate(average_duration=models.Avg('overall_duration_in_seconds'))
                .get('average_duration'))


class GoalKind(models.Model):
    kind = models.CharField(primary_key=True)


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
    has_left_forum = models.BooleanField(default=False)
    rewarded = models.BooleanField(default=False)
    submitted_review = models.BooleanField(default=False)

    objects = EventParticipationManager()

    def get_event(self):
        raise NotImplementedError

    def get_participation_type(self):
        raise NotImplementedError

    def delete_participation(self):
        raise NotImplementedError

    def is_eligible_for_reward(self):
        raise NotImplementedError

    def get_reviews(self):
        return self.participationreview_set.all()

    def get_review(self):
        return self.get_reviews().first()

    def can_submit_review(self):
        return not self.has_submitted_review()

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

    def create_review(self, rating, comment):
        self.submitted_review = True
        self.save()
        return ParticipationReview.objects.create(
            participation=self,
            event_rating=rating,
            event_comment=comment
        )

    def get_review(self):
        return self.participationreview_set.filter(participation=self).first()


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


class InitiativeParticipation(AttendableEventParticipation):
    event = models.ForeignKey('event.Initiative', on_delete=models.CASCADE)

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

    def can_act_as_manager(self):
        return self.granted_manager_access and self.get_is_currently_attending()

    def delete_participation(self):
        self.event.decrement_volunteer()
        self.delete()

    def set_as_manager(self):
        self.granted_manager_access = True
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


class AttendableEventParticipationSerializer(serializers.ModelSerializer):
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
        event_data = EventSerializer(instance.get_event()).data
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


class EventSerializer(serializers.ModelSerializer):
    event_type = serializers.SerializerMethodField(method_name='get_event_type')
    event_location = serializers.SerializerMethodField(method_name='get_event_location_data')
    event_category = serializers.SerializerMethodField(method_name='get_category_data')
    event_creator_id = serializers.SerializerMethodField(method_name='get_event_creator_user_id')
    event_start_date_time = serializers.SerializerMethodField(method_name='get_start_date_time_iso_format')
    event_end_date_time = serializers.SerializerMethodField(method_name='get_end_date_time_iso_format')
    event_tags = serializers.SerializerMethodField(method_name='get_tags_names')

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
            'event_tags'
        ]


class InitiativeSerializer(serializers.ModelSerializer):
    def to_representation(self, initiative):
        serialized_data = EventSerializer(initiative).data
        serialized_data['participation_registration_enabled'] = initiative.get_participation_registration_enabled()
        return serialized_data

    class Meta:
        model = Initiative
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    def to_representation(self, project):
        serialized_data = EventSerializer(project).data
        serialized_data['goal'] = project.get_goal()
        serialized_data['measurement_unit'] = project.get_measurement_unit()
        serialized_data['progress'] = project.get_progress()
        serialized_data['transactions'] = ContributionActivitySerializer(project.get_activities(), many=True).data
        return serialized_data

    class Meta:
        model = Project
        fields = '__all__'


class BaseEventSerializer(serializers.ModelSerializer):
    def to_representation(self, event):
        if isinstance(event, Initiative):
            serialized_data = InitiativeSerializer(event).data

        else:
            serialized_data = ProjectSerializer(event).data

        return serialized_data

    class Meta:
        model = Event
        fields = '__all__'


