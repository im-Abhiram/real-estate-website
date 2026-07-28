"""Security Headers Middleware - Implements OWASP security headers."""

from django.conf import settings


class SecurityHeadersMiddleware:
    """Adds security headers to all responses."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://www.google.com https://www.gstatic.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; "
            "frame-src https://www.google.com; "
            "connect-src 'self'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )

        # Prevent browsers from MIME-sniffing
        response['X-Content-Type-Options'] = 'nosniff'

        # Prevent clickjacking
        response['X-Frame-Options'] = 'DENY'

        # Enable XSS filter in browsers
        response['X-XSS-Protection'] = '1; mode=block'

        # Referrer policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Permissions policy
        response['Permissions-Policy'] = (
            'camera=(), microphone=(), geolocation=(), payment=()'
        )

        # HSTS - only if HTTPS is enabled
        if settings.SECURE_HSTS_SECONDS > 0:
            response['Strict-Transport-Security'] = (
                f'max-age={settings.SECURE_HSTS_SECONDS}; '
                f'includeSubDomains; preload'
            )

        # Remove Server header
        if 'Server' in response:
            del response['Server']

        return response
