from ..models import Forum, ForumPostSerializer
from communalspace.exceptions import InvalidRequestException


def find_trending_posts(request_data):
    if request_data.get("threshold") is not None:
        try:
            int(request_data.get("threshold"))
        except:
            raise InvalidRequestException("'threshold' is not a valid integer")

    threshold = int(request_data.get("threshold")) if request_data.get("threshold") is not None else 20

    all_forums = Forum.objects.all()
    trending_posts = []

    for forum in all_forums:
        posts = ForumPostSerializer(forum.forumpost_set.filter(vote_count__gte=threshold), many=True).data
        if len(posts) > 0:
            trending_posts.append({
                'event_id': forum.event.get_id(),
                'event_name': forum.event.get_name(),
                'event_location_id': forum.event.location.id,
                'event_location_name': forum.event.get_location_name(),
                'forum_top_words': forum.get_forum_top_words(),
                'forum_trending_posts': posts
            })

    return trending_posts
