"""Forms for general contact enquiries."""

from django import forms
from .models import ContactEnquiry


class ContactForm(forms.ModelForm):
    """General contact form with spam protection."""

    # Honeypot field
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'style': 'position: absolute; left: -9999px;',
            'tabindex': '-1',
            'autocomplete': 'off'
        })
    )

    class Meta:
        model = ContactEnquiry
        fields = ['name', 'email', 'phone', 'subject', 'message', 'website']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Full Name',
                'required': True,
                'maxlength': 100,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Email Address',
                'required': True,
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Phone (Optional)',
                'maxlength': 20,
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject',
                'maxlength': 200,
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Your Message...',
                'required': True,
                'rows': 5,
                'maxlength': 5000,
            }),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean_website(self):
        """Honeypot check."""
        website = self.cleaned_data.get('website')
        if website:
            raise forms.ValidationError('Spam detected.')
        return ''

    def clean_message(self):
        """Sanitize message - remove HTML tags."""
        message = self.cleaned_data.get('message', '')
        import re
        message = re.sub(r'<[^>]*>', '', message)
        return message.strip()

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.request:
            instance.ip_address = self.request.META.get('REMOTE_ADDR')
            instance.user_agent = self.request.META.get('HTTP_USER_AGENT', '')[:500]
        if commit:
            instance.save()
        return instance