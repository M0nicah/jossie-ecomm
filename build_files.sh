#!/bin/bash

# Build script for Vercel deployment
echo "======================================"
echo "Build script started"
echo "======================================"

# Print current directory
echo "Current directory: $(pwd)"

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

# Create necessary directories
echo "======================================"
echo "Creating directories..."
echo "======================================"
mkdir -p static/css
mkdir -p staticfiles
mkdir -p staticfiles/css
mkdir -p staticfiles/admin
mkdir -p staticfiles/admin/css

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
    
    # Copy CSS files directly to staticfiles as backup
    echo "Copying CSS files to staticfiles directory..."
    cp -v static/css/output.css staticfiles/css/output.css
    cp -v static/css/test.css staticfiles/css/test.css 2>/dev/null || true
    cp -v static/css/input.css staticfiles/css/input.css 2>/dev/null || true
    
    # Also copy to public directory for Vercel
    echo "Copying CSS files to public directory for Vercel..."
    mkdir -p public/static/css
    mkdir -p public/static/images
    cp -v static/css/output.css public/static/css/output.css
    cp -v static/images/* public/static/images/ 2>/dev/null || true
else
    echo "ERROR: output.css was NOT created"
    echo "Creating fallback CSS file..."
    cat > static/css/output.css << 'EOF'
/* Fallback CSS - Tailwind build failed */
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Lato', -apple-system, BlinkMacSystemFont, sans-serif; line-height: 1.6; color: #333; }
.bg-primary { background-color: #FF9A00; }
.text-primary { color: #FF9A00; }
.bg-white { background-color: white; }
.text-white { color: white; }
.container { max-width: 1200px; margin: 0 auto; padding: 0 1rem; }
.btn { padding: 0.5rem 1rem; border-radius: 0.25rem; cursor: pointer; transition: all 0.3s; }
.hidden { display: none !important; }
EOF
    
    # Copy fallback to staticfiles
    cp -v static/css/output.css staticfiles/css/output.css
fi

# Run Django collectstatic
echo "======================================"
echo "Collecting static files..."
echo "======================================"
python manage.py collectstatic --noinput --clear || {
    echo "WARNING: collectstatic failed, copying files manually..."
    
    # Manual copy of essential files
    cp -r static/* staticfiles/ 2>/dev/null || true
    
    # Copy Django admin static files
    DJANGO_STATIC=$(python -c "import django; print(django.__path__[0])")
    if [ -d "$DJANGO_STATIC/contrib/admin/static/admin" ]; then
        echo "Copying Django admin static files..."
        cp -r "$DJANGO_STATIC/contrib/admin/static/admin" staticfiles/
    fi
}

# Verify CSS files exist in staticfiles
echo "======================================"
echo "Verifying static files..."
echo "======================================"
if [ -f "staticfiles/css/output.css" ]; then
    echo "SUCCESS: CSS file is in staticfiles"
    echo "File size: $(ls -lh staticfiles/css/output.css | awk '{print $5}')"
else
    echo "ERROR: CSS file is NOT in staticfiles"
    echo "Creating it one more time..."
    mkdir -p staticfiles/css
    echo "/* Emergency CSS */" > staticfiles/css/output.css
    echo "body { font-family: sans-serif; }" >> staticfiles/css/output.css
fi

# List all CSS files for debugging
echo "======================================"
echo "All CSS files in project:"
find . -name "*.css" -type f | grep -E "(static|staticfiles)" | head -20

echo "======================================"
echo "Build script completed"
echo "======================================"