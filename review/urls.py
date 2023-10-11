from django.urls import path
from .views import (
    serve_submit_review,
)

urlpatterns = [
    path('submit/', serve_submit_review),
]
