"""Core models for site settings."""

from django.db import models


class SiteSettings(models.Model):
    """Site-wide settings managed from admin."""

    site_name = models.CharField(max_length=100, default='Royal Trivandrum')
    tagline = models.CharField(max_length=200, default='Your Trusted Real Estate Partner in Trivandrum')
    description = models.TextField(default='Your trusted real estate partner in Trivandrum. Premium properties across Kerala.')
    contact_address = models.CharField(max_length=255, default='TC 24/1256, MG Road, Statue Junction, Thiruvananthapuram, Kerala - 695001')
    contact_phone = models.CharField(max_length=20, default='+91 471 234 5678')
    contact_email = models.EmailField(default='info@royaltrivandrum.com')
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    
    # About page content
    about_story_title = models.CharField(max_length=200, default='Our Story')
    about_story_content = models.TextField(default='Premium Real Estate has been at the forefront of the real estate industry, delivering exceptional properties and unmatched service to our clients. Founded in 2010, we have grown from a small local agency to one of the most trusted real estate companies in the region.')
    about_mission_title = models.CharField(max_length=200, default='Our Mission')
    about_mission_content = models.TextField(default='To provide exceptional real estate services with integrity, transparency, and professionalism. We strive to make the property buying and selling process seamless and rewarding for our clients.')
    about_vision_title = models.CharField(max_length=200, default='Our Vision')
    about_vision_content = models.TextField(default='To be the most trusted and innovative real estate company, setting new standards in property services and creating lasting value for our clients and communities.')

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.site_name