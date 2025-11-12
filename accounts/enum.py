from django.db import models

class UserRole(models.TextChoices):
    ADMIN = "admin", "Admin"
    TEAM_LEAD = "team_lead", "Team Lead"
    EMPLOYEE = "employee", "Employee"