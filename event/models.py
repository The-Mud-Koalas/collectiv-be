from communalspace.settings import MINIMUM_SECONDS_FOR_REWARD_ELIGIBILITY
from django.db import models
from event.choices import (
    EventStatus,
    AttendanceActivityType,
    EventType,
    ParticipationType
)
from event.managers import EventManager
from polymorphic.models import PolymorphicModel
from rest_framework import serializers
from review.models import ParticipationVolunteeringReview, ContributionReview
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

    def get_all_type_participation_by_participant(self, participant):
        raise NotImplementedError

    def check_all_type_participation(self, participant):
        raise NotImplementedError

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

    def check_user_is_granted_manager_access(self, user):
        """
        1. User is the creator of event, or
        2. User is a volunteer and has been granted access by other granter
        """
        if user == self.get_creator():
            return True

        participation = self.get_participation_by_participant(user)
        return isinstance(participation, VolunteerParticipation) and participation.get_granted_manager_access()

    def set_status(self, status):
        self.status = status
        self.save()


class Initiative(Event):
    participation_registration_enabled = models.BooleanField(default=True)
    current_num_of_participants = models.PositiveIntegerField(default=0)

    def get_type(self):
        return EventType.INITIATIVE

    def get_participation_registration_enabled(self):
        return self.participation_registration_enabled

    def get_current_num_of_participants(self):
        return self.current_num_of_participants

    def add_participant(self, participant):
        initiative_participation = self.initiativeparticipation_set.create(participant=participant)
        self.current_num_of_participants += 1
        self.save()

        return initiative_participation

    def decrement_participant(self):
        if self.current_num_of_participants > 0:
            self.current_num_of_participants -= 1
            self.save()

    def get_participation_by_participant(self, participant):
        return self.initiativeparticipation_set.filter(participant=participant).first()

    def get_all_type_participation_by_participant(self, participant):
        return self.get_volunteer_participation_by_participant(volunteer=participant) or \
               self.get_participation_by_participant(participant=participant)

    def check_all_type_participation(self, participant):
        return self.get_all_type_participation_by_participant(participant=participant).exists()


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

    current_num_of_contributor = models.PositiveIntegerField(default=0)

    def get_type(self):
        return EventType.PROJECT

    def get_contribution_by_contributor(self, contributor):
        return self.contributionparticipation_set.filter(participant=contributor).first()

    def add_contributor(self, contributor):
        contributor_participation = self.contributionparticipation_set.get_or_create(participant=contributor)
        self.current_num_of_contributor += 1
        self.save()

        return contributor_participation

    def get_all_type_participation_by_participant(self, participant):
        return self.get_volunteer_participation_by_participant(volunteer=participant) or \
               self.get_contribution_by_contributor(contributor=participant)

    def check_all_type_participation(self, participant):
        return self.get_all_type_participation_by_participant(participant=participant).exists()

    def get_transactions(self):
        return self.transactionhistory_set.all()

    def increase_progress(self, amount_to_increase):
        self.transactionhistory_set.create(transaction_value=amount_to_increase)
        self.progress = self.progress + amount_to_increase
        self.save()

    def decrease_progress(self, amount_to_decrease):
        if self.progress < amount_to_decrease:
            raise ValueError('Amount to decrease must not exceed the current progress')

        self.transactionhistory_set.creaete(transaction_value=-amount_to_decrease)
        self.progress = self.progress - amount_to_decrease
        self.save()

    def get_goal(self):
        return self.goal

    def get_progress(self):
        return self.progress

    def get_measurement_unit(self):
        return self.measurement_unit


class EventParticipation(PolymorphicModel):
    participant = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    registration_time = models.DateTimeField(auto_now=True)
    has_left_forum = models.BooleanField(default=False)
    rewarded = models.BooleanField(default=False)

    def get_participation_type(self):
        raise NotImplementedError

    def delete_participation(self):
        raise NotImplementedError

    def is_eligible_for_reward(self):
        raise NotImplementedError

    def can_submit_review(self):
        raise NotImplementedError

    def has_been_rewarded(self):
        return self.rewarded

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

    def can_submit_review(self):
        return self.has_attended

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
                not self.has_violated_geofencing_rule)

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

    def _user_is_compliance_to_geofencing_rule_while_checking_out(self, latitude, longitude):
        return latitude is not None \
               and longitude is not None and \
               self.get_event().check_user_is_near_event(latitude, longitude)

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
        }

    def self_check_out(self):
        raise NotImplementedError

    def get_participation_type(self):
        raise NotImplementedError

    def delete_participation(self):
        raise NotImplementedError


class InitiativeParticipation(AttendableEventParticipation):
    event = models.ForeignKey('event.Initiative', on_delete=models.CASCADE)

    def get_event(self):
        return self.event

    def get_participation_type(self):
        return ParticipationType.PARTICIPANT

    def delete_participation(self):
        self.event.decrement_participant()
        self.delete()

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

    def get_granted_manager_access(self):
        return self.granted_manager_access

    def delete_participation(self):
        self.event.decrement_volunteer()
        self.delete()


class ContributionParticipation(EventParticipation):
    event = models.ForeignKey('event.Project', on_delete=models.CASCADE)

    def can_submit_review(self):
        return True

    def is_eligible_for_reward(self):
        return True

    def get_participation_type(self):
        return ParticipationType.CONTRIBUTOR

    def delete_participation(self):
        raise NotImplementedError('Contribution participation cannot be deleted')


class AttendableEventParticipationSerializer(serializers.ModelSerializer):
    activity = serializers.SerializerMethodField(method_name='get_activity_data')

    def get_activity_data(self, instance):
        return AttendanceActivitySerializer(instance.get_activities(), many=True).data

    class Meta:
        model = AttendableEventParticipation
        fields = [
            'is_currently_attending',
            'overall_duration_in_seconds',
            'has_attended',
            'activity',
        ]


class BaseEventParticipationSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        if isinstance(instance, AttendableEventParticipation):
            return AttendableEventParticipationSerializer(instance).data

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


# class Event(PolymorphicModel):
#     id = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4)
#     name = models.CharField(max_length=50)
#     description = models.TextField(null=True)
#     start_date_time = models.DateTimeField()
#     end_date_time = models.DateTimeField()
#
#     min_num_of_volunteers = models.PositiveIntegerField(default=0)
#     current_num_of_participants = models.PositiveIntegerField(default=0)
#     current_num_of_volunteers = models.PositiveIntegerField(default=0)
#
#     location = models.ForeignKey('space.Location', on_delete=models.RESTRICT)
#     creator = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
#     category = models.ForeignKey('event.EventCategory', on_delete=models.RESTRICT)
#
#     status = models.CharField(max_length=10, choices=EventStatus.choices, default=EventStatus.SCHEDULED)
#     tags = models.ManyToManyField('event.Tags')
#
#     event_image_directory = models.TextField(null=True, default=None)
#
#     objects = EventManager()
#
#     def get_type(self):
#         return EventType.INITIATIVE
#
#     def get_status(self):
#         return self.status
#
#     def set_event_image(self, event_image_directory):
#         self.event_image_directory = event_image_directory
#         self.save()
#
#     def add_tags(self, tag):
#         self.tags.add(tag)
#         self.save()
#
#     def get_event_image_directory(self):
#         return self.event_image_directory
#
#     def get_name(self):
#         return self.name
#
#     def get_id(self):
#         return str(self.id)
#
#     def get_location(self):
#         return self.location
#
#     def get_creator(self):
#         return self.creator
#
#     def get_creator_id(self):
#         return self.get_creator().get_user_id()
#
#     def get_category(self):
#         return self.category
#
#     def get_category_name(self):
#         return self.get_category().get_name()
#
#     def get_start_date_time_iso_format(self):
#         return self.start_date_time.isoformat()
#
#     def get_end_date_time_iso_format(self):
#         return self.end_date_time.isoformat()
#
#     def get_tags(self):
#         return self.tags.all()
#
#     def get_participation_by_participant(self, participant):
#         matching_participation = self.eventparticipation_set.filter(participant=participant)
#
#         if len(matching_participation) > 0:
#             return matching_participation[0]
#
#         else:
#             return None
#
#     def check_participation(self, participant):
#         return self.get_participation_by_participant(participant=participant) is not None
#
#     def add_participant(self, participant):
#         event_participation = EventParticipation.objects.create(
#             event=self,
#             participant=participant,
#         )
#
#         self.current_num_of_participants += 1
#         self.save()
#
#         return event_participation
#
#     def add_volunteer(self, volunteer):
#         event_participation = EventVolunteerParticipation.objects.create(
#             event=self,
#             participant=volunteer,
#         )
#
#         self.current_num_of_volunteers += 1
#         self.save()
#
#         return event_participation
#
#     def decrement_participant(self):
#         if self.current_num_of_participants > 0:
#             self.current_num_of_participants -= 1
#             self.save()
#
#     def decrement_volunteer(self):
#         if self.current_num_of_volunteers > 0:
#             self.current_num_of_volunteers -= 1
#             self.save()
#
#     def is_active(self):
#         return self.status in (EventStatus.SCHEDULED, EventStatus.ON_GOING)
#
#     def is_ongoing(self):
#         return self.status == EventStatus.ON_GOING
#
#     def check_user_is_inside_event(self, user_latitude, user_longitude):
#         return self.location.coordinate_is_inside_location(user_latitude, user_longitude)
#
#     def check_user_is_granted_manager_access(self, user):
#         """
#         1. User is the creator of event, or
#         2. User is a volunteer and has been granted access by other granter
#         """
#         if user == self.get_creator():
#             return True
#
#         participation = self.get_participation_by_participant(user)
#         return isinstance(participation, EventVolunteerParticipation) and participation.get_granted_manager_access()
#
#     def set_status(self, status):
#         self.status = status
#         self.save()


# class Project(Event):
#     goal = models.FloatField()
#     progress = models.FloatField(default=0)
#     measurement_unit = models.CharField(max_length=30)
#     goal_kind = models.ForeignKey('event.GoalKind', on_delete=models.RESTRICT, null=True, default=None)
#
#     def get_participation_by_participant(self, participant):
#         raise NotImplementedError()
#
#     def check_participation(self, participant):
#         raise NotImplementedError()
#
#     def add_participant(self, participant):
#         raise NotImplementedError()
#
#     def get_contribution_by_contributor(self, contributor):
#         matching_participation = self.projectcontribution_set.filter(contributor=contributor)
#
#         if len(matching_participation) > 0:
#             return matching_participation[0]
#
#         else:
#             return None
#
#     def add_contributor(self, contributor):
#         event_participation = ProjectContribution.objects.create(
#             event=self,
#             contributor=contributor,
#         )
#
#         return event_participation
#
#     def get_transactions(self):
#         return self.transactionhistory_set.all()
#
#     def increase_progress(self, amount_to_increase):
#         TransactionHistory.objects.create(
#             project=self,
#             transaction_value=amount_to_increase
#         )
#         self.progress = self.progress + amount_to_increase
#         self.save()
#
#     def decrease_progress(self, amount_to_decrease):
#         if self.progress < amount_to_decrease:
#             raise ValueError('Amount to decrease must not exceed the current progress')
#
#         TransactionHistory.objects.create(
#             project=self,
#             transaction_value=-amount_to_decrease
#         )
#         self.progress = self.progress - amount_to_decrease
#         self.save()
#
#     def get_type(self):
#         return EventType.PROJECT
#
#     def get_goal(self):
#         return self.goal
#
#     def get_progress(self):
#         return self.progress
#
#     def get_measurement_unit(self):
#         return self.measurement_unit


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
        serialized_data['current_num_of_participants'] = initiative.get_current_num_of_participants()
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
        serialized_data['transactions'] = TransactionHistorySerializer(project.get_transactions(), many=True).data
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


# class EventParticipation(PolymorphicModel):
#     event = models.ForeignKey('event.Event', on_delete=models.CASCADE)
#     participant = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
#     registration_time = models.DateTimeField(auto_now=True)
#
#     check_in_time = models.DateTimeField(null=True)
#     check_out_time = models.DateTimeField(null=True)
#
#     has_left_forum = models.BooleanField(default=False)
#
#     class Meta:
#         indexes = [
#             models.Index(fields=['event', 'participant'])
#         ]
#
#     def get_participation_type(self):
#         return ParticipationType.PARTICIPANT
#
#     def get_status(self):
#         if self.check_out_time is not None:
#             return ParticipationStatus.PAST
#
#         if self.check_in_time is not None and self.check_out_time is None:
#             return ParticipationStatus.ON_GOING
#
#         if self.check_in_time is None:
#             return ParticipationStatus.FUTURE
#
#     def check_in(self):
#         if self.check_in_time is not None:
#             raise InvalidCheckInCheckOutException(f'User already checked in at {self.check_in_time}')
#
#         self.check_in_time = datetime.datetime.utcnow()
#         self.save()
#
#     def check_out(self):
#         if self.check_in_time is None:
#             raise InvalidCheckInCheckOutException('Check in time does not exist')
#
#         if self.check_out_time is not None:
#             raise InvalidCheckInCheckOutException(f'User already checked out at {self.check_out_time}')
#
#         self.check_out_time = datetime.datetime.utcnow()
#         self.save()
#
#     def has_checked_in(self):
#         return self.check_in_time is not None
#
#     def has_checked_out(self):
#         return self.check_out_time is not None
#
#     def create_review(self, rating, comment):
#         review = ParticipationVolunteeringReview.objects.create(
#             participation=self,
#             event_rating=rating,
#             event_comment=comment,
#         )
#
#         return review
#
#     def get_has_left_forum(self):
#         return self.has_left_forum
#
#     def set_has_left_forum(self, has_left_forum):
#         self.has_left_forum = has_left_forum
#         self.save()
#
#     def get_review(self):
#         review = ParticipationVolunteeringReview.objects.filter(participation=self)
#         if len(review) > 0:
#             return review[0]
#
#         else:
#             return None
#
#     def delete_participation(self):
#         if self.get_participation_type() == ParticipationType.PARTICIPANT:
#             self.event.decrement_participant()
#
#         if self.get_participation_type() == ParticipationType.VOLUNTEER:
#             self.event.decrement_volunteer()
#
#         self.delete()
#
#
# class EventVolunteerParticipation(EventParticipation):
#     granted_manager_access = models.BooleanField(default=False)
#
#     def get_participation_type(self):
#         return ParticipationType.VOLUNTEER
#
#     def get_granted_manager_access(self):
#         return self.granted_manager_access
#
#     def set_as_manager(self):
#         if self.check_in_time is None:
#             raise InvalidCheckInCheckOutException('User must check in before being granted a managerial role')
#
#         self.granted_manager_access = True
#         self.save()
#
#
class ProjectContribution:
    pass


#     event = models.ForeignKey('event.Project', on_delete=models.CASCADE)
#     contributor = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
#
#     contribution_time = models.DateTimeField(auto_now=True)
#     has_left_forum = models.BooleanField(default=False)
#
#     def create_review(self, rating, comment):
#         return ContributionReview.objects.create(
#             contribution=self,
#             event_rating=rating,
#             event_comment=comment,
#         )
#
#     def get_review(self):
#         review = ContributionReview.objects.filter(contribution=self)
#         if len(review) > 0:
#             return review[0]
#
#         else:
#             return None


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


# class BaseEventParticipationSerializer(serializers.ModelSerializer):
#     def to_representation(self, event_participation):
#         serialized_data = EventParticipationSerializer(event_participation).data
#         if isinstance(event_participation, EventVolunteerParticipation):
#             serialized_data['granted_manager_access'] = event_participation.get_granted_manager_access()
#
#         return serialized_data
#
#     class Meta:
#         model = EventParticipation
#         fields = '__all__'


class ProjectContributionSerializer(serializers.ModelSerializer):
    event_data = serializers.SerializerMethodField(method_name='get_event_data')

    def get_event_data(self, event_participation):
        return BaseEventSerializer(event_participation.event).data

    class Meta:
        model = ProjectContribution
        fields = [
            'event_data',
            'contribution_time',
            'contributor',
            'has_left_forum',
        ]
