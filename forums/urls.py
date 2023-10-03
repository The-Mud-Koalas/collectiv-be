from django.urls import path
from .views import (
    serve_create_forum_post,
)


urlpatterns = [
    path('create/', serve_create_forum_post),
]
