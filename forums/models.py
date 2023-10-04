import uuid
from django.db import models
from rest_framework import serializers
from event.models import Event

class Forum(models.Model):
    id = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4)
    event = models.ForeignKey('event.Event', on_delete=models.CASCADE)

class ForumPost(models.Model):
    content = models.TextField()
    author = models.ForeignKey('users.User', on_delete=models.CASCADE)
    forum = models.ForeignKey('forums.Forum', on_delete=models.CASCADE)
    posted_at = models.DateTimeField(auto_now_add=True)
    is_anonymous = models.BooleanField(default=False)
    vote_count = models.IntegerField(default=0)
    upvoters = models.ManyToManyField('users.User', related_name="upvoted_posts")
    downvoters = models.ManyToManyField('users.User', related_name="downvoted_posts")


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'name', 'start_date', 'end_date', 'location']

class ForumSerializer(serializers.ModelSerializer):
    event_name = serializers.ReadOnlyField(source='event.name')
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Forum
        fields = ['id', 'event', 'event_name', 'type_display']

class ForumPostSerializer(serializers.ModelSerializer):
    forum_title = serializers.ReadOnlyField(source='forum.title')
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = ForumPost
        fields = ['id', 'content', 'author_name', 'forum', 'forum_title', 'posted_at', 'is_anonymous', 'vote_count']
