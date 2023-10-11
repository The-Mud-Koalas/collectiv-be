from .views import (
    serve_get_complete_event_analytics,
    serve_get_total_participants_of_events_in_location
)
from django.urls import path

urlpatterns = [
    path('event/<str:event_id>/', serve_get_complete_event_analytics),
    path('space/<str:location_id>/', serve_get_total_participants_of_events_in_location),
]
