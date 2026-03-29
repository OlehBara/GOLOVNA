from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

UserModel = get_user_model()


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Custom authentication backend to allow users to log in using either their
    username or their email address.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            # We check if the provided 'username' matches either a username or an email
            user = (
                UserModel.objects.filter(
                    Q(username__iexact=username) | Q(email__iexact=username)
                )
                .distinct()
                .first()
            )

            if user and user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            return None
        return None
