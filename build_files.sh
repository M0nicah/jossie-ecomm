#!/bin/bash

# Build script for Vercel
echo "BUILD START"

# Create a virtual environment
echo "Creating virtual environment..."
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing requirements..."
pip install -r requirements.txt

# Make migrations
echo "Making migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "BUILD END"