"""Context processors for global template context."""

from django.conf import settings
from properties.models import Category, Property
from core.models import SiteSettings


def site_settings(request):
    """Provide global settings and navigation data to all templates."""
    site_settings_obj = SiteSettings.objects.first()

    return {
        'categories': Category.objects.all(),
        'featured_properties': Property.objects.filter(
            is_featured=True,
            is_published=True,
            status='published'
        ).select_related('category')[:6],
        'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY,
        'SITE_NAME': site_settings_obj.site_name if site_settings_obj else 'Royal Trivandrum',
        'SITE_DESCRIPTION': site_settings_obj.description if site_settings_obj else 'Your trusted real estate partner in Trivandrum. Premium properties across Kerala.',
        'SITE_TAGLINE': site_settings_obj.tagline if site_settings_obj else 'Your Trusted Real Estate Partner in Trivandrum',
        'CONTACT_ADDRESS': site_settings_obj.contact_address if site_settings_obj else 'TC 24/1256, MG Road, Statue Junction, Thiruvananthapuram, Kerala - 695001',
        'CONTACT_PHONE': site_settings_obj.contact_phone if site_settings_obj else '+91 471 234 5678',
        'CONTACT_EMAIL': site_settings_obj.contact_email if site_settings_obj else 'info@royaltrivandrum.com',
    }
