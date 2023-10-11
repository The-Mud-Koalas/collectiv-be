from django.urls import path
from .views import (
    serve_get_user_data,
    serve_get_user_interests,
    serve_subscribe_to_tags,
    serve_update_user_data,
    serve_get_user_current_event,
    serve_update_user_prompted_location_tracking
)


urlpatterns = [
    path('data/', serve_get_user_data),
    path('update/', serve_update_user_data),
    path('interests/', serve_get_user_interests),
    path('interests/update/', serve_subscribe_to_tags),
    path('current-event/', serve_get_user_current_event),
    path('location-prompt-status/update/', serve_update_user_prompted_location_tracking),
]
