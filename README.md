# 🏡 Jossie SmartHome - Premium Home Goods E-commerce Platform

[![Django](https://img.shields.io/badge/Django-5.2.4-092E20?style=flat&logo=django&logoColor=white)](https://djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4.0-38B2AC?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Node.js](https://img.shields.io/badge/Node.js-18+-43853D?style=flat&logo=node.js&logoColor=white)](https://nodejs.org/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat&logo=sqlite&logoColor=white)](https://sqlite.org/)

A modern, full-featured e-commerce platform built for **Jossie SmartHome**, specializing in premium home goods. Built with Django, Django REST Framework, and modern frontend technologies.

## 🚀 **Live Demo**
*[jossiefancies.onrender.com/]*

## 📋 **Table of Contents**
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Development Setup](#-development-setup)
- [API Documentation](#-api-documentation)
- [Deployment](#-deployment)
- [Testing](#-testing)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ **Features**

### 🛍️ **E-commerce Core**
- **Product Catalog**: Comprehensive product management with categories, images, and variants
- **Shopping Cart**: Session-based cart for anonymous users, persistent cart for registered users
- **Order Management**: Complete order processing with status tracking
- **Inventory Management**: Real-time stock tracking with low-stock alerts
- **WhatsApp Integration**: Seamless order notifications via WhatsApp Business API

### 🎨 **Modern Frontend**
- **Responsive Design**: Mobile-first design with Tailwind CSS
- **Interactive UI**: Dynamic product filtering, search, and quick-view modals
- **Progressive Enhancement**: Works without JavaScript, enhanced with JS
- **Modern CSS**: Production-optimized Tailwind CSS build process
- **Accessibility**: WCAG 2.1 compliant interface

### 🔧 **Admin & Management**
- **Django Admin**: Enhanced admin interface for content management
- **REST API**: Complete API for all operations with DRF
- **Stock History**: Detailed inventory transaction tracking
- **Order Analytics**: Business intelligence and reporting
- **Email Notifications**: Automated order confirmations and admin alerts

### 🛡️ **Production Ready**
- **Security**: CSRF protection, input validation, secure file uploads
- **Performance**: Optimized queries, static file compression, CDN ready
- **Monitoring**: Comprehensive logging and error tracking
- **Testing**: 79 comprehensive test cases with 100% critical path coverage

## 🛠️ **Tech Stack**

### **Backend**
- **Django 5.2.4** - Web framework
- **Django REST Framework** - API development
- **SQLite/PostgreSQL** - Database (configurable)
- **Python 3.11+** - Programming language

### **Frontend**
- **Tailwind CSS 3.4.0** - Utility-first CSS framework
- **Vanilla JavaScript** - Modern ES6+ JavaScript
- **Iconify** - Icon system
- **Lottie** - Animations

### **DevOps & Tools**
- **Node.js 18+** - Build tools
- **Git** - Version control
- **npm** - Package management

## 🚀 **Quick Start**

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### One-Command Setup
```bash
git clone <repository-url>
cd jossie2
./build.sh
python manage.py runserver
```

Visit `http://localhost:8000` to see the application.

## 💻 **Development Setup**

### 1. **Clone the Repository**
```bash
git clone <repository-url>
cd jossie2
```

### 2. **Set Up Python Environment**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. **Set Up Node.js Dependencies**
```bash
npm install
```

### 4. **Configure Environment**
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env
```

### 5. **Initialize Database**
```bash
python manage.py migrate
python manage.py populate_data  # Load sample data
```

### 6. **Build CSS Assets**
```bash
# Development (with file watching)
npm run dev

# Production build
npm run build
```

### 7. **Start Development Server**
```bash
python manage.py runserver
```

## 🔧 **Development Workflow**

### **CSS Development**
```bash
# Watch for changes during development
npm run dev

# Build for production
npm run build
```

### **Running Tests**
```bash
# Run all tests
python manage.py test

# Run with coverage
python manage.py test --with-coverage

# Run specific test module
python manage.py test core.tests.CategoryModelTest
```

### **Database Management**
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## 📡 **API Documentation**

### **Base URL**
```
http://localhost:8000/api/
```

### **Key Endpoints**

#### **Products**
- `GET /api/products/` - List all products
- `GET /api/products/{id}/` - Get product details
- `GET /api/products/featured/` - Get featured products

#### **Categories**
- `GET /api/categories/` - List all categories
- `GET /api/categories/{id}/products/` - Get products in category

#### **Cart**
- `GET /api/cart/` - Get current cart
- `POST /api/cart/add_item/` - Add item to cart
- `PUT /api/cart/update_item/` - Update cart item
- `DELETE /api/cart/remove_item/` - Remove item from cart

#### **Orders**
- `POST /api/orders/` - Create new order
- `GET /api/orders/` - List orders (admin only)
- `PATCH /api/orders/{id}/update_status/` - Update order status

### **Authentication**
The API supports both session-based authentication for web clients and can be extended with token authentication for mobile/API clients.

## 🚀 **Deployment**

### **Production Build**
```bash
# Complete production build
./build.sh

# Manual steps:
npm install --production
npm run build
python manage.py collectstatic --noinput
python manage.py migrate
```

### **Environment Variables**
Required environment variables for production:

```bash
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:pass@host:port/dbname
WHATSAPP_BUSINESS_NUMBER=+1234567890
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### **Deployment Platforms**
- **Railway**: Use provided `railway.toml`
- **Heroku**: Use provided `Procfile`
- **DigitalOcean**: Use Docker configuration
- **AWS**: Use Elastic Beanstalk configuration

## 🧪 **Testing**

### **Test Coverage**
- **79 Test Cases** covering all critical functionality
- **Models**: Category, Product, Cart, Order, Stock History
- **API Endpoints**: Complete REST API test coverage
- **Services**: WhatsApp, Email, Order processing
- **Template Views**: All user-facing pages

### **Running Tests**
```bash
# All tests
python manage.py test

# Specific test categories
python manage.py test core.tests.ProductModelTest
python manage.py test core.tests.CartAPITest
python manage.py test core.tests.OrderServiceTest
```

## 📁 **Project Structure**
```
jossie2/
├── 📁 core/                   # Django app
│   ├── 📁 management/commands/ # Custom management commands
│   ├── 📁 migrations/         # Database migrations
│   ├── 📄 models.py           # Data models
│   ├── 📄 views.py            # Views and API endpoints
│   ├── 📄 serializers.py      # DRF serializers
│   ├── 📄 services.py         # Business logic services
│   └── 📄 tests.py            # Test suite
├── 📁 templates/              # Django templates
│   ├── 📄 base.html           # Base template
│   └── 📁 core/               # App-specific templates
├── 📁 static/                 # Static assets
│   ├── 📁 css/                # CSS source and build files
│   └── 📁 images/             # Static images
├── 📁 media/                  # User uploads
├── 📄 manage.py               # Django management script
├── 📄 requirements.txt        # Python dependencies
├── 📄 package.json            # Node.js dependencies
├── 📄 tailwind.config.js      # Tailwind CSS configuration
└── 📄 build.sh                # Production build script
```

## 🤝 **Contributing**

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### **Development Process**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### **Code Standards**
- Follow PEP 8 for Python code
- Use meaningful commit messages
- Include tests for new features
- Update documentation as needed

## 📞 **Support**

- **Email**: jossiefancies1@gmail.com
- **Phone**: +254 790 420 843
- **Documentation**: [CSS Development Guide](CSS_DEVELOPMENT.md)

## 📄 **License**

This project is proprietary software owned by **Jossie SmartHome**. All rights reserved.

---

<div align="center">

**Built with ❤️ by the Jossie SmartHome Team**

*Bringing premium home goods to your doorstep*

</div>
