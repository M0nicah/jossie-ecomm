# 🚀 Quick Start Guide - Jossie Fancies

Get the Jossie Fancies e-commerce platform up and running in minutes!

## ⚡ **One-Command Setup**

```bash
git clone <your-repository-url>
cd jossie2
./build.sh
python manage.py runserver
```

Visit `http://localhost:8000` 🎉

## 📋 **Prerequisites**

- **Python 3.11+** ([Download](https://python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/))

## 🛠️ **Manual Setup** (if build.sh doesn't work)

### 1. **Python Setup**
```bash
# Create virtual environment
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate
# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. **Database Setup**
```bash
python manage.py migrate
python manage.py populate_data  # Load sample data
```

### 3. **Frontend Setup**
```bash
npm install
npm run build  # Build production CSS
```

### 4. **Start Development**
```bash
# Terminal 1: Django server
python manage.py runserver

# Terminal 2: CSS development (optional)
npm run dev  # Watch for CSS changes
```

## 🎯 **Quick Commands**

| Task | Command |
|------|---------|
| **Start server** | `python manage.py runserver` |
| **Run tests** | `python manage.py test` |
| **Build CSS** | `npm run build` |
| **Watch CSS** | `npm run dev` |
| **Create admin** | `python manage.py createsuperuser` |
| **Load sample data** | `python manage.py populate_data` |

## 📁 **Key Files**

- **`manage.py`** - Django management commands
- **`requirements.txt`** - Python dependencies
- **`package.json`** - Node.js dependencies
- **`tailwind.config.js`** - CSS configuration
- **`core/`** - Main Django app
- **`templates/`** - HTML templates
- **`static/`** - CSS, JS, and images

## 🌐 **Default URLs**

- **Home**: `http://localhost:8000/`
- **Products**: `http://localhost:8000/products/`
- **Admin**: `http://localhost:8000/admin/`
- **API**: `http://localhost:8000/api/`

## 🔧 **Environment Setup**

1. Copy environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your settings:
   ```bash
   SECRET_KEY=your-secret-key
   DEBUG=True
   WHATSAPP_BUSINESS_NUMBER=+254794748719
   ```

## 🧪 **Testing**

```bash
# Run all tests
python manage.py test

# Run specific tests
python manage.py test core.tests.ProductModelTest
```

## 🚀 **Production Deployment**

1. **Build for production**:
   ```bash
   ./build.sh
   ```

2. **Deploy to your platform**:
   - Railway: `railway up`
   - Heroku: `git push heroku main`
   - See [DEPLOYMENT.md](DEPLOYMENT.md) for details

## 🆘 **Troubleshooting**

| Problem | Solution |
|---------|----------|
| **Command not found** | Make sure Python/Node.js are installed |
| **Permission denied** | Run `chmod +x build.sh` |
| **CSS not loading** | Run `npm run build` |
| **Database errors** | Run `python manage.py migrate` |
| **Port already in use** | Use `python manage.py runserver 8001` |

## 📚 **Next Steps**

1. **Read the docs**: [README.md](README.md)
2. **Development**: [CONTRIBUTING.md](CONTRIBUTING.md)
3. **CSS Guide**: [CSS_DEVELOPMENT.md](CSS_DEVELOPMENT.md)
4. **Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md)
5. **Security**: [SECURITY.md](SECURITY.md)

## 💬 **Need Help?**

- **Email**: jossiefancies1@gmail.com
- **Issues**: Create a GitHub issue
- **Phone**: +254 790 420 843

---

**Happy coding! 🎉**