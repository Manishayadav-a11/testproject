from django.contrib import admin
from .models import Instructor


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'branch', 'license_number', 'experience_years',
        'is_available', 'female_instructor', 'average_rating', 'created_at',
    ]
    list_filter = ['is_available', 'female_instructor', 'branch', 'experience_years']
    search_fields = ['user__first_name', 'user__last_name', 'license_number']
    readonly_fields = ['average_rating', 'total_reviews', 'created_at', 'updated_at']
