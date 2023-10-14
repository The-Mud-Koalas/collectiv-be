from .views import serve_submit_event_report
from django.urls import path


urlpatterns = [
    path('submit/', serve_submit_event_report),
]