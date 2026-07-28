"""Views for the contact page and contact form handling."""

import logging
from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from .forms import ContactForm
from .models import ContactEnquiry

logger = logging.getLogger('realestate')


class ContactPageView(FormView):
    """Contact page with general enquiry form."""
    template_name = 'contact/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact:contact')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meta_title'] = 'Contact Us - Premium Real Estate'
        context['meta_description'] = 'Get in touch with Premium Real Estate. ' \
                                     'Call, email, or visit our office.'
        return context

    def form_valid(self, form):
        # Check honeypot
        if form.cleaned_data.get('website'):
            messages.error(self.request, 'Spam detected.')
            return self.form_invalid(form)

        # Check rate limiting (IP-based)
        ip = self.request.META.get('REMOTE_ADDR')
        recent_count = ContactEnquiry.objects.filter(
            ip_address=ip,
            created_at__gte=timezone.now() - timezone.timedelta(hours=1)
        ).count()
        if recent_count >= 3:
            messages.error(
                self.request,
                'Too many submissions. Please try again later.'
            )
            return self.form_invalid(form)

        # Save form
        enquiry = form.save(commit=False)
        enquiry.ip_address = ip
        enquiry.user_agent = self.request.META.get('HTTP_USER_AGENT', '')[:500]
        enquiry.save()

        # Send admin notification
        self._send_admin_notification(form)

        messages.success(
            self.request,
            'Thank you for your message! We will get back to you shortly.'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Please correct the errors below and try again.'
        )
        return super().form_invalid(form)

    def _send_admin_notification(self, form):
        """Send email notification to admin."""
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            subject = f'New Contact Enquiry: {form.cleaned_data["subject"] or "No Subject"}'
            message = (
                f'New contact enquiry received.\n\n'
                f'From: {form.cleaned_data["name"]}\n'
                f'Email: {form.cleaned_data["email"]}\n'
                f'Phone: {form.cleaned_data.get("phone", "N/A")}\n'
                f'Subject: {form.cleaned_data.get("subject", "N/A")}\n'
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
            logger.error(f'Failed to send contact notification: {e}')