import uuid

from django.db.models.signals import post_save
from django.dispatch import receiver
from event.models import Event
from .models import Forum


@receiver(post_save, sender=Event)
def create_forum_for_new_event(sender, instance, created, **kwargs):
    if created:
        Forum.objects.create(id=uuid.uuid4(), event=instance)
