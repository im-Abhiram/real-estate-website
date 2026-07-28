"""URL configuration for contact app."""

from django.urls import path
from . import views

app_name = 'contact'

urlpatterns = [
    path('', views.ContactPageView.as_view(), name='contact'),
]