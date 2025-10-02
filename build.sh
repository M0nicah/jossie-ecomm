#!/bin/bash

# Exit on error
set -o errexit

echo "Starting build process..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install Node.js dependencies and build CSS
echo "Installing Node.js dependencies..."
npm install

echo "Building Tailwind CSS for production..."
npm run build-css-prod

# Verify CSS file exists
if [ ! -f "static/css/output.css" ]; then
    echo "Error: CSS file not found after build!"
    echo "Attempting fallback build..."
    npm run build
    
    # Check again
    if [ ! -f "static/css/output.css" ]; then
        echo "Fallback build also failed. Creating minimal CSS file..."
        mkdir -p static/css
        echo "/* Minimal CSS fallback */" > static/css/output.css
        echo "body { font-family: Arial, sans-serif; }" >> static/css/output.css
    fi
fi

echo "CSS file size: $(ls -lh static/css/output.css | awk '{print $5}')"

# Run database migrations
echo "Running database migrations..."
python manage.py migrate

# Create superuser if environment variables are provided
if [[ -n "$DJANGO_SUPERUSER_USERNAME" && -n "$DJANGO_SUPERUSER_EMAIL" && -n "$DJANGO_SUPERUSER_PASSWORD" ]]; then
  echo "Creating superuser..."
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
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Verify static files were collected
echo "Verifying static files collection..."
ls -la staticfiles/

# Run debug script to check static files
echo "Running static files debug..."
python debug_static.py

# Create sample data for production
echo "Creating sample data..."
python manage.py populate_data

echo "Build completed successfully!"
