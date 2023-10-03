from django.db import models
from django.contrib.auth.models import User
from rest_framework import serializers

from event.models import Event
from eventforum.models import Forum, ForumType


class ForumPost(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE)
    posted_at = models.DateTimeField(auto_now_add=True)
    is_anonymous = models.BooleanField(default=False)
    likes_count = models.PositiveIntegerField(default=0)
    reports_count = models.PositiveIntegerField(default=0)

class Like(models.Model):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)


class Report(models.Model):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'name', 'start_date', 'end_date', 'location']

class ForumSerializer(serializers.ModelSerializer):
    event_name = serializers.ReadOnlyField(source='event.name')
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Forum
        fields = ['id', 'event', 'event_name', 'type', 'type_display']

    def validate_type(self, value):
        if value not in ForumType.values:
            raise serializers.ValidationError(f"Type must be one of: {', '.join(ForumType.values)}")
        return value



class ForumPostSerializer(serializers.ModelSerializer):
    forum_title = serializers.ReadOnlyField(source='forum.title')
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = ForumPost
        fields = ['id', 'content', 'author_name', 'forum', 'forum_title', 'posted_at', 'is_anonymous', 'likes_count', 'reports_count']



class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'post', 'user', 'timestamp']


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'post', 'user', 'reason', 'timestamp']