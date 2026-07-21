from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Platform Admin'
        INSTITUTE_OWNER = 'institute_owner', 'Institute Owner'
        INSTRUCTOR = 'instructor', 'Instructor'
        STUDENT = 'student', 'Student'

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, default='')
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    city = models.CharField(max_length=100, blank=True, default='')
    state = models.CharField(max_length=100, blank=True, default='')
    address = models.TextField(blank=True, default='')
    pincode = models.CharField(max_length=10, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN

    @property
    def is_institute_owner(self):
        return self.role == self.Role.INSTITUTE_OWNER

    @property
    def is_instructor_role(self):
        return self.role == self.Role.INSTRUCTOR

    @property
    def is_student_role(self):
        return self.role == self.Role.STUDENT
