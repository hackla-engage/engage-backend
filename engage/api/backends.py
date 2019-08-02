from django.contrib.auth.backends import ModelBackend
from engage.ingest.models import EngageUser
from django.contrib.auth import get_user_model
User = get_user_model()

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
