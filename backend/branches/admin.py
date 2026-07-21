from django.contrib import admin
from .models import Branch


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'institute', 'city', 'state', 'pincode',
        'contact_number', 'is_active', 'created_at',
    ]
    list_filter = ['is_active', 'state', 'city', 'institute']
    search_fields = ['name', 'address', 'contact_number']
    readonly_fields = ['created_at', 'updated_at']
