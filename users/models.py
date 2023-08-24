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

    USERNAME_FIELD = 'user_id'

    objects = UserManager()

    class Meta:
        db_table = 'auth_user'

    def __str__(self):
        return self.user_id

    def set_full_name(self, full_name):
        self.full_name = full_name
        self.save()

    def set_preferred_radius(self, preferred_radius):
        self.preferred_radius = preferred_radius
        self.save()

    def set_location_track(self, location_track):
        self.location_track = location_track
        self.save()

    def get_user_id(self):
        return str(self.user_id)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'user_id',
            'full_name',
            'reward_points',
            'preferred_radius',
            'location_track'
        ]

