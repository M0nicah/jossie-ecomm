#!/bin/bash

# Build script for Vercel
echo "BUILD START"

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install Node dependencies for Tailwind CSS
echo "Installing Node dependencies..."
npm install

# Build Tailwind CSS
echo "Building Tailwind CSS..."
npm run build-css-prod

# Create directories
echo "Creating directories..."
mkdir -p staticfiles
mkdir -p static/css

# Run Django collectstatic
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# List static files for debugging
echo "Static files collected:"
ls -la staticfiles/

echo "BUILD END"