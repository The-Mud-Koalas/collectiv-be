from django.urls import path
from .views import (
    serve_create_forum_post, upvote_forum_post, downvote_forum_post,
)


urlpatterns = [
    path('create/', serve_create_forum_post),
    path('upvote/', upvote_forum_post),
    path('downvote/', downvote_forum_post),
]
