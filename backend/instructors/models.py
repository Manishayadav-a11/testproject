from django.db import models
from accounts.models import User


class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='instructor_profile')
    branch = models.ForeignKey(
        'branches.Branch', on_delete=models.CASCADE, related_name='instructors'
    )
    license_number = models.CharField(max_length=50, blank=True, default='')
    experience_years = models.PositiveIntegerField(default=0)
    languages = models.JSONField(default=list, blank=True)
    bio = models.TextField(blank=True, default='')
    is_available = models.BooleanField(default=True)
    home_pickup_available = models.BooleanField(default=False)
    female_instructor = models.BooleanField(default=False)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.branch.name}"
