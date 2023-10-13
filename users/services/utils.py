from django.core.exceptions import ObjectDoesNotExist
from users.models import User


def get_or_create_user_by_id(user_id):
    matching_user = User.objects.filter(user_id=user_id)

    if len(matching_user):
        return matching_user[0]

    else:
        return User.objects.create_user(user_id=user_id)


def get_user_by_id_or_raise_exception(user_id):
    matching_user = User.objects.filter(user_id=user_id)

    if len(matching_user):
        return matching_user[0]

    else:
        raise ObjectDoesNotExist(f'User with id {user_id} does not exist')


def get_user_by_id_or_raise_exception_thread_safe(user_id):
    matching_user = User.objects.filter(user_id=user_id).select_for_update()

    if matching_user.exists():
        return matching_user[0]

    else:
        raise ObjectDoesNotExist(f'User with id {user_id} does not exist')
