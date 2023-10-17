from django.views.decorators.http import require_POST, require_GET
from django.db import transaction
from communalspace.decorators import firebase_authenticated
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import ForumPostSerializer, Forum
from .services import create_post
import json

from .services.forum_auth import check_authorization
from .services.vote_post import upvote_post, downvote_post
from .services.range_find_post import find_post_in_range
from .services.forum_analytics import get_forum_analytics
from .services.trending_posts import find_trending_posts


@require_POST
@api_view(['POST'])
@firebase_authenticated()
@transaction.atomic()
def serve_create_forum_post(request, event_id):
    """
    This view serves as the endpoint to create a forum post.
    ----------------------------------------------------------
    request-data must contain:
    event_id: UUID string
    content: string
    anonymous: boolean

    * The user information will be taken from the firebase authentication.
    """
    request_data = json.loads(request.body.decode('utf-8'))
    created_post = create_post.handle_create_forum_post(request_data, request.user, event_id)
    response_data = ForumPostSerializer(created_post).data
    return Response(data=response_data)


@require_POST
@api_view(['POST'])
@firebase_authenticated()
@transaction.atomic()
def upvote_forum_post(request, event_id):
    """
    This view serves as the endpoint to upvote a forum post.
    ----------------------------------------------------------
    request-data must contain:
    post_id: UUID string

    * The user information will be taken from the firebase authentication.
    """
    user_id = request.user
    request_data = json.loads(request.body.decode('utf-8'))

    if not check_authorization(user_id, event_id):
        return Response({"error": "User not authorized to upvote post"}, status=403)

    else:
        updated_post = upvote_post(request_data.get('post_id'), user_id)
        response_data = ForumPostSerializer(updated_post).data
        return Response(data=response_data)


@require_POST
@api_view(['POST'])
@firebase_authenticated()
@transaction.atomic()
def downvote_forum_post(request, event_id):
    """
    This view serves as the endpoint to downvote a forum post.
    ----------------------------------------------------------
    request-data must contain:
    post_id: UUID string

    * The user information will be taken from the firebase authentication.
    """
    user_id = request.user
    request_data = json.loads(request.body.decode('utf-8'))

    if not check_authorization(user_id, event_id):
        return Response({"error": "User not authorized to downvote post"}, status=403)
    else:
        updated_post = downvote_post(request_data.get('post_id'), user_id)
        response_data = ForumPostSerializer(updated_post).data
        return Response(data=response_data)


@require_GET
@api_view(['GET'])
@firebase_authenticated()
@transaction.atomic()
def get_forum_posts_by_event(request, event_id):
    """
    This view serves as the endpoint to get all forum posts for an event.
    ----------------------------------------------------------
    request-data must contain:
    event_id: UUID string

    * The user information will be taken from the firebase authentication.
    """
    user_id = request.user

    if not check_authorization(user_id, event_id):
        return Response({"error": "User not authorized to view forum"}, status=403)
    else:
        forum = Forum.objects.get(event_id=event_id)
        posts = forum.forumpost_set.all()
        response_data = ForumPostSerializer(posts, many=True).data
        return Response(data=response_data)


@require_GET
@api_view(['GET'])
@firebase_authenticated()
def get_forum_posts_by_event_and_range(request, event_id):
    """
    This view serves as the endpoint to get all forum posts for an event
    in a certain time range
    ----------------------------------------------------------
    request-data must contain:
    event_id: UUID string

    * The user information will be taken from the firebase authentication.
    """
    posts = find_post_in_range(request.GET, request.user, event_id)
    response_data = ForumPostSerializer(posts, many=True).data
    return Response(data=response_data)


@require_GET
@api_view(['GET'])
def serve_get_forum_analytics(request, event_id):
    analytics = get_forum_analytics(event_id)
    return Response(data=analytics)


@require_GET
@api_view(['GET'])
def server_get_global_forum_posts(request):
    posts = find_trending_posts(request.GET)
    return Response(data=posts)
