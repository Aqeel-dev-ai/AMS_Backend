from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from accounts.manager import UserManager
from accounts.enum import UserRole

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(
        max_length=50,
        choices=UserRole.choices,
    )
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(default=timezone.now)
    objects = UserManager()

    def __str__(self):
        return self.email

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'role']
