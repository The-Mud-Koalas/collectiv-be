from django.db import transaction
from users.models import User


@transaction.atomic()
def reset_user_points():
    users = User.objects.all().select_for_update()
    for user in users:
        user.reset_monthly_point()
