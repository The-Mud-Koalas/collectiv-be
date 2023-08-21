from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, user_id, **extra_fields):
        if not user_id:
            raise ValueError(_('The User ID must be set'))

        user = self.model(user_id=user_id, **extra_fields)
        user.save()

        return user

    def create_superuser(self, user_id, **extra_fields):
        user = self.create_user(user_id, **extra_fields)
        user.is_staff = True
        user.is_admin = True
        user.is_superuser = True
        user.save()

        return user


