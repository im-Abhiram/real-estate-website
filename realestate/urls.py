"""Main URL configuration for realestate project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import GenericSitemap
from properties.models import Property


def superuser_admin_permission(request):
    """Limit Django's administrative interface to superusers."""
    return request.user.is_active and request.user.is_superuser


admin.site.has_permission = superuser_admin_permission

# Sitemap configuration
property_sitemap = {
    'queryset': Property.objects.filter(is_published=True, status='published'),
    'date_field': 'updated_at',
}

sitemaps = {
    'properties': GenericSitemap(property_sitemap, priority=0.8, changefreq='daily'),
}

# Get admin URL from settings (for security, avoid default /admin/)
admin_url = getattr(settings, 'ADMIN_URL', 'admin/')

urlpatterns = [
    # Admin site with customizable URL
    path(admin_url, admin.site.urls),

    # Apps
    path('', include('core.urls')),
    path('properties/', include('properties.urls')),
    path('contact/', include('contact.urls')),
    path('dashboard/', include('dashboard.urls')),

    # Authentication
    path('accounts/', include('allauth.urls')),

    # SEO
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(
        template_name='robots.txt',
        content_type='text/plain'
    )),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)

# Custom error handlers
handler404 = 'core.views.handler404'
handler500 = 'core.views.handler500'
handler403 = 'core.views.handler403'
