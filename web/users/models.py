from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    ユーザー
    """
    webhook_url = models.URLField(max_length=500, blank=True, null=True)
