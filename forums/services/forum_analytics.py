from event.services import utils
from forums.models import Forum


def get_forum_analytics(event_id):
    event = utils.get_event_by_id_or_raise_exception(event_id)
    forum: Forum = event.get_or_create_forum()

    top_words = forum.get_forum_top_words()
    sentiment_score = forum.get_average_forum_sentiment_score()

    return {"top_words": top_words, "sentiment_score": sentiment_score}

