from django.db import models

# Create your models here.
from rest_framework import serializers

from event.models import BaseEventSerializer, Event


class InitiativeAnalyticsSerializer(serializers.ModelSerializer):
    @staticmethod
    def get_participants_average_attendance_duration(initiative):
        return initiative.get_participants_average_attendance_duration()

    @staticmethod
    def get_event_rating(event):
        return event.get_event_average_rating()

    @staticmethod
    def get_registration_history(event):
        return [
            {**day_data, 'registration_date': day_data['registration_date']}
            for day_data
            in event.get_event_registration_per_day()
        ]

    def to_representation(self, event):
        serialized_data = BaseEventSerializer(event).data
        serialized_data['registration_history'] = self.get_registration_history(event)
        serialized_data['average_rating'] = self.get_event_rating(event)
        serialized_data['average_participant_duration'] = self.get_participants_average_attendance_duration(event)

        return serialized_data

    class Meta:
        model = Event
        fields = '__all__'
