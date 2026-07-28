"""Validation helpers for uploaded property images and videos."""

from PIL import Image, UnidentifiedImageError
from django.conf import settings
from django.core.exceptions import ValidationError


ALLOWED_CONTENT_TYPES = {'image/jpeg', 'image/png', 'image/webp'}
ALLOWED_IMAGE_FORMATS = {'JPEG', 'PNG', 'WEBP'}

ALLOWED_VIDEO_CONTENT_TYPES = {'video/mp4', 'video/webm', 'video/ogg', 'video/quicktime'}
ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.webm', '.ogg', '.mov'}
MAX_VIDEO_SIZE = 104857600  # 100MB


def validate_uploaded_image(uploaded_file):
    """Reject oversized, non-image, or unsupported image uploads."""
    if uploaded_file.size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
        raise ValidationError('Each image must be 5 MB or smaller.')
    if uploaded_file.content_type not in ALLOWED_CONTENT_TYPES:
        raise ValidationError('Only JPG, JPEG, PNG, and WebP images are allowed.')
    try:
        image = Image.open(uploaded_file)
        image.verify()
        if image.format not in ALLOWED_IMAGE_FORMATS:
            raise ValidationError('Only JPG, JPEG, PNG, and WebP images are allowed.')
    except (UnidentifiedImageError, OSError, ValueError) as error:
        raise ValidationError('Upload a valid image file.') from error
    finally:
        uploaded_file.seek(0)


def validate_uploaded_video(uploaded_file):
    """Reject oversized, non-video, or unsupported video uploads."""
    if uploaded_file.size > MAX_VIDEO_SIZE:
        raise ValidationError('Each video must be 100 MB or smaller.')
    if uploaded_file.content_type not in ALLOWED_VIDEO_CONTENT_TYPES:
        raise ValidationError('Only MP4, WebM, OGG, and MOV video formats are allowed.')
    # Check file extension as an additional safety measure
    ext = uploaded_file.name.lower().rsplit('.', 1)[-1] if '.' in uploaded_file.name else ''
    if f'.{ext}' not in ALLOWED_VIDEO_EXTENSIONS:
        raise ValidationError('Only MP4, WebM, OGG, and MOV video formats are allowed.')
    uploaded_file.seek(0)