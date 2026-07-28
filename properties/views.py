"""Views for property listing, detail, and search."""

import logging
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, FormView
from django.urls import reverse
from django.contrib import messages
from .models import Property, Category, Location
from .forms import PropertyEnquiryForm, PropertySearchForm

logger = logging.getLogger('realestate')


class PropertyListView(ListView):
    """Property listing page with search, filter, and pagination."""
    model = Property
    template_name = 'properties/property_list.html'
    context_object_name = 'properties'
    paginate_by = 9

    def get_queryset(self):
        queryset = Property.objects.filter(
            is_published=True,
            status='published'
        ).select_related('category').prefetch_related('gallery_images', 'property_videos')

        # Apply search filters
        form = PropertySearchForm(self.request.GET)
        if form.is_valid():
            data = form.cleaned_data

            # Keyword search
            keyword = data.get('keyword')
            if keyword:
                queryset = queryset.filter(
                    Q(title__icontains=keyword) |
                    Q(location__icontains=keyword) |
                    Q(description__icontains=keyword) |
                    Q(city__icontains=keyword) |
                    Q(address__icontains=keyword)
                )

            # Location filter
            location = data.get('location')
            if location:
                location_filters = Q(location__icontains=location.name)
                if location.city:
                    location_filters |= Q(city__icontains=location.city)
                if location.state:
                    location_filters |= Q(state__icontains=location.state)
                queryset = queryset.filter(location_filters)

            # Property type filter
            property_type = data.get('property_type')
            if property_type:
                queryset = queryset.filter(property_type=property_type)

            # Price range filter
            min_price = data.get('min_price')
            if min_price:
                queryset = queryset.filter(price__gte=min_price)

            max_price = data.get('max_price')
            if max_price:
                queryset = queryset.filter(price__lte=max_price)

            # Bedrooms filter
            bedrooms = data.get('bedrooms')
            if bedrooms:
                if bedrooms == '10+':
                    queryset = queryset.filter(bedrooms__gte=10)
                else:
                    queryset = queryset.filter(bedrooms=int(bedrooms))

            # Sorting
            sort_by = data.get('sort_by', 'newest')
            if sort_by == 'price_low':
                queryset = queryset.order_by('price')
            elif sort_by == 'price_high':
                queryset = queryset.order_by('-price')
            else:
                queryset = queryset.order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = PropertySearchForm(self.request.GET)
        context['categories'] = Category.objects.annotate(
            property_count=Count('properties', filter=Q(
                properties__is_published=True,
                properties__status='published'
            ))
        )
        context['locations'] = Location.objects.filter(is_active=True).order_by('name')
        context['meta_title'] = 'Properties - Premium Real Estate'
        context['meta_description'] = 'Browse our collection of premium properties. ' \
                                     'Find apartments, villas, houses, and commercial spaces.'
        return context


class PropertyDetailView(DetailView):
    """Property detail page with gallery, details, and enquiry form."""
    model = Property
    template_name = 'properties/property_detail.html'
    context_object_name = 'property'

    def get_queryset(self):
        return Property.objects.filter(
            is_published=True,
            status='published'
        ).select_related('category').prefetch_related('gallery_images', 'property_videos')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        property_obj = self.get_object()

        # Enquiry form
        context['enquiry_form'] = PropertyEnquiryForm()

        # Related properties (same category or type, excluding current)
        related = Property.objects.filter(
            is_published=True,
            status='published'
        ).exclude(pk=property_obj.pk)

        if property_obj.category:
            related = related.filter(category=property_obj.category)
        else:
            related = related.filter(property_type=property_obj.property_type)

        context['related_properties'] = related.select_related('category')[:3]

        # SEO
        context['meta_title'] = property_obj.meta_title or \
                                f'{property_obj.title} - Premium Real Estate'
        context['meta_description'] = property_obj.meta_description or \
                                      f'{property_obj.title} at {property_obj.location}. ' \
                                      f'Price: {property_obj.formatted_price()}'

        return context


class PropertyEnquiryView(FormView):
    """Handle property enquiry form submission."""
    form_class = PropertyEnquiryForm
    http_method_names = ['post']

    def form_valid(self, form):
        property_obj = get_object_or_404(
            Property,
            pk=self.kwargs.get('pk'),
            is_published=True,
            status='published'
        )

        # Check rate limiting (simple IP-based)
        ip = self.request.META.get('REMOTE_ADDR')
        from .models import PropertyEnquiry
        recent_enquiries = PropertyEnquiry.objects.filter(
            ip_address=ip,
            created_at__gte=timezone.now() - timezone.timedelta(hours=1)
        ).count()
        if recent_enquiries >= 5:
            messages.error(
                self.request,
                'Too many enquiries. Please try again later.'
            )
            return redirect(reverse('properties:detail', kwargs={'slug': property_obj.slug}))

        # Save enquiry with property and request data
        enquiry = form.save(commit=False)
        enquiry.property = property_obj
        enquiry.ip_address = ip
        enquiry.user_agent = self.request.META.get('HTTP_USER_AGENT', '')[:500]
        enquiry.save()

        # Send email notification to admin
        self._send_admin_notification(property_obj, form)

        messages.success(
            self.request,
            'Thank you for your enquiry! We will get back to you shortly.'
        )
        return redirect(reverse('properties:detail', kwargs={'slug': property_obj.slug}))

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        property_obj = get_object_or_404(
            Property,
            pk=self.kwargs.get('pk'),
            is_published=True,
            status='published',
        )
        return redirect(
            reverse('properties:detail', kwargs={'slug': property_obj.slug})
        )

    def _send_admin_notification(self, property_obj, form):
        """Send email notification to admin about new enquiry."""
        try:
            from django.core.mail import send_mail
            from django.conf import settings

            subject = f'New Enquiry: {property_obj.title}'
            message = (
                f'New property enquiry received.\n\n'
                f'Property: {property_obj.title}\n'
                f'Property ID: {property_obj.property_id}\n\n'
                f'From: {form.cleaned_data["name"]}\n'
                f'Email: {form.cleaned_data["email"]}\n'
                f'Phone: {form.cleaned_data["phone"]}\n'
                f'Message: {form.cleaned_data["message"]}\n'
            )
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f'Failed to send enquiry notification: {e}')


# Import at bottom to avoid circular import
from django.utils import timezone
