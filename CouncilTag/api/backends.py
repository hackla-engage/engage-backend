from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class EmailPasswordBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None
