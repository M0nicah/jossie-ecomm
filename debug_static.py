#!/usr/bin/env python
"""
Debug script to check static files configuration
Run this on Render to debug static file issues
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
sys.path.append(str(Path(__file__).parent))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jossie_fancies.settings')
django.setup()

from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.core.management import execute_from_command_line

def debug_static_files():
    print("=== Static Files Debug Information ===")
    print(f"DEBUG: {settings.DEBUG}")
    print(f"STATIC_URL: {settings.STATIC_URL}")
    print(f"STATIC_ROOT: {settings.STATIC_ROOT}")
    print(f"STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
    print(f"STATICFILES_STORAGE: {settings.STATICFILES_STORAGE}")
    
    # Check if staticfiles directory exists
    staticfiles_path = Path(settings.STATIC_ROOT)
    if staticfiles_path.exists():
        print(f"\nStaticfiles directory exists: {staticfiles_path}")
        print(f"Contents: {list(staticfiles_path.iterdir())}")
        
        # Check for CSS file
        css_path = staticfiles_path / "css" / "output.css"
        if css_path.exists():
            print(f"CSS file exists: {css_path}")
            print(f"CSS file size: {css_path.stat().st_size} bytes")
        else:
            print("CSS file NOT found!")
    else:
        print(f"Staticfiles directory does NOT exist: {staticfiles_path}")
    
    # Try to find static files using Django's finders
    try:
        css_path = find('css/output.css')
        if css_path:
            print(f"Django found CSS at: {css_path}")
        else:
            print("Django could not find CSS file")
    except Exception as e:
        print(f"Error finding CSS file: {e}")

if __name__ == "__main__":
    debug_static_files()
