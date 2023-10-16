from django.urls import path
from .views import (
    serve_create_forum_post, upvote_forum_post, downvote_forum_post, get_forum_posts_by_event, get_forum_posts_by_event_and_range, serve_get_forum_analytics
)


urlpatterns = [
    path('<str:event_id>/post/', serve_create_forum_post),
    path('<str:event_id>/upvote/', upvote_forum_post),
    path('<str:event_id>/downvote/', downvote_forum_post),
    path('<str:event_id>/list/', get_forum_posts_by_event),
    path('<str:event_id>/list/range/', get_forum_posts_by_event_and_range),
    path('<str:event_id>/analytics/', serve_get_forum_analytics)
]
