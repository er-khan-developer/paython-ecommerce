from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class EmailAuthenticate(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Yahan hum maan kar chal rahe hain ki 'username' variable me email aayega
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        return None