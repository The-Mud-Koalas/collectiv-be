from django.urls import path
from .views import serve_get_or_create_location, serve_get_nearby_non_subscribed_locations

urlpatterns = [
    path('get-or-create/', serve_get_or_create_location),
    path('nearby/nonsubscribed/', serve_get_nearby_non_subscribed_locations),
]
