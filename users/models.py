from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework import serializers
from .managers import UserManager


class User(AbstractUser):
    username = None
    password = None
    email = None

    last_login = None
    first_name = None
    last_name = None

    user_id = models.CharField(max_length=30, unique=True, primary_key=True)
    full_name = models.CharField(max_length=50, null=True)
    reward_points = models.IntegerField(default=0)
    preferred_radius = models.FloatField(default=2000)
    location_track = models.BooleanField(default=True)

    notified_locations = models.ManyToManyField('space.Location', through='users.NotifiedLocation')
    interests = models.ManyToManyField('event.Tags')

    event_currently_attended = models.ForeignKey('event.Event', on_delete=models.SET_NULL, default=None, null=True)
    currently_attending_role = models.CharField(max_length=15, default=None, null=True)
    initial_location_track_prompt = models.BooleanField(default=False)

    USERNAME_FIELD = 'user_id'

    objects = UserManager()

    class Meta:
        db_table = 'auth_user'

    def __str__(self):
        return self.user_id

    def has_been_prompted_for_location_tracking(self):
        return self.initial_location_track_prompt

    def set_has_been_prompted_for_location_tracking(self, has_been_prompted):
        self.has_been_prompted = has_been_prompted
        self.save()

    def get_currently_attended_event(self):
        return self.event_currently_attended

    def get_currently_attended_event_id(self):
        return self.event_currently_attended.get_id()

    def get_currently_attending_role(self):
        return self.currently_attending_role

    def is_currently_attending_event(self):
        return self.currently_attending_role is not None

    def set_currently_attended_event(self, event):
        self.event_currently_attended = event
        self.save()

    def set_currently_attending_role(self, role):
        self.currently_attending_role = role
        self.save()

    def remove_currently_attended_event(self):
        self.set_currently_attended_event(None)
        self.set_currently_attending_role(None)

    def add_reward(self, amount):
        self.reward_points += amount
        self.save()

    def set_full_name(self, full_name):
        self.full_name = full_name
        self.save()

    def set_preferred_radius(self, preferred_radius):
        self.preferred_radius = preferred_radius
        self.save()

    def set_location_track(self, location_track):
        self.location_track = location_track
        self.save()

    def add_to_notified_locations(self, location, is_subscribe):
        existing_notified_location = self._get_notified_location_objects().filter(location=location)
        if not existing_notified_location.exists():
            NotifiedLocation.objects.create(
                user=self,
                location=location,
                subscribed=is_subscribe
            )

        else:
            existing_notified_location = existing_notified_location[0]
            existing_notified_location.update_subscription(is_subscribe)

    def _get_notified_location_objects(self):
        return NotifiedLocation.objects.filter(user=self)

    def get_notified_locations(self):
        return list(map(lambda x: x.location, self._get_notified_location_objects()))

    def get_subscribed_locations(self):
        return list(map(lambda n: n.location, self._get_notified_location_objects().filter(subscribed=True)))

    def get_user_id(self):
        return str(self.user_id)

    def get_interests(self):
        return self.interests.all()

    def get_preferred_radius(self):
        return self.preferred_radius

    def set_interests(self, interests):
        self.interests.clear()
        for interest in interests:
            self.interests.add(interest)

    def get_full_name(self):
        return self.full_name

    def get_reward_points(self):
        return self.reward_points

    def redeem_reward(self, amount_of_points_to_be_redeemed):
        if amount_of_points_to_be_redeemed > self.reward_points:
            raise ValueError("Amount of points to be redeemed must not exceed owned points")

        self.reward_points -= amount_of_points_to_be_redeemed
        self.save()


class UserSerializer(serializers.ModelSerializer):
    has_been_prompted_for_location_tracking = serializers.SerializerMethodField(
        method_name='get_has_been_prompted_for_location_tracking'
    )

    def get_has_been_prompted_for_location_tracking(self, instance):
        return instance.has_been_prompted_for_location_tracking()

    class Meta:
        model = User
        fields = [
            'user_id',
            'full_name',
            'reward_points',
            'preferred_radius',
            'location_track',
            'has_been_prompted_for_location_tracking',
        ]


class NotifiedLocation(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    location = models.ForeignKey('space.Location', on_delete=models.RESTRICT)
    subscribed = models.BooleanField(default=False)

    def update_subscription(self, subscribed):
        self.subscribed = subscribed
        self.save()

