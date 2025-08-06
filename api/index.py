# Vercel expects an api directory with Python files
# This file redirects to the main Django WSGI application

import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jossie_fancies.settings')

# Import and use the WSGI application
from jossie_fancies.wsgi import application

# Create a handler for Vercel
def handler(request, context):
    """
    Vercel serverless function handler that wraps the Django WSGI application
    """
    return application(request, context)

# For local testing
if __name__ == "__main__":
    print("This file is meant to be deployed on Vercel")