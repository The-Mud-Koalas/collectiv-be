from ..models import Forum


def find_trending_posts():
    all_forums = Forum.objects.all()

    trending_posts = {}

    for forum in all_forums:
        trending_posts[forum.id] = {
            'event_id': forum.event.get_id(),
            'event_name': forum.event.get_name(),
            'event_location_name': forum.event.get_location_name(),
            'forum_top_words': forum.get_forum_top_words(),
            'forum_trending_posts': forum.forumpost_set.filter(vote_count__gte=20)
        }

    return trending_posts
