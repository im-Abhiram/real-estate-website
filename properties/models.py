"""Property models for the real estate application."""

import os
import uuid
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.db import models
from django.utils.text import slugify
from django.utils import timezone


def property_image_path(instance, filename):
    """Generate unique filename for property cover images."""
    ext = filename.lower().split('.')[-1]
    if ext not in ['jpg', 'jpeg', 'png', 'webp']:
        ext = 'jpg'
    filename = f'{uuid.uuid4().hex}.{ext}'
    # instance is Property model itself for cover_image
    slug = getattr(instance, 'slug', 'property')
    return os.path.join('properties', slug, filename)


def property_gallery_path(instance, filename):
    """Generate unique filename for gallery images."""
    ext = filename.lower().split('.')[-1]
    if ext not in ['jpg', 'jpeg', 'png', 'webp']:
        ext = 'jpg'
    filename = f'{uuid.uuid4().hex}.{ext}'
    # instance is PropertyImage model, access property via FK
    slug = instance.property.slug if hasattr(instance, 'property') and instance.property else 'property'
    return os.path.join('properties', slug, 'gallery', filename)


def property_video_path(instance, filename):
    """Generate unique filename for property videos."""
    ext = filename.lower().split('.')[-1]
    filename = f'{uuid.uuid4().hex}.{ext}'
    slug = instance.property.slug if hasattr(instance, 'property') and instance.property else 'property'
    return os.path.join('properties', slug, 'videos', filename)


class Category(models.Model):
    """Property categories like Apartment, Villa, House, etc."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon class")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def property_count(self):
        """Return count of published properties in this category."""
        return self.properties.filter(status='published', is_published=True).count()


class Property(models.Model):
    """Main Property model with all fields for real estate listings."""

    class PropertyType(models.TextChoices):
        APARTMENT = 'apartment', 'Apartment'
        VILLA = 'villa', 'Villa'
        HOUSE = 'house', 'House'
        COMMERCIAL = 'commercial', 'Commercial'
        OFFICE = 'office', 'Office'
        LAND = 'land', 'Land'
        FARM = 'farm', 'Farm'
        INDUSTRIAL = 'industrial', 'Industrial'

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'
        SOLD = 'sold', 'Sold'
        RENTED = 'rented', 'Rented'

    # Basic Information
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    property_id = models.CharField(max_length=20, unique=True, blank=True, editable=False)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True, related_name='properties'
    )
    property_type = models.CharField(
        max_length=20,
        choices=PropertyType.choices,
        default=PropertyType.APARTMENT
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

    # Pricing
    price = models.DecimalField(max_digits=14, decimal_places=2)
    price_sqft = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Location
    location = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    # Property Details
    description = models.TextField()
    bedrooms = models.PositiveIntegerField(default=0)
    bathrooms = models.PositiveIntegerField(default=0)
    area = models.DecimalField(max_digits=12, decimal_places=2, help_text="Area in sq. ft.")
    parking = models.PositiveIntegerField(default=0, help_text="Number of parking spaces")
    year_built = models.PositiveIntegerField(blank=True, null=True)
    amenities = models.TextField(
        blank=True,
        help_text="Comma-separated list of amenities"
    )

    # Featured & Publishing
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    featured_until = models.DateTimeField(blank=True, null=True)

    # Images
    cover_image = models.ImageField(
        upload_to=property_image_path,
        blank=True,
        null=True
    )

    # SEO Fields
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True, max_length=500)
    og_image = models.ImageField(upload_to=property_image_path, blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'is_published']),
            models.Index(fields=['city', 'state']),
            models.Index(fields=['price']),
            models.Index(fields=['bedrooms']),
            models.Index(fields=['property_type']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        # Generate slug
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Property.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug

        # Generate property ID
        if not self.property_id:
            year = timezone.now().strftime('%Y')
            last_property = Property.objects.filter(
                property_id__startswith=f'RE{year}'
            ).order_by('property_id').last()
            if last_property and last_property.property_id:
                last_num = int(last_property.property_id[-5:])
                new_num = last_num + 1
            else:
                new_num = 1
            self.property_id = f'RE{year}{new_num:05d}'

        # Set published date
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)

        # Process and resize cover image
        if self.cover_image and is_new:
            self._resize_image(self.cover_image)

    def _resize_image(self, image_field, max_width=1200, max_height=800):
        """Resize and compress image for optimization."""
        try:
            img = Image.open(image_field.path)
            if img.height > max_height or img.width > max_width:
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                img.save(image_field.path, quality=85, optimize=True)
        except Exception:
            pass  # Log error silently if image processing fails

    def get_amenities_list(self):
        """Return amenities as a list."""
        if not self.amenities:
            return []
        return [a.strip() for a in self.amenities.split(',') if a.strip()]

    def formatted_price(self):
        """Return price formatted with commas."""
        return f'₹{self.price:,.0f}'

    def formatted_area(self):
        """Return area formatted."""
        return f'{self.area:,.2f} sq. ft.'


class PropertyImage(models.Model):
    """Gallery images for properties."""

    property = models.ForeignKey(
        Property, on_delete=models.CASCADE,
        related_name='gallery_images'
    )
    image = models.ImageField(upload_to=property_gallery_path)
    alt_text = models.CharField(max_length=200, blank=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Property Image'
        verbose_name_plural = 'Property Images'
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"Image for {self.property.title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Resize gallery images
        try:
            img = Image.open(self.image.path)
            if img.height > 1200 or img.width > 1600:
                img.thumbnail((1600, 1200), Image.Resampling.LANCZOS)
                img.save(self.image.path, quality=85, optimize=True)
        except Exception:
            pass


class PropertyVideo(models.Model):
    """Videos for properties."""

    property = models.ForeignKey(
        Property, on_delete=models.CASCADE,
        related_name='property_videos'
    )
    video = models.FileField(upload_to=property_video_path)
    title = models.CharField(max_length=200, blank=True, help_text="Optional title/description for the video")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Property Video'
        verbose_name_plural = 'Property Videos'
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"Video for {self.property.title}"


class PropertyEnquiry(models.Model):
    """Enquiries from users about specific properties."""

    property = models.ForeignKey(
        Property, on_delete=models.CASCADE,
        related_name='enquiries'
    )
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    # Spam protection fields
    honeypot = models.CharField(max_length=100, blank=True, default='')
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Property Enquiry'
        verbose_name_plural = 'Property Enquiries'
        ordering = ['-created_at']

    def __str__(self):
        return f"Enquiry from {self.name} about {self.property.title}"


class Location(models.Model):
    """Location / City model for managing property locations."""

    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def property_count(self):
        return Property.objects.filter(city=self.city, state=self.state).count()