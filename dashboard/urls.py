"""URL configuration for dashboard app."""

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardHomeView.as_view(), name='home'),
    path('login/', views.admin_login_view, name='login'),
    path('properties/', views.PropertyListView.as_view(), name='property_list'),
    path('properties/add/', views.PropertyCreateView.as_view(), name='property_create'),
    path('properties/<int:pk>/edit/', views.PropertyUpdateView.as_view(), name='property_edit'),
    path('properties/<int:pk>/delete/', views.PropertyDeleteView.as_view(), name='property_delete'),
    path('enquiries/', views.EnquiryListView.as_view(), name='enquiry_list'),
    path('enquiries/<int:pk>/delete/', views.EnquiryDeleteView.as_view(), name='enquiry_delete'),
    path('enquiries/export/', views.export_enquiries_csv, name='enquiry_export_csv'),
    path('settings/', views.site_settings_view, name='site_settings'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    path('locations/', views.LocationListView.as_view(), name='location_list'),
    path('locations/add/', views.LocationCreateView.as_view(), name='location_create'),
    path('locations/<int:pk>/edit/', views.LocationUpdateView.as_view(), name='location_edit'),
    path('locations/<int:pk>/delete/', views.LocationDeleteView.as_view(), name='location_delete'),
    path('images/<int:image_id>/delete/', views.delete_gallery_image, name='delete_gallery_image'),
    path('videos/<int:video_id>/delete/', views.delete_property_video, name='delete_property_video'),
    path('logout/', views.admin_logout_view, name='logout'),
]