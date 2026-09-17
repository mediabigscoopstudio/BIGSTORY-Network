from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=16, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return timezone.now() - self.created_at <= timezone.timedelta(minutes=30)