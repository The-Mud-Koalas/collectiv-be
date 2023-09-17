from django.urls import path
from .views import (
    serve_create_event,
    serve_get_event_by_id,
    serve_get_event_image_by_id,
    serve_get_all_tags,
    serve_update_event
)


urlpatterns = [
    path('create/', serve_create_event),
    path('detail/<str:event_id>/', serve_get_event_by_id),
    path('image/<str:event_id>', serve_get_event_image_by_id),
    path('tags/', serve_get_all_tags),
    path('update/', serve_update_event)
]
