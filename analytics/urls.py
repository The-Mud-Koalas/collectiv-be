from .views import serve_get_event_analytics
from django.urls import path

urlpatterns = [
    path('analytics/', serve_get_event_analytics),
]
