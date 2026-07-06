from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    READER = "reader"
    EMPLOYEE = "employee"
    ROLE_CHOICES = [(READER, "Reader"), (EMPLOYEE, "Employee")]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=READER)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


class Reader(models.Model):
    ph_num_validator = RegexValidator(regex=r'^[6-9]\d{9}$', message="Enter a valid 10-digit Indian mobile number.")

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="reader_profile")
    roll_number = models.CharField(max_length=30, unique=True)
    department = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True, validators=[ph_num_validator])
    address = models.TextField(blank=False)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.roll_number})"


class Employee(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="employee_profile")
    employee_id = models.CharField(max_length=30, unique=True)
    designation = models.CharField(max_length=100)
    joining_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.employee_id})"