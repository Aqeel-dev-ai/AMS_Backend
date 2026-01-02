from django.db import models


class AttendanceStatus(models.TextChoices):
    PRESENT = "present", "Present"
    ABSENT = "absent", "Absent"
    BREAK = "break", "Break"
    LEAVE = "leave", "Leave"
    OFFLINE = "offline", "Offline"

class UserRole(models.TextChoices):
    ADMIN = "admin", "Admin"
    TEAM_LEAD = "team_lead", "Team Lead"
    EMPLOYEE = "employee", "Employee"


class UserDesignation(models.TextChoices):
    FRONTEND_DEV = "frontend_dev", "Frontend Developer"
    BACKEND_DEV = "backend_dev", "Backend Developer"
    FULLSTACK_DEV = "fullstack_dev", "Full Stack Developer"
    MOBILE_DEV = "mobile_dev", "Mobile Developer"
    UI_UX_DESIGNER = "ui_ux_designer", "UI/UX Designer"
    PROJECT_MANAGER = "project_manager", "Project Manager"
    HR = "hr", "HR"
    QA = "qa", "Quality Assurance"
    DEVOPS = "devops", "DevOps Engineer"

class LeaveType(models.TextChoices):
    CASUAL = "casual", "Casual"
    SICK = "sick", "Sick"

class LeaveStatus(models.TextChoices):  
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"