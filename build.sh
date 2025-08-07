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

# Collect Django static files
python manage.py collectstatic --noinput

# Create sample data for production
python manage.py populate_data

echo "Build completed successfully!"