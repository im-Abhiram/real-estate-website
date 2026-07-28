"""Admin configuration for core models."""

from django.contrib import admin
from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Admin for site settings - only one record should exist."""

    list_display = ['site_name', 'contact_phone', 'contact_email']
    search_fields = ['site_name', 'contact_email']
    fieldsets = (
        ('General', {
            'fields': ('site_name', 'tagline', 'description'),
        }),
        ('Contact details', {
            'fields': ('contact_address', 'contact_phone', 'contact_email'),
        }),
        ('Social media', {
            'fields': ('facebook_url', 'instagram_url', 'youtube_url', 'whatsapp_number'),
        }),
        ('About page', {
            'fields': (
                'about_story_title', 'about_story_content',
                'about_mission_title', 'about_mission_content',
                'about_vision_title', 'about_vision_content',
            ),
        }),
    )

    def has_add_permission(self, request):
        """Prevent adding more than one settings record."""
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Prevent deleting the settings record."""
        return False
