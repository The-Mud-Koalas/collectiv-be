from django.apps import AppConfig
from apscheduler.triggers.cron import CronTrigger
from communalspace.cron import scheduler


class RewardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reward'

    def ready(self):
        from reward.scheduled_tasks import reset_user_points
        scheduler.add_job(reset_user_points, CronTrigger.from_crontab('0 0 1 * *'))
        scheduler.start()


