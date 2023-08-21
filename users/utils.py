from .models import User


def get_or_create_user_by_id(user_id):
    matching_user = User.objects.filter(user_id=user_id)

    if len(matching_user):
        return matching_user[0]

    else:
        return User.objects.create_user(user_id=user_id)
