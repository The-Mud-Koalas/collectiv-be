from django.views.decorators.http import require_POST, require_GET
from django.db import transaction
from communalspace.decorators import firebase_authenticated
from rest_framework.decorators import api_view
from rest_framework.response import Response
from event.models import Event
from users.models import User
from .models import ForumPostSerializer, Forum
from .services import create_post
import json
from .services.vote_post import upvote_post, downvote_post


def check_authorization(user: User, event_id: str) -> bool:
    """
    This function checks if the user is authorized to perform the action.
    ----------------------------------------------------------
    user: User object
    user_id: UUID string
    event_id: UUID string

    * The user information will be taken from the firebase authentication.
    """
    event = Event.objects.get(pk=event_id)
    attend_event = event.get_all_type_participation_by_participant(user)
    try:
        participation = event.get_all_type_participation_by_participant(user)
        has_left_forum = participation.get_has_left_forum()
    except:
        has_left_forum = True

    if event.creator == user:
        print("Creator")
        return True

    if attend_event is not None and has_left_forum is not True:
        print("Attends event")
        return True

    return False


@require_POST
@api_view(['POST'])
@firebase_authenticated()
@transaction.atomic()
def serve_create_forum_post(request, forum_id):
    """
    This view serves as the endpoint to create a forum post.
    ----------------------------------------------------------
    request-data must contain:
    event_id: UUID string
    content: string
    anonymous: boolean

    * The user information will be taken from the firebase authentication.
    """
    author_id = request.user
    try:
        forum = Forum.objects.get(pk=forum_id)
        event_id = str(forum.event.id)
    except Forum.DoesNotExist:
        return Response({"error": "Forum not found"}, status=404)

    request_data = json.loads(request.body.decode('utf-8'))
    if not check_authorization(author_id, event_id):
        return Response({"error": "User not authorized to create post"}, status=403)
    else:
        created_post = create_post.handle_create_forum_post(request_data, author_id, forum_id)
        response_data = ForumPostSerializer(created_post).data
        return Response(data=response_data)


@require_POST
@api_view(['POST'])
@firebase_authenticated()
@transaction.atomic()
def upvote_forum_post(request, post_id):
    """
    This view serves as the endpoint to upvote a forum post.
    ----------------------------------------------------------
    request-data must contain:
    post_id: UUID string

    * The user information will be taken from the firebase authentication.
    """
    user_id = request.user

    if not check_authorization(user_id, post_id):
        return Response({"error": "User not authorized to upvote post"}, status=403)

    else:
        updated_post = upvote_post(post_id, user_id)
        response_data = ForumPostSerializer(updated_post).data
        return Response(data=response_data)


@require_POST
@api_view(['POST'])
@firebase_authenticated()
@transaction.atomic()
def downvote_forum_post(request, post_id):
    """
    This view serves as the endpoint to downvote a forum post.
    ----------------------------------------------------------
    request-data must contain:
    post_id: UUID string

    * The user information will be taken from the firebase authentication.
    """
    user_id = request.user

    if not check_authorization(user_id, post_id):
        return Response({"error": "User not authorized to downvote post"}, status=403)
    else:
        updated_post = downvote_post(post_id, user_id)
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
