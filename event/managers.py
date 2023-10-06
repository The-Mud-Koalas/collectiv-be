from .choices import EventStatus
from polymorphic.managers import PolymorphicManager


class EventManager(PolymorphicManager):
    def filter_active(self):
        return self.filter(status__in=(EventStatus.SCHEDULED, EventStatus.ON_GOING))
