"""
Seed data script to populate the database with initial data.
Run: python manage.py shell < seed_data.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realestate.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from properties.models import Category, Property
from core.models import SiteSettings

User = get_user_model()

# Create admin user if not exists
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@realestate.com',
        password='Admin@123456'
    )
    print('Admin user created: admin / Admin@123456')

# Create categories
categories_data = [
    {'name': 'Apartment', 'icon': 'fas fa-building'},
    {'name': 'Villa', 'icon': 'fas fa-home'},
    {'name': 'House', 'icon': 'fas fa-house-user'},
    {'name': 'Commercial', 'icon': 'fas fa-store'},
    {'name': 'Office', 'icon': 'fas fa-briefcase'},
    {'name': 'Land', 'icon': 'fas fa-tree'},
    {'name': 'Farm', 'icon': 'fas fa-tractor'},
    {'name': 'Industrial', 'icon': 'fas fa-industry'},
]

categories = {}
for cat_data in categories_data:
    cat, created = Category.objects.get_or_create(
        name=cat_data['name'],
        defaults={'icon': cat_data['icon']}
    )
    categories[cat.name] = cat
    if created:
        print(f'Category created: {cat.name}')

# Create sample properties
sample_properties = [
    {
        'title': 'Luxury 3BHK Apartment with Sea View',
        'category': 'Apartment',
        'property_type': 'apartment',
        'price': 8500000.00,
        'location': 'Marine Drive, Mumbai',
        'city': 'Mumbai',
        'state': 'Maharashtra',
        'description': 'Beautiful 3BHK apartment with stunning sea view. Features modern interiors, fully modular kitchen, spacious living room with panoramic windows, and premium fittings throughout. Located in the heart of Marine Drive with easy access to all amenities.',
        'bedrooms': 3,
        'bathrooms': 2,
        'area': 1500.00,
        'parking': 2,
        'amenities': 'Sea View, Modular Kitchen, AC, Parking, Gym, Pool, Security, Power Backup',
        'is_featured': True,
        'is_published': True,
        'status': 'published',
    },
    {
        'title': 'Premium Villa in Gated Community',
        'category': 'Villa',
        'property_type': 'villa',
        'price': 25000000.00,
        'location': 'Whitefield, Bangalore',
        'city': 'Bangalore',
        'state': 'Karnataka',
        'description': 'Stunning 4BHK villa in a premium gated community. Features include private garden, modern architecture, high ceilings, and top-quality finishes. The community offers clubhouse, swimming pool, tennis court, and 24/7 security.',
        'bedrooms': 4,
        'bathrooms': 3,
        'area': 3500.00,
        'parking': 3,
        'amenities': 'Garden, Clubhouse, Pool, Tennis Court, Security, Parking, Rainwater Harvesting',
        'is_featured': True,
        'is_published': True,
        'status': 'published',
    },
    {
        'title': 'Modern 2BHK Apartment',
        'category': 'Apartment',
        'property_type': 'apartment',
        'price': 4500000.00,
        'location': 'Koramangala, Bangalore',
        'city': 'Bangalore',
        'state': 'Karnataka',
        'description': 'Modern 2BHK apartment in a prime location. Close to tech parks, restaurants, and shopping centers. Features include spacious rooms, modular kitchen, and beautiful city views.',
        'bedrooms': 2,
        'bathrooms': 2,
        'area': 1100.00,
        'parking': 1,
        'amenities': 'Modular Kitchen, AC, Parking, Gym, Security',
        'is_featured': False,
        'is_published': True,
        'status': 'published',
    },
    {
        'title': 'Commercial Office Space for Lease',
        'category': 'Office',
        'property_type': 'office',
        'price': 15000000.00,
        'location': 'Bandra Kurla Complex, Mumbai',
        'city': 'Mumbai',
        'state': 'Maharashtra',
        'description': 'Premium commercial office space in BKC. Open floor plan with modern finishes, ample natural light, and excellent connectivity. Ideal for corporate offices, co-working spaces, or professional services.',
        'bedrooms': 0,
        'bathrooms': 2,
        'area': 2000.00,
        'parking': 4,
        'amenities': 'AC, Parking, Security, Cafeteria, Elevator, Power Backup',
        'is_featured': True,
        'is_published': True,
        'status': 'published',
    },
    {
        'title': 'Sprawling Farm House',
        'category': 'Farm',
        'property_type': 'farm',
        'price': 50000000.00,
        'location': 'Lavasa, Pune',
        'city': 'Pune',
        'state': 'Maharashtra',
        'description': 'Beautiful farm house on 5 acres of land. Features a main house, guest house, organic farm, fruit orchard, and a private lake. Perfect for weekend getaways or permanent residence away from the city.',
        'bedrooms': 5,
        'bathrooms': 4,
        'area': 5000.00,
        'parking': 6,
        'amenities': 'Private Lake, Organic Farm, Garden, Swimming Pool, Solar Panels, Water Treatment',
        'is_featured': True,
        'is_published': True,
        'status': 'published',
    },
    {
        'title': 'Residential Plot for Development',
        'category': 'Land',
        'property_type': 'land',
        'price': 12000000.00,
        'location': 'Electronic City, Bangalore',
        'city': 'Bangalore',
        'state': 'Karnataka',
        'description': 'Prime residential plot in a developing area. Ideal for building your dream home or for investment purposes. All utilities available. Easy access to main road and public transport.',
        'bedrooms': 0,
        'bathrooms': 0,
        'area': 2400.00,
        'parking': 0,
        'amenities': 'Water Connection, Electricity, Road Access',
        'is_featured': False,
        'is_published': True,
        'status': 'published',
    },
]

created_count = 0
for prop_data in sample_properties:
    category_name = prop_data.pop('category')
    cat = categories.get(category_name)
    if not Property.objects.filter(title=prop_data['title']).exists():
        Property.objects.create(
            category=cat,
            **prop_data
        )
        created_count += 1
        print(f'Property created: {prop_data["title"]}')

# Create site settings
if not SiteSettings.objects.exists():
    SiteSettings.objects.create(
        site_name='Royal Trivandrum',
        tagline='Your Trusted Real Estate Partner in Trivandrum',
        description='Your trusted real estate partner in Trivandrum. Premium properties across Kerala.',
        contact_address='TC 24/1256, MG Road, Statue Junction, Thiruvananthapuram, Kerala - 695001',
        contact_phone='+91 471 234 5678',
        contact_email='info@royaltrivandrum.com',
    )
    print('Site settings created')

print(f'\nSeed data complete!')
print(f'Categories: {Category.objects.count()}')
print(f'Properties: {Property.objects.count()}')
print(f'Properties published: {Property.objects.filter(is_published=True).count()}')
