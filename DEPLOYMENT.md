# 🚀 Deployment Guide - Jossie Fancies

This guide covers deployment strategies for the Jossie Fancies e-commerce platform across different hosting providers and environments.

## 📋 **Pre-Deployment Checklist**

### ✅ **Code Preparation**
- [ ] All tests passing (`python manage.py test`)
- [ ] Production CSS built (`npm run build`)
- [ ] Static files collected (`python manage.py collectstatic`)
- [ ] Database migrations created and tested
- [ ] Environment variables configured
- [ ] Security settings reviewed
- [ ] Performance optimizations applied

### ✅ **Security Review**
- [ ] `DEBUG=False` in production
- [ ] Secret key properly configured
- [ ] ALLOWED_HOSTS configured
- [ ] HTTPS enforcement enabled
- [ ] Database credentials secured
- [ ] API keys and tokens secured

## 🌐 **Deployment Platforms**

## 1. **Railway (Recommended)**

Railway offers simple deployment with automatic builds and managed databases.

### **Setup**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and initialize
railway login
railway init
```

### **Configuration**
Create `railway.toml`:
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn jossie_fancies.wsgi:application"
healthcheckPath = "/"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

[environments.production]
variables = { RAILWAY_STATIC_URL = "/static/" }
```

### **Environment Variables**
Set in Railway dashboard:
```bash
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.railway.app
DATABASE_URL=postgresql://...  # Auto-provided by Railway
WHATSAPP_BUSINESS_NUMBER=+254794748719
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### **Deployment**
```bash
railway up
```

## 2. **Heroku**

Traditional platform-as-a-service with extensive add-on ecosystem.

### **Setup**
```bash
# Install Heroku CLI
# macOS: brew install heroku/brew/heroku
# Windows: Download from heroku.com

# Login and create app
heroku login
heroku create jossie-fancies
```

### **Configuration**
Create `Procfile`:
```
web: gunicorn jossie_fancies.wsgi:application
release: python manage.py migrate && python manage.py collectstatic --noinput
```

Create `runtime.txt`:
```
python-3.11.9
```

### **Environment Variables**
```bash
heroku config:set SECRET_KEY=your-production-secret-key
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=jossie-fancies.herokuapp.com
heroku config:set WHATSAPP_BUSINESS_NUMBER=+254794748719
```

### **Add PostgreSQL**
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

### **Deployment**
```bash
git push heroku main
```

## 3. **DigitalOcean App Platform**

Managed platform with competitive pricing and good performance.

### **Setup**
1. Connect GitHub repository in DigitalOcean dashboard
2. Configure build and run commands
3. Set environment variables
4. Deploy

### **App Spec (`.do/app.yaml`)**
```yaml
name: jossie-fancies
services:
- name: web
  source_dir: /
  github:
    repo: your-username/jossie-fancies
    branch: main
  run_command: gunicorn jossie_fancies.wsgi:application
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  
  envs:
  - key: SECRET_KEY
    value: your-production-secret-key
  - key: DEBUG
    value: "False"
  - key: ALLOWED_HOSTS
    value: jossie-fancies-app.ondigitalocean.app
    
databases:
- name: db
  engine: PG
  size: db-s-dev-database
```

## 4. **AWS Elastic Beanstalk**

AWS managed platform with advanced scaling options.

### **Setup**
```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init jossie-fancies
eb create production
```

### **Configuration**
Create `.ebextensions/django.config`:
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: jossie_fancies.wsgi:application
  aws:elasticbeanstalk:environment:proxy:staticfiles:
    /static: static
```

### **Environment Variables**
Set in AWS console or:
```bash
eb setenv SECRET_KEY=your-production-secret-key
eb setenv DEBUG=False
eb setenv ALLOWED_HOSTS=your-app.region.elasticbeanstalk.com
```

## 🗄️ **Database Setup**

### **PostgreSQL (Recommended)**

#### **Local PostgreSQL**
```bash
# Install PostgreSQL
# macOS: brew install postgresql
# Ubuntu: sudo apt-get install postgresql

# Create database and user
createdb jossie_fancies
createuser jossie_user --password
```

#### **Managed PostgreSQL**
- **Railway**: Automatically provisioned
- **Heroku**: `heroku addons:create heroku-postgresql`
- **DigitalOcean**: Add database component
- **AWS RDS**: Set up through AWS console

### **Database Migration**
```bash
# Run migrations
python manage.py migrate

# Load initial data (optional)
python manage.py populate_data
```

## 📁 **Static Files & Media**

### **Local Static Files**
```python
# settings.py
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
```

### **CDN Setup (Recommended for Production)**

#### **Cloudinary**
```python
# settings.py
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'your-cloud-name',
    'API_KEY': 'your-api-key',
    'API_SECRET': 'your-api-secret',
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
STATICFILES_STORAGE = 'cloudinary_storage.storage.StaticHashedCloudinaryStorage'
```

#### **AWS S3**
```python
# settings.py
AWS_ACCESS_KEY_ID = 'your-access-key'
AWS_SECRET_ACCESS_KEY = 'your-secret-key'
AWS_STORAGE_BUCKET_NAME = 'your-bucket-name'
AWS_S3_REGION_NAME = 'us-east-1'

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
```

## 🔧 **Production Settings**

### **Security Settings**
```python
# production_settings.py
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# HTTPS Settings
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# Session Security
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Database Connection Pooling
DATABASES['default']['CONN_MAX_AGE'] = 600
```

### **Performance Settings**
```python
# Caching
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Session Engine
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

# Template Caching
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]
```

## 📧 **Email Configuration**

### **Gmail (Development/Small Scale)**
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Use App Password
```

### **SendGrid (Production)**
```python
EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
SENDGRID_API_KEY = 'your-sendgrid-api-key'
```

### **AWS SES (Enterprise)**
```python
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_ACCESS_KEY_ID = 'your-access-key'
AWS_SECRET_ACCESS_KEY = 'your-secret-key'
AWS_SES_REGION_NAME = 'us-east-1'
```

## 🔍 **Monitoring & Logging**

### **Error Tracking with Sentry**
```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True
)
```

### **Application Monitoring**
```python
# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## 🚀 **Deployment Scripts**

### **Production Deployment Script**
```bash
#!/bin/bash
# deploy.sh

echo "🚀 Deploying Jossie Fancies to production..."

# Pull latest code
git pull origin main

# Install/update dependencies
pip install -r requirements.txt
npm install

# Build assets
npm run build
python manage.py collectstatic --noinput

# Database migrations
python manage.py migrate

# Restart application server
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo "✅ Deployment completed successfully!"
```

### **Health Check Script**
```bash
#!/bin/bash
# health_check.sh

curl -f http://localhost:8000/health/ || exit 1
echo "✅ Application is healthy"
```

## 🔄 **CI/CD Pipeline**

### **GitHub Actions**
Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
        
    - name: Set up Node.js
      uses: actions/setup-node@v2
      with:
        node-version: 18
        
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        npm install
        
    - name: Run tests
      run: python manage.py test
      
    - name: Build CSS
      run: npm run build
      
    - name: Deploy to Railway
      run: railway up
      env:
        RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

## 🆘 **Troubleshooting**

### **Common Issues**

#### **Static Files Not Loading**
```bash
# Ensure static files are collected
python manage.py collectstatic --noinput

# Check STATIC_URL and STATIC_ROOT settings
# Verify web server configuration
```

#### **Database Connection Errors**
```bash
# Check DATABASE_URL format
# Verify database server is running
# Test connection manually
python manage.py dbshell
```

#### **ALLOWED_HOSTS Error**
```python
# Add your domain to ALLOWED_HOSTS
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```

#### **CSS Not Updating**
```bash
# Rebuild CSS
npm run build

# Clear cache
python manage.py collectstatic --clear --noinput
```

## 📞 **Support**

For deployment issues:
- **Email**: jossiefancies1@gmail.com
- **Documentation**: [GitHub Issues](https://github.com/your-repo/issues)
- **Emergency**: +254 790 420 843

---

**Happy Deploying! 🚀**