#!/bin/bash

# Exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Build Tailwind CSS
npm install
npm run build-css-prod

# Collect Django static files
python manage.py collectstatic --noinput

echo "Build completed successfully!"