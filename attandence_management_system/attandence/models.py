from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from datetime import datetime 

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

class Employee(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('employee', 'Employee'),
        ('admin', 'Admin'),
    )

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True)
    position = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='employee')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return self.full_name
class EmployeeAttendance(models.Model):
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('leave', 'Leave'),
    )
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=timezone.now)
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    photo = models.ImageField(upload_to='attendance_photos/', blank=True, null=True)
    is_late = models.BooleanField(default=False)
    is_early_out = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='absent')  # NEW

    def __str__(self):
        return f"{self.employee.full_name} - {self.date} ({self.status})"

    def calculate_status(self):
        from .models import OfficeSettings

        try:
            office_settings = OfficeSettings.objects.latest('created_at')
        except OfficeSettings.DoesNotExist:
            return

        if not self.check_in_time or not self.check_out_time:
            self.status = 'absent'
            return

        check_in_datetime = datetime.combine(self.date, self.check_in_time)
        check_out_datetime = datetime.combine(self.date, self.check_out_time)
        worked_hours = (check_out_datetime - check_in_datetime).total_seconds() / 3600

        office_start_datetime = datetime.combine(self.date, office_settings.working_start_time)
        office_end_datetime = datetime.combine(self.date, office_settings.working_end_time)
        office_total_hours = (office_end_datetime - office_start_datetime).total_seconds() / 3600

        minimum_required_hours = office_total_hours * 0.75

        if worked_hours >= minimum_required_hours:
            self.status = 'present'
        else:
            self.status = 'leave'

    def save(self, *args, **kwargs):
        self.calculate_status()
        super().save(*args, **kwargs)

class OfficeLocation(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    allowed_range_km = models.FloatField(default=1.0)

    def __str__(self):
        return self.name


from django.db import models

class OfficeSettings(models.Model):
    working_start_time = models.TimeField()
    working_end_time = models.TimeField()
    grace_minutes = models.PositiveIntegerField(default=10)  # Example: 10 min grace for late entry
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Office Working Hours Settings"


