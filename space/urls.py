from django.urls import path
from .views import (
    serve_get_all_locations,
    serve_get_or_create_location,
    serve_get_nearby_non_subscribed_locations,
    serve_subscribe_or_neglect_location
)

urlpatterns = [
    path('all/', serve_get_all_locations),
    path('get-or-create/', serve_get_or_create_location),
    path('nearby/nonsubscribed/', serve_get_nearby_non_subscribed_locations),
    path('preference/update/', serve_subscribe_or_neglect_location),
]
