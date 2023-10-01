from django.urls import path
from .views import (
    serve_participant_volunteer_submit_review,
    serve_contributor_submit_review,
)

urlpatterns = [
    path('participant-volunteer/submit/', serve_participant_volunteer_submit_review),
    path('contributor/submit/', serve_contributor_submit_review),
]