"""Forms for property enquiries and search."""

from django import forms
from django.conf import settings
from .models import Property, PropertyEnquiry, Location


class PropertyEnquiryForm(forms.ModelForm):
    """Form for property enquiry with spam protection."""

    # Honeypot field for spam protection
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'style': 'position: absolute; left: -9999px;',
            'tabindex': '-1',
            'autocomplete': 'off'
        })
    )

    class Meta:
        model = PropertyEnquiry
        fields = ['name', 'phone', 'email', 'message', 'website']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Full Name',
                'required': True,
                'maxlength': 100,
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Phone Number',
                'required': True,
                'maxlength': 20,
                'pattern': '[0-9+ -]+',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Email Address',
                'required': True,
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Your Message...',
                'required': True,
                'rows': 4,
                'maxlength': 2000,
            }),
        }

    def __init__(self, *args, **kwargs):
        self.property_obj = kwargs.pop('property_obj', None)
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean_website(self):
        """Honeypot check - if filled, it's a bot."""
        website = self.cleaned_data.get('website')
        if website:
            raise forms.ValidationError('Spam detected.')
        return ''

    def clean_phone(self):
        """Validate phone number format."""
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove common separators for validation
            cleaned = phone.replace(' ', '').replace('-', '').replace('+', '')
            if not cleaned.isdigit():
                raise forms.ValidationError('Enter a valid phone number.')
            if len(cleaned) < 10 or len(cleaned) > 15:
                raise forms.ValidationError('Phone number must be between 10 and 15 digits.')
        return phone

    def clean_message(self):
        """Sanitize message input."""
        message = self.cleaned_data.get('message', '')
        # Strip potentially dangerous HTML/script tags
        import re
        message = re.sub(r'<[^>]*>', '', message)
        return message.strip()

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.property_obj:
            instance.property = self.property_obj
        if self.request:
            instance.ip_address = self.request.META.get('REMOTE_ADDR')
            instance.user_agent = self.request.META.get('HTTP_USER_AGENT', '')[:500]
        if commit:
            instance.save()
        return instance


class PropertySearchForm(forms.Form):
    """Property search form with multiple criteria."""

    keyword = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by keyword, title, or location...',
        })
    )
    location = forms.ModelChoiceField(
        required=False,
        queryset=Location.objects.filter(is_active=True).order_by('name'),
        empty_label='All Locations',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    property_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types')] + list(Property.PropertyType.choices),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Price',
            'min': 0,
        })
    )
    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Price',
            'min': 0,
        })
    )
    bedrooms = forms.ChoiceField(
        required=False,
        choices=[('', 'Any')] + [(str(i), str(i)) for i in range(1, 11)] +
                [('10+', '10+')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    sort_by = forms.ChoiceField(
        required=False,
        choices=[
            ('newest', 'Newest First'),
            ('price_low', 'Price: Low to High'),
            ('price_high', 'Price: High to Low'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )