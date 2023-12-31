from django.urls import path
from .views import (
    serve_get_all_locations,
    serve_get_or_create_location,
    serve_get_nearby_non_subscribed_locations,
    serve_get_list_of_subscribed_locations,
    serve_subscribe_or_neglect_location,
    serve_get_location_by_id,
    serve_get_location_by_latitude_longitude,
)

urlpatterns = [
    path('all/', serve_get_all_locations),
    path('detail/<str:location_id>/', serve_get_location_by_id),
    path('get-or-create/', serve_get_or_create_location),
    path('get-by-coordinate/', serve_get_location_by_latitude_longitude),
    path('nearby/nonsubscribed/', serve_get_nearby_non_subscribed_locations),
    path('preference/update/', serve_subscribe_or_neglect_location),
    path('subscribed/', serve_get_list_of_subscribed_locations),
]
