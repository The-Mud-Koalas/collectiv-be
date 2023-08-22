from django.urls import path
from .views import serve_get_or_create_location

urlpatterns = [
    path('get-or-create/', serve_get_or_create_location),
]
