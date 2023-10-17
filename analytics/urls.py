from .views import (
    serve_get_complete_event_analytics,
    serve_get_total_participants_of_events_in_location,
    serve_get_progresses_of_projects_in_location,
    serve_get_ratings_of_all_events_in_location,
    serve_get_sentiment_of_all_events_in_location,
    serve_get_location_event_count,
)
from django.urls import path

urlpatterns = [
    path('event/<str:event_id>/', serve_get_complete_event_analytics),
    path('space/participation-count/<str:location_id>/', serve_get_total_participants_of_events_in_location),
    path('space/project-contributions/<str:location_id>/', serve_get_progresses_of_projects_in_location),
    path('space/event-ratings/<str:location_id>/', serve_get_ratings_of_all_events_in_location),
    path('space/event-sentiments/<str:location_id>/', serve_get_sentiment_of_all_events_in_location),
    path('space/event-counts/<str:location_id>/', serve_get_location_event_count),
]
