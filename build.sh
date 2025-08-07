#!/bin/bash

# Exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Build Tailwind CSS
npm install
npm run build-css-prod

# Run database migrations
python manage.py migrate

# Create superuser if it doesn't exist
python manage.py shell -c "
from django.contrib.auth.models import User;
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@jossiefancies.com', 'JossieFancies2024!')
    print('Superuser created: admin')
else:
    print('Superuser already exists')
"

# Collect Django static files
python manage.py collectstatic --noinput

# Create sample data for production
python manage.py populate_data

echo "Build completed successfully!"