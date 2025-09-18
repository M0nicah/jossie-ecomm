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

# Create superuser if environment variables are provided
if [[ -n "$DJANGO_SUPERUSER_USERNAME" && -n "$DJANGO_SUPERUSER_EMAIL" && -n "$DJANGO_SUPERUSER_PASSWORD" ]]; then
  python manage.py shell -c "
from django.contrib.auth.models import User;
import os;
username = os.environ['DJANGO_SUPERUSER_USERNAME'];
email = os.environ['DJANGO_SUPERUSER_EMAIL'];
password = os.environ['DJANGO_SUPERUSER_PASSWORD'];
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f'Superuser created: {username}')
else:
    print(f'Superuser already exists: {username}')
"
else
  echo "Skipping superuser creation. Provide DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, and DJANGO_SUPERUSER_PASSWORD to auto-create one."
fi

# Collect Django static files
python manage.py collectstatic --noinput

# Create sample data for production
python manage.py populate_data

echo "Build completed successfully!"
