from django.urls import path
from .views import (
    serve_create_forum_post, upvote_forum_post, downvote_forum_post,
)


urlpatterns = [
    path('<str:forum_id>/post/', serve_create_forum_post),
    path('<str:post_id>/upvote/', upvote_forum_post),
    path('<str:post_id>/downvote/', downvote_forum_post),
]
