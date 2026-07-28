"""Contact models for general enquiries."""

from django.db import models


class ContactEnquiry(models.Model):
    """General contact form enquiries."""

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    # Spam protection
    honeypot = models.CharField(max_length=100, blank=True, default='')
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Contact Enquiry'
        verbose_name_plural = 'Contact Enquiries'
        ordering = ['-created_at']

    def __str__(self):
        return f"Contact from {self.name} - {self.subject or 'No Subject'}"