from django.urls import path
from .views import serve_create_event, serve_get_all_tags


urlpatterns = [
    path('create/', serve_create_event),
    path('tags/', serve_get_all_tags),
]
