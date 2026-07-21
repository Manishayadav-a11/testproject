from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'date_of_birth', 'learner_license_number',
        'emergency_contact_name', 'created_at',
    ]
    search_fields = ['user__first_name', 'user__last_name', 'learner_license_number']
    readonly_fields = ['created_at', 'updated_at']
