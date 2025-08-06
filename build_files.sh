#!/bin/bash

# Build script for Vercel deployment
echo "======================================"
echo "Build script started"
echo "======================================"

# Print current directory
echo "Current directory: $(pwd)"

# List files in current directory
echo "Files in current directory:"
ls -la

# Install Python dependencies
echo "======================================"
echo "Installing Python dependencies..."
echo "======================================"
pip install -r requirements.txt

# Install Node dependencies
echo "======================================"
echo "Installing Node dependencies..."
echo "======================================"
npm install

# List node_modules to verify installation
echo "Checking if node_modules exists:"
ls -la node_modules/ | head -10

# Create necessary directories
echo "======================================"
echo "Creating directories..."
echo "======================================"
mkdir -p static/css
mkdir -p staticfiles
mkdir -p staticfiles/css

# Build Tailwind CSS
echo "======================================"
echo "Building Tailwind CSS..."
echo "======================================"
npm run build-css-prod

# Check if CSS was created
echo "======================================"
echo "Checking if CSS file was created..."
echo "======================================"
if [ -f "static/css/output.css" ]; then
    echo "SUCCESS: output.css created"
    echo "File size: $(ls -lh static/css/output.css | awk '{print $5}')"
else
    echo "ERROR: output.css was NOT created"
    echo "Contents of static/css:"
    ls -la static/css/
fi

# Run Django collectstatic
echo "======================================"
echo "Collecting static files..."
echo "======================================"
python manage.py collectstatic --noinput --clear

# Check staticfiles directory
echo "======================================"
echo "Checking collected static files..."
echo "======================================"
echo "Contents of staticfiles/css:"
ls -la staticfiles/css/

# Final verification
echo "======================================"
echo "Final verification..."
echo "======================================"
if [ -f "staticfiles/css/output.css" ]; then
    echo "SUCCESS: CSS file is in staticfiles"
    echo "File size: $(ls -lh staticfiles/css/output.css | awk '{print $5}')"
else
    echo "ERROR: CSS file is NOT in staticfiles"
fi

echo "======================================"
echo "Build script completed"
echo "======================================"