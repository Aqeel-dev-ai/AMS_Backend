from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, username=None, password=None, **extra_fields):
        if not email:
            raise ValueError("Email field is required")
        if not username:
            raise ValueError("Username field is required")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)

        return user

    def create_superuser(self, email, username=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email=email, username=username, password=password, **extra_fields)
