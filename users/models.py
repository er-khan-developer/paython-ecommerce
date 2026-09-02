import pyotp
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    totp_secret = models.CharField(max_length=32, blank=True, null=True)
    is_2fa_enabled = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Agar secret code nahi hai, toh automatically naya generate karein
        if not self.totp_secret:
            self.totp_secret = pyotp.random_base32()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Profile of {self.user.email}"