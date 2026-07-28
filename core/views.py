"""Core views for homepage, about page, and other static pages."""

import logging
from django.shortcuts import render
from django.views.generic import TemplateView
from properties.models import Property, Category, Location
from core.models import SiteSettings

logger = logging.getLogger('realestate')


class HomePageView(TemplateView):
    """Homepage view with featured properties and categories."""
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_properties'] = Property.objects.filter(
            is_featured=True,
            is_published=True,
            status='published'
        ).select_related('category')[:6]
        context['latest_properties'] = Property.objects.filter(
            is_published=True,
            status='published'
        ).select_related('category')[:6]
        context['categories'] = Category.objects.all()
        context['locations'] = Location.objects.filter(is_active=True).order_by('name')
        context['meta_title'] = 'Premium Real Estate - Find Your Dream Property'
        context['meta_description'] = 'Discover premium properties across prime locations. ' \
                                     'Apartments, villas, houses, and commercial spaces.'
        return context


class AboutPageView(TemplateView):
    """About us page view."""
    template_name = 'core/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meta_title'] = 'About Us - Premium Real Estate'
        context['meta_description'] = 'Learn about Premium Real Estate, our mission, vision, ' \
                                     'and experience in the real estate industry.'
        context['site_settings'] = SiteSettings.objects.first()
        return context


# Error handlers
def handler404(request, exception):
    """404 page not found handler."""
    logger.warning(f'404 Not Found: {request.path}')
    return render(request, 'errors/404.html', status=404)


def handler500(request):
    """500 server error handler."""
    logger.error(f'500 Server Error: {request.path}')
    return render(request, 'errors/500.html', status=500)


def handler403(request, exception):
    """403 forbidden handler."""
    logger.warning(f'403 Forbidden: {request.path}')
    return render(request, 'errors/403.html', status=403)
