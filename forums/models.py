from communalspace import utils as app_utils
from django.db import models
from rest_framework import serializers
from event.models import Event
import uuid
from event.choices import ParticipationType


class Forum(models.Model):
    id = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4)
    event = models.ForeignKey('event.Event', on_delete=models.CASCADE)

    average_sentiment_score = models.FloatField(default=None, null=True)
    number_of_post_sentiment_calculated = models.PositiveIntegerField(default=0)

    top_words = models.JSONField(default=dict)

    def get_event(self) -> Event:
        return self.event

    def update_average_forum_sentiment_score(self, new_sentiment_score):
        self.average_sentiment_score = app_utils.update_average(
            new_sentiment_score,
            self.average_sentiment_score,
            self.number_of_post_sentiment_calculated
        )
        self.number_of_post_sentiment_calculated += 1
        self.save()
        return self.average_sentiment_score

    def get_average_forum_sentiment_score(self):
        return self.average_sentiment_score

    def update_forum_top_words(self, named_entities):
        for named_entity in named_entities:
            entity_group_label = named_entity['entity_group']
            entity_group = self.top_words.setdefault(entity_group_label, [])
            entity_exists_in_group = False
            for existing_entity in entity_group:
                if existing_entity.get('word').lower() == named_entity.get('word').lower():
                    existing_entity['count'] += 1
                    entity_exists_in_group = True
                    break
            if not entity_exists_in_group:
                entity_group.append({'word': named_entity.get('word').lower(), 'count': 1})

        self.save()

    def get_forum_top_words(self):
        return self.top_words

    def create_post(self, content, author, author_role, sentiment_score, named_entities, is_anonymous=False):
        self.update_average_forum_sentiment_score(sentiment_score)
        self.update_forum_top_words(named_entities)
        return self.forumpost_set.create(
            content=content,
            author=author,
            author_role=author_role,
            is_anonymous=is_anonymous,
            sentiment_score=sentiment_score
        )


class ForumPost(models.Model):
    id = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4)
    content = models.TextField()
    author = models.ForeignKey('users.User', on_delete=models.CASCADE)
    author_role = models.CharField(default=ParticipationType.PARTICIPANT)
    forum = models.ForeignKey('forums.Forum', on_delete=models.CASCADE)
    posted_at = models.DateTimeField(auto_now_add=True)
    is_anonymous = models.BooleanField(default=False)
    vote_count = models.IntegerField(default=0)
    upvoters = models.ManyToManyField('users.User', related_name="upvoted_posts")
    downvoters = models.ManyToManyField('users.User', related_name="downvoted_posts")
    sentiment_score = models.FloatField(default=0)

    @property
    def author_name(self):
        return "Anonymous User" if self.is_anonymous else self.author.full_name


class ForumSerializer(serializers.ModelSerializer):
    event_name = serializers.ReadOnlyField(source='event.name')
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Forum
        fields = [
            'id',
            'event',
            'event_name',
            'type_display'
        ]


class ForumPostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(read_only=True)

    class Meta:
        model = ForumPost
        fields = [
            'id',
            'content',
            'author',
            'author_name',
            'author_role',
            'forum',
            'posted_at',
            'is_anonymous',
            'vote_count',
            'upvoters',
            'downvoters'
        ]
