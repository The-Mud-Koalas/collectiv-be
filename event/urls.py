from django.urls import path
from .views import serve_create_event


urlpatterns = [
    path('create/', serve_create_event),
]
