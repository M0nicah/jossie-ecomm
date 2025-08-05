#!/bin/bash
# Build script for Jossie Fancies

echo "🚀 Building Jossie Fancies..."

# Install npm dependencies
echo "📦 Installing npm dependencies..."
npm install

# Build production CSS
echo "🎨 Building production CSS..."
npm run build-css-prod

# Collect Django static files
echo "📁 Collecting Django static files..."
python3 manage.py collectstatic --noinput

# Run Django migrations
echo "🗄️ Running Django migrations..."
python3 manage.py migrate

echo "✅ Build complete! Your site is ready for production."