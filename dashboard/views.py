"""Dashboard views for admin property management."""

import csv
import logging
from functools import wraps
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import redirect_to_login
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from properties.models import Property, Category, PropertyEnquiry, PropertyImage, PropertyVideo, Location
from properties.validators import validate_uploaded_image, validate_uploaded_video
from contact.models import ContactEnquiry
from core.models import SiteSettings

logger = logging.getLogger('realestate')
security_logger = logging.getLogger('django.security')


def staff_required(view_func):
    """Redirect anonymous users to login and deny non-staff users with HTTP 403."""
    @wraps(view_func)
    @login_required(login_url=reverse_lazy('dashboard:login'))
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            security_logger.warning('Dashboard access denied for user_id=%s path=%s', request.user.pk, request.path)
            raise PermissionDenied('Staff access is required.')
        return view_func(request, *args, **kwargs)
    return wrapped_view


def admin_login_view(request):
    """Custom admin login page with premium design."""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff:
                login(request, user)
                next_url = request.GET.get('next', 'dashboard:home')
                if url_has_allowed_host_and_scheme(next_url, {request.get_host()}, request.is_secure()):
                    return redirect(next_url)
                return redirect('dashboard:home')
            security_logger.warning('Non-staff dashboard login attempt for user_id=%s', user.pk)
            form.add_error(None, 'Invalid credentials.')
        else:
            security_logger.warning('Failed dashboard login attempt from ip=%s', request.META.get('REMOTE_ADDR'))
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {
        'form': form,
        'next': request.GET.get('next', ''),
    })


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to restrict access to staff users only."""

    login_url = reverse_lazy('dashboard:login')
    raise_exception = True

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect_to_login(
                self.request.get_full_path(), self.get_login_url(), self.get_redirect_field_name()
            )
        security_logger.warning(
            'Dashboard access denied for user_id=%s path=%s',
            self.request.user.pk, self.request.path,
        )
        raise PermissionDenied('Staff access is required.')


class DashboardHomeView(StaffRequiredMixin, TemplateView):
    """Dashboard home with statistics overview."""
    template_name = 'dashboard/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_properties'] = Property.objects.count()
        context['published_properties'] = Property.objects.filter(
            status='published', is_published=True
        ).count()
        context['featured_properties'] = Property.objects.filter(is_featured=True).count()
        context['draft_properties'] = Property.objects.filter(status='draft').count()
        context['total_enquiries'] = PropertyEnquiry.objects.count()
        context['unread_enquiries'] = PropertyEnquiry.objects.filter(is_read=False).count()
        context['total_contact_enquiries'] = ContactEnquiry.objects.count()
        context['unread_contact_enquiries'] = ContactEnquiry.objects.filter(is_read=False).count()
        context['recent_properties'] = Property.objects.all().select_related('category')[:5]
        context['recent_enquiries'] = PropertyEnquiry.objects.all().select_related('property')[:5]
        return context


class PropertyListView(StaffRequiredMixin, ListView):
    """Dashboard property list view."""
    model = Property
    template_name = 'dashboard/property_list.html'
    context_object_name = 'properties'
    paginate_by = 20

    def get_queryset(self):
        return Property.objects.all().select_related('category').order_by('-created_at')


class PropertyCreateView(StaffRequiredMixin, CreateView):
    """Dashboard create property view."""
    model = Property
    template_name = 'dashboard/property_form.html'
    fields = [
        'title', 'category', 'property_type', 'status',
        'price', 'price_sqft',
        'location', 'address', 'city', 'state', 'zip_code',
        'description', 'bedrooms', 'bathrooms', 'area', 'parking', 'year_built',
        'amenities', 'is_featured', 'is_published',
        'cover_image',
        'meta_title', 'meta_description',
    ]
    success_url = reverse_lazy('dashboard:property_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['property_types'] = Property.PropertyType.choices
        context['status_choices'] = Property.Status.choices
        context['locations'] = Location.objects.filter(is_active=True).order_by('name')
        return context

    def form_valid(self, form):
        gallery_images = self.request.FILES.getlist('gallery_images')
        property_videos = self.request.FILES.getlist('property_videos')
        try:
            cover_image = self.request.FILES.get('cover_image')
            if cover_image:
                validate_uploaded_image(cover_image)
            for image in gallery_images:
                validate_uploaded_image(image)
            for video in property_videos:
                validate_uploaded_video(video)
        except ValidationError as error:
            form.add_error(None, error)
            return self.form_invalid(form)
        response = super().form_valid(form)
        property_obj = form.instance

        for img in gallery_images:
            PropertyImage.objects.create(property=property_obj, image=img)

        for video in property_videos:
            PropertyVideo.objects.create(property=property_obj, video=video)

        messages.success(self.request, 'Property created successfully!')
        return response


class PropertyUpdateView(StaffRequiredMixin, UpdateView):
    """Dashboard update property view."""
    model = Property
    template_name = 'dashboard/property_form.html'
    fields = [
        'title', 'category', 'property_type', 'status',
        'price', 'price_sqft',
        'location', 'address', 'city', 'state', 'zip_code',
        'description', 'bedrooms', 'bathrooms', 'area', 'parking', 'year_built',
        'amenities', 'is_featured', 'is_published',
        'cover_image',
        'meta_title', 'meta_description',
    ]
    success_url = reverse_lazy('dashboard:property_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['property_types'] = Property.PropertyType.choices
        context['status_choices'] = Property.Status.choices
        context['locations'] = Location.objects.filter(is_active=True).order_by('name')
        return context

    def form_valid(self, form):
        gallery_images = self.request.FILES.getlist('gallery_images')
        property_videos = self.request.FILES.getlist('property_videos')
        try:
            cover_image = self.request.FILES.get('cover_image')
            if cover_image:
                validate_uploaded_image(cover_image)
            for image in gallery_images:
                validate_uploaded_image(image)
            for video in property_videos:
                validate_uploaded_video(video)
        except ValidationError as error:
            form.add_error(None, error)
            return self.form_invalid(form)
        response = super().form_valid(form)
        property_obj = form.instance

        for img in gallery_images:
            PropertyImage.objects.create(property=property_obj, image=img)

        for video in property_videos:
            PropertyVideo.objects.create(property=property_obj, video=video)

        messages.success(self.request, 'Property updated successfully!')
        return response


class PropertyDeleteView(StaffRequiredMixin, DeleteView):
    """Dashboard delete property view."""
    model = Property
    template_name = 'dashboard/property_confirm_delete.html'
    success_url = reverse_lazy('dashboard:property_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Property deleted successfully!')
        return super().delete(request, *args, **kwargs)


class EnquiryListView(StaffRequiredMixin, ListView):
    """Dashboard enquiries list view."""
    model = PropertyEnquiry
    template_name = 'dashboard/enquiry_list.html'
    context_object_name = 'enquiries'
    paginate_by = 20

    def get_queryset(self):
        queryset = PropertyEnquiry.objects.all().select_related('property')

        # Search functionality
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) |
                models.Q(email__icontains=search) |
                models.Q(phone__icontains=search) |
                models.Q(property__title__icontains=search) |
                models.Q(property__property_id__icontains=search)
            )

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


class EnquiryDeleteView(StaffRequiredMixin, DeleteView):
    """Dashboard delete enquiry view."""
    model = PropertyEnquiry
    template_name = 'dashboard/enquiry_confirm_delete.html'
    success_url = reverse_lazy('dashboard:enquiry_list')


@staff_required
def export_enquiries_csv(request):
    """Export enquiries to CSV file."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="enquiries.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Date', 'Property ID', 'Property Title', 'Name',
        'Email', 'Phone', 'Message', 'Status'
    ])

    enquiries = PropertyEnquiry.objects.all().select_related('property')
    for enquiry in enquiries:
        writer.writerow([
            enquiry.created_at.strftime('%Y-%m-%d %H:%M'),
            enquiry.property.property_id,
            enquiry.property.title,
            enquiry.name,
            enquiry.email,
            enquiry.phone,
            enquiry.message,
            'Read' if enquiry.is_read else 'Unread'
        ])

    return response


@staff_required
def site_settings_view(request):
    """Edit site settings / contact details."""
    settings_obj = SiteSettings.objects.first()
    if not settings_obj:
        settings_obj = SiteSettings.objects.create()

    if request.method == 'POST':
        settings_obj.site_name = request.POST.get('site_name', settings_obj.site_name)
        settings_obj.tagline = request.POST.get('tagline', settings_obj.tagline)
        settings_obj.description = request.POST.get('description', settings_obj.description)
        settings_obj.contact_address = request.POST.get('contact_address', settings_obj.contact_address)
        settings_obj.contact_phone = request.POST.get('contact_phone', settings_obj.contact_phone)
        settings_obj.contact_email = request.POST.get('contact_email', settings_obj.contact_email)
        settings_obj.facebook_url = request.POST.get('facebook_url', settings_obj.facebook_url)
        settings_obj.instagram_url = request.POST.get('instagram_url', settings_obj.instagram_url)
        settings_obj.youtube_url = request.POST.get('youtube_url', settings_obj.youtube_url)
        settings_obj.whatsapp_number = request.POST.get('whatsapp_number', settings_obj.whatsapp_number)
        
        # About page content
        settings_obj.about_story_title = request.POST.get('about_story_title', settings_obj.about_story_title)
        settings_obj.about_story_content = request.POST.get('about_story_content', settings_obj.about_story_content)
        settings_obj.about_mission_title = request.POST.get('about_mission_title', settings_obj.about_mission_title)
        settings_obj.about_mission_content = request.POST.get('about_mission_content', settings_obj.about_mission_content)
        settings_obj.about_vision_title = request.POST.get('about_vision_title', settings_obj.about_vision_title)
        settings_obj.about_vision_content = request.POST.get('about_vision_content', settings_obj.about_vision_content)
        
        settings_obj.save()
        messages.success(request, 'Site settings updated successfully!')
        return redirect('dashboard:site_settings')

    return render(request, 'dashboard/site_settings.html', {
        'settings': settings_obj,
        'dashboard_title': 'Site Settings'
    })


class CategoryListView(StaffRequiredMixin, ListView):
    """Dashboard categories list view."""
    model = Category
    template_name = 'dashboard/category_list.html'
    context_object_name = 'categories'
    paginate_by = 20

    def get_queryset(self):
        return Category.objects.all().order_by('name')


class CategoryCreateView(StaffRequiredMixin, CreateView):
    """Dashboard create category view."""
    model = Category
    template_name = 'dashboard/category_form.html'
    fields = ['name', 'icon', 'description']
    success_url = reverse_lazy('dashboard:category_list')

    def form_valid(self, form):
        messages.success(self.request, 'Category created successfully!')
        return super().form_valid(form)


class CategoryUpdateView(StaffRequiredMixin, UpdateView):
    """Dashboard update category view."""
    model = Category
    template_name = 'dashboard/category_form.html'
    fields = ['name', 'icon', 'description']
    success_url = reverse_lazy('dashboard:category_list')

    def form_valid(self, form):
        messages.success(self.request, 'Category updated successfully!')
        return super().form_valid(form)


class CategoryDeleteView(StaffRequiredMixin, DeleteView):
    """Dashboard delete category view."""
    model = Category
    template_name = 'dashboard/category_confirm_delete.html'
    success_url = reverse_lazy('dashboard:category_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Category deleted successfully!')
        return super().delete(request, *args, **kwargs)


class LocationListView(StaffRequiredMixin, ListView):
    """Dashboard locations list view."""
    model = Location
    template_name = 'dashboard/location_list.html'
    context_object_name = 'locations'
    paginate_by = 20

    def get_queryset(self):
        return Location.objects.all().order_by('name')


class LocationCreateView(StaffRequiredMixin, CreateView):
    """Dashboard create location view."""
    model = Location
    template_name = 'dashboard/location_form.html'
    fields = ['name', 'city', 'state', 'is_active']
    success_url = reverse_lazy('dashboard:location_list')

    def form_valid(self, form):
        messages.success(self.request, 'Location created successfully!')
        return super().form_valid(form)


class LocationUpdateView(StaffRequiredMixin, UpdateView):
    """Dashboard update location view."""
    model = Location
    template_name = 'dashboard/location_form.html'
    fields = ['name', 'city', 'state', 'is_active']
    success_url = reverse_lazy('dashboard:location_list')

    def form_valid(self, form):
        messages.success(self.request, 'Location updated successfully!')
        return super().form_valid(form)


class LocationDeleteView(StaffRequiredMixin, DeleteView):
    """Dashboard delete location view."""
    model = Location
    template_name = 'dashboard/location_confirm_delete.html'
    success_url = reverse_lazy('dashboard:location_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Location deleted successfully!')
        return super().delete(request, *args, **kwargs)


@staff_required
def delete_gallery_image(request, image_id):
    """Delete a gallery image."""
    if request.method == 'POST':
        image = get_object_or_404(PropertyImage, id=image_id)
        property_obj = image.property
        image.delete()
        messages.success(request, 'Image deleted successfully!')
        return redirect('dashboard:property_edit', pk=property_obj.pk)
    return JsonResponse({'status': 'error'}, status=400)


@staff_required
def delete_property_video(request, video_id):
    """Delete a property video."""
    if request.method == 'POST':
        video = get_object_or_404(PropertyVideo, id=video_id)
        property_obj = video.property
        video.delete()
        messages.success(request, 'Video deleted successfully!')
        return redirect('dashboard:property_edit', pk=property_obj.pk)
    return JsonResponse({'status': 'error'}, status=400)


@staff_required
def admin_logout_view(request):
    """Logout from dashboard."""
    if request.method != 'POST':
        return JsonResponse({'detail': 'Method not allowed.'}, status=405)
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('dashboard:login')


# Import models for use in queryset
from django.db import models
