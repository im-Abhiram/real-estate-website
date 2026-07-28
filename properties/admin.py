"""Admin configuration for properties app."""

from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.utils import timezone
from .models import Category, Property, PropertyImage, PropertyVideo, PropertyEnquiry, Location
from .validators import validate_uploaded_image


class PropertyAdminForm(forms.ModelForm):
    """Apply the same file validation in Django Admin as the custom dashboard."""

    class Meta:
        model = Property
        fields = '__all__'

    def clean_cover_image(self):
        image = self.cleaned_data.get('cover_image')
        if image and getattr(image, 'content_type', None):
            validate_uploaded_image(image)
        return image


class PropertyImageInlineForm(forms.ModelForm):
    """Validate inline gallery image uploads before saving them."""

    class Meta:
        model = PropertyImage
        fields = '__all__'

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and getattr(image, 'content_type', None):
            validate_uploaded_image(image)
        return image


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for categories."""
    list_display = ['name', 'slug', 'property_count', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']


class PropertyImageInline(admin.TabularInline):
    """Inline admin for property gallery images."""
    model = PropertyImage
    form = PropertyImageInlineForm
    extra = 1
    fields = ['image', 'alt_text', 'is_featured', 'order']
    readonly_fields = ['created_at']


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    """Admin configuration for properties."""
    list_display = [
        'property_id', 'title', 'category', 'property_type',
        'formatted_price_display', 'location', 'bedrooms',
        'bathrooms', 'status', 'is_featured', 'is_published',
        'created_at'
    ]
    list_filter = [
        'status', 'property_type', 'is_featured', 'is_published',
        'category', 'city', 'created_at'
    ]
    search_fields = [
        'title', 'property_id', 'location', 'description',
        'city', 'address'
    ]
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = [
        'property_id', 'created_at', 'updated_at', 'published_at',
        'cover_image_preview'
    ]
    inlines = [PropertyImageInline]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    form = PropertyAdminForm

    fieldsets = [
        ('Basic Information', {
            'fields': [
                'title', 'slug', 'property_id', 'category',
                'property_type', 'status'
            ]
        }),
        ('Pricing', {
            'fields': ['price', 'price_sqft']
        }),
        ('Location', {
            'fields': [
                'location', 'address', 'city', 'state',
                'zip_code', 'latitude', 'longitude'
            ]
        }),
        ('Property Details', {
            'fields': [
                'description', 'bedrooms', 'bathrooms',
                'area', 'parking', 'year_built', 'amenities'
            ]
        }),
        ('Featured & Publishing', {
            'fields': [
                'is_featured', 'is_published',
                'featured_until', 'published_at'
            ]
        }),
        ('Images', {
            'fields': ['cover_image', 'cover_image_preview']
        }),
        ('SEO', {
            'fields': ['meta_title', 'meta_description']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]

    actions = ['make_published', 'make_draft', 'make_featured', 'make_unfeatured']

    def cover_image_preview(self, obj):
        """Show cover image thumbnail."""
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 300px;" />',
                obj.cover_image.url
            )
        return 'No image'
    cover_image_preview.short_description = 'Cover Image Preview'

    def formatted_price_display(self, obj):
        """Display formatted price in admin."""
        return obj.formatted_price()
    formatted_price_display.short_description = 'Price'
    formatted_price_display.admin_order_field = 'price'

    def make_published(self, request, queryset):
        """Bulk action to publish properties."""
        updated = queryset.update(
            status='published',
            is_published=True,
            published_at=timezone.now()
        )
        self.message_user(request, f'{updated} properties published.')
    make_published.short_description = 'Publish selected properties'

    def make_draft(self, request, queryset):
        """Bulk action to set properties as draft."""
        updated = queryset.update(status='draft', is_published=False)
        self.message_user(request, f'{updated} properties set to draft.')
    make_draft.short_description = 'Set selected properties to draft'

    def make_featured(self, request, queryset):
        """Bulk action to feature properties."""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} properties featured.')
    make_featured.short_description = 'Feature selected properties'

    def make_unfeatured(self, request, queryset):
        """Bulk action to unfeature properties."""
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} properties unfeatured.')
    make_unfeatured.short_description = 'Unfeature selected properties'


@admin.register(PropertyVideo)
class PropertyVideoAdmin(admin.ModelAdmin):
    """Admin configuration for property videos."""
    list_display = ['property', 'video_preview', 'title', 'order', 'created_at']
    list_filter = ['created_at']
    search_fields = ['property__title', 'property__property_id', 'title']
    readonly_fields = ['created_at']

    def video_preview(self, obj):
        """Show video preview in admin."""
        if obj.video:
            return format_html(
                '<video width="200" height="120" controls><source src="{}" type="video/mp4">Preview</video>',
                obj.video.url
            )
        return 'No video'
    video_preview.short_description = 'Video Preview'


@admin.register(PropertyEnquiry)
class PropertyEnquiryAdmin(admin.ModelAdmin):
    """Admin configuration for property enquiries."""
    list_display = [
        'name', 'email', 'phone', 'property', 'is_read',
        'created_at'
    ]
    list_filter = ['is_read', 'created_at']
    search_fields = [
        'name', 'email', 'phone', 'property__title',
        'property__property_id'
    ]
    readonly_fields = [
        'name', 'email', 'phone', 'message', 'property',
        'ip_address', 'user_agent', 'created_at'
    ]
    actions = ['mark_as_read', 'mark_as_unread']
    date_hierarchy = 'created_at'

    def mark_as_read(self, request, queryset):
        """Bulk action to mark enquiries as read."""
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} enquiries marked as read.')
    mark_as_read.short_description = 'Mark selected as read'

    def mark_as_unread(self, request, queryset):
        """Bulk action to mark enquiries as unread."""
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} enquiries marked as unread.')
    mark_as_unread.short_description = 'Mark selected as unread'


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Admin configuration for locations."""
    list_display = ['name', 'slug', 'city', 'state', 'is_active', 'created_at']
    list_filter = ['is_active', 'state', 'city']
    search_fields = ['name', 'city', 'state']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_active']
