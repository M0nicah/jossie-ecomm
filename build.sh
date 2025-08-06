#!/bin/bash

# Exit on error
set -e

echo "Starting Django build process..."

# Install Python dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p staticfiles

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Run migrations (optional, remove if using external database)
# echo "Running migrations..."
# python manage.py migrate --noinput

echo "Build completed successfully!"