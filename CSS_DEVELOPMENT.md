# CSS Development Guide - Jossie SmartHome

This project uses **Tailwind CSS** with a proper build process instead of the CDN for production-ready performance.

## 🚀 Quick Start

### Development Mode (Auto-rebuild CSS on changes)
```bash
npm run dev
```

### Production Build (Minified CSS)
```bash
npm run build
```

### Complete Build (CSS + Django static files)
```bash
./build.sh
```

## 📁 File Structure

```
├── static/css/
│   ├── input.css      # Source CSS with Tailwind directives
│   └── output.css     # Built CSS (auto-generated)
├── tailwind.config.js # Tailwind configuration
├── postcss.config.js  # PostCSS configuration
└── package.json       # Node.js dependencies and scripts
```

## 🎨 Custom Styling

### Tailwind Configuration
The `tailwind.config.js` includes:
- **Custom Colors**: Primary orange theme, success green, dark variants
- **Custom Fonts**: Lato font family
- **Custom Animations**: Fade-in, slide effects, glow effects
- **Custom Box Shadows**: Modern cards, glow effects
- **Custom Spacing**: Additional spacing utilities

### Custom CSS Classes
In `static/css/input.css`:
- `.modern-card` - Elevated card with hover effects
- `.glass-nav` - Glassmorphism navigation bar
- `.product-card` - Enhanced product card styling
- `.hover-glow` - Orange glow effect on hover
- `.loading-spinner` - Consistent loading animation
- `.line-clamp-2/3` - Text truncation utilities

## 🔧 Development Workflow

1. **Edit styles** in `static/css/input.css` or use Tailwind classes in templates
2. **Run development build**: `npm run dev` (watches for changes)
3. **Test changes** in your browser
4. **Build for production**: `npm run build` when ready to deploy

## 📦 Production Deployment

1. Run the complete build process:
   ```bash
   ./build.sh
   ```

2. This will:
   - Install npm dependencies
   - Build minified CSS
   - Collect Django static files
   - Run database migrations

## 🛠️ Available Scripts

- `npm run dev` - Development build with file watching
- `npm run build` - Production build (minified)
- `npm run start` - Start Django development server
- `npm run update-browserslist` - Update browser compatibility data

## 📋 Benefits of This Setup

✅ **Production Ready**: No CDN dependency, faster load times  
✅ **Optimized**: Only includes CSS classes actually used in templates  
✅ **Customizable**: Full control over Tailwind configuration  
✅ **Maintainable**: Clear separation of source and built files  
✅ **Modern**: Uses latest Tailwind CSS features and plugins

## 🎯 Template Integration

Templates now use:
```html
{% load static %}
<link href="{% static 'css/output.css' %}" rel="stylesheet">
```

Instead of:
```html
<script src="https://cdn.tailwindcss.com"></script>
```

This eliminates the production warning and improves performance significantly.