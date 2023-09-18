from django.urls import path
from .views import (
    serve_create_event,
    serve_get_all_tags,
    serve_get_event_by_id,
    serve_get_event_image_by_id,
    serve_get_nearby_events,
    serve_get_or_create_tags,
    serve_search_events,
)


urlpatterns = [
    path('create/', serve_create_event),
    path('detail/<str:event_id>/', serve_get_event_by_id),
    path('discover/nearby/', serve_get_nearby_events),
    path('image/<str:event_id>', serve_get_event_image_by_id),
    path('search/', serve_search_events),
    path('tags/', serve_get_all_tags),
    path('tags/get-or-create/multiple/', serve_get_or_create_tags),
]
