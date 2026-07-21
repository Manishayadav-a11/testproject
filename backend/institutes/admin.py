from django.contrib import admin
from .models import Institute


@admin.register(Institute)
class InstituteAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'owner', 'category', 'status', 'is_featured',
        'average_rating', 'total_reviews', 'commission_rate', 'created_at',
    ]
    list_filter = ['status', 'is_featured', 'category']
    search_fields = ['name', 'contact_email', 'license_number', 'owner__email']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['average_rating', 'total_reviews', 'created_at', 'updated_at']
