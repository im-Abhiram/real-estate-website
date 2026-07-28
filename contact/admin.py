"""Admin configuration for contact app."""

from django.contrib import admin
from .models import ContactEnquiry


@admin.register(ContactEnquiry)
class ContactEnquiryAdmin(admin.ModelAdmin):
    """Admin configuration for contact enquiries."""
    list_display = ['name', 'email', 'phone', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['name', 'email', 'phone', 'subject', 'message',
                      'ip_address', 'user_agent', 'created_at']
    actions = ['mark_as_read', 'mark_as_unread']
    date_hierarchy = 'created_at'

    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} enquiries marked as read.')
    mark_as_read.short_description = 'Mark selected as read'

    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} enquiries marked as unread.')
    mark_as_unread.short_description = 'Mark selected as unread'