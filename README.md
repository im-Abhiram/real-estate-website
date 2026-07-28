# Premium Real Estate Website

A production-ready real estate property listing website built with Django. This website is designed for displaying properties and collecting enquiries - no booking or payment functionality.

## Features

### Public Website
- **Homepage**: Hero section, featured properties, latest properties, property categories, search box, about section, why choose us, contact section
- **Property Listing**: Grid layout with pagination, search, filter by location/type/price/bedrooms, sorting
- **Property Details**: Image gallery, full details, amenities, location map, enquiry form, related properties
- **About Page**: Company information, mission, vision, experience stats
- **Contact Page**: General enquiry form, office address, phone, email, Google Map
- **SEO Optimized**: Meta tags, Open Graph, Twitter Cards, Schema.org markup, sitemap, robots.txt
- **Responsive Design**: Mobile-first, works on all devices

### Admin Dashboard
- Secure admin login with rate limiting
- Dashboard with statistics overview
- Property management (CRUD): Create, Edit, Delete, Draft/Publish
- Enquiry management: View, Search, Delete, Export to CSV
- Django admin panel for full control

### Security (OWASP Top 10)
- CSRF Protection
- XSS Protection (output escaping, input sanitization)
- SQL Injection Protection (Django ORM only)
- Security Headers (CSP, HSTS, X-Frame-Options, etc.)
- Login Rate Limiting (django-axes)
- Strong Password Validation
- Session Security (HttpOnly, SameSite, expiry)
- File Upload Validation (type, extension, size, rename)
- Honeypot spam protection
- Environment variables for secrets
- Custom admin URL to reduce automated scanning

## Tech Stack

- **Backend**: Django 6.0, Python 3.12+
- **Frontend**: HTML5, CSS3, Bootstrap 5, Vanilla JavaScript
- **Database**: SQLite (dev), PostgreSQL ready (production)
- **Image Processing**: Pillow
- **Deployment**: Gunicorn, Nginx, WhiteNoise

## Installation

### Prerequisites
- Python 3.12 or higher
- pip (Python package manager)
- Git (optional)

### Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd realestate
```

2. **Create and activate virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment configuration**
```bash
cp .env.example .env
# Edit .env with your settings (SECRET_KEY, database, email, etc.)
```

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Seed sample data (optional)**
```bash
python manage.py shell
# In the shell, run:
exec(open('seed_data.py').read())
```

7. **Collect static files**
```bash
python manage.py collectstatic --noinput
```

8. **Run development server**
```bash
python manage.py runserver
```

9. **Access the website**
- Website: http://localhost:8000
- Admin Panel: http://localhost:8000/admin-panel/
- Dashboard: http://localhost:8000/dashboard/

### Default Admin Credentials
After running seed_data.py:
- Username: `admin`
- Password: `Admin@123456`

## Project Structure

```
realestate/
├── accounts/           # User authentication app
├── properties/         # Property management app
│   ├── models.py       # Property, Category, PropertyImage, PropertyEnquiry
│   ├── views.py        # PropertyListView, PropertyDetailView, PropertyEnquiryView
│   ├── forms.py        # PropertyEnquiryForm, PropertySearchForm
│   └── admin.py        # Admin configuration
├── contact/            # Contact/enquiry app
├── core/               # Core pages (home, about, error handlers)
├── dashboard/          # Admin dashboard app
├── realestate/         # Project settings
│   ├── settings.py     # Django settings
│   ├── urls.py         # Main URL configuration
│   └── middleware.py   # Security headers middleware
├── static/             # Static files (CSS, JS)
├── templates/          # HTML templates
│   ├── base.html       # Base template
│   ├── core/           # Home, About pages
│   ├── properties/     # Property list, detail pages
│   ├── contact/        # Contact page
│   ├── dashboard/      # Admin dashboard templates
│   └── errors/         # 404, 500, 403 error pages
├── media/              # Uploaded images (created at runtime)
├── staticfiles/        # Collected static files
├── logs/               # Application logs
├── manage.py           # Django management script
├── requirements.txt    # Python dependencies
├── seed_data.py        # Sample data seeder
└── .env.example        # Environment variables template
```

## Security Configuration

### For Production Deployment

1. **Generate a secure SECRET_KEY**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

2. **Set environment variables in .env**
```
DEBUG=False
SECRET_KEY=<your-generated-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
ADMIN_URL=<random-secure-string>/
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
```

3. **Configure database** (PostgreSQL recommended)
   - Uncomment PostgreSQL config in settings.py
   - Add DB credentials to .env

4. **Configure email** (SMTP)
   - Add SMTP settings to .env

5. **Set up HTTPS** with a reverse proxy (Nginx)

### Security Headers
The website implements these security headers via middleware:
- Content-Security-Policy
- X-Content-Type-Options (nosniff)
- X-Frame-Options (DENY)
- X-XSS-Protection
- Referrer-Policy
- Permissions-Policy
- Strict-Transport-Security (HSTS)

## Deployment

### With Gunicorn and Nginx

1. **Install production dependencies**
```bash
pip install gunicorn psycopg2-binary
```

2. **Run with Gunicorn**
```bash
gunicorn realestate.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

3. **Configure Nginx** - Sample configuration is available on request

## License

This project is licensed under the MIT License.