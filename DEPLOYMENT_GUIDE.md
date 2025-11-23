# KB Helper - Deployment Guide

## 📋 Pre-Deployment Checklist

### ✅ Static Files
- [ ] All CSS files are in `analyzer/static/analyzer/css/`
- [ ] All templates have `{% load static %}` at the top
- [ ] CSS links use `{% static 'analyzer/css/filename.css' %}`

### ✅ Settings Configuration
```python
# kb_portal/settings.py

# Static files configuration
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# For development
DEBUG = True  # Set to False in production

# For production
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']
```

### ✅ Dependencies
```bash
# Check requirements.txt includes:
Django>=4.0
django-material-admin>=1.8.6
# ... other dependencies
```

---

## 🚀 Development Deployment

### 1. Activate Virtual Environment
```bash
# On macOS/Linux
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Migrations
```bash
python manage.py migrate
```

### 4. Collect Static Files (Optional for Dev)
```bash
# Not required in development (DEBUG=True)
# Django serves static files automatically from app directories
python manage.py collectstatic --noinput
```

### 5. Run Development Server
```bash
python manage.py runserver

# Server will start at http://127.0.0.1:8000
```

### 6. Test the Application
Visit these URLs and verify styling:
- http://127.0.0.1:8000/ - Home page with feature cards
- http://127.0.0.1:8000/stale-content/ - Stale content analysis
- http://127.0.0.1:8000/low-engagement/ - Low engagement analysis
- http://127.0.0.1:8000/duplicates/ - Duplicate detection

---

## 🏭 Production Deployment

### 1. Update Settings for Production
```python
# kb_portal/settings.py

DEBUG = False

ALLOWED_HOSTS = [
    'yourdomain.com',
    'www.yourdomain.com',
    'your-server-ip',
]

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/kb-helper/staticfiles/'  # Adjust path
```

### 2. Collect Static Files
```bash
python manage.py collectstatic --noinput

# This copies all static files to STATIC_ROOT
# Files will be at: /var/www/kb-helper/staticfiles/analyzer/css/
```

### 3. Web Server Configuration

#### Option A: Nginx + Gunicorn
```nginx
# /etc/nginx/sites-available/kb-helper

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Static files
    location /static/ {
        alias /var/www/kb-helper/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files (if any)
    location /media/ {
        alias /var/www/kb-helper/media/;
        expires 30d;
    }

    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Start Gunicorn:**
```bash
gunicorn kb_portal.wsgi:application \
    --bind 127.0.0.1:8000 \
    --workers 3 \
    --timeout 60
```

#### Option B: Apache + mod_wsgi
```apache
# /etc/apache2/sites-available/kb-helper.conf

<VirtualHost *:80>
    ServerName yourdomain.com
    ServerAlias www.yourdomain.com

    # Static files
    Alias /static/ /var/www/kb-helper/staticfiles/
    <Directory /var/www/kb-helper/staticfiles>
        Require all granted
        ExpiresActive On
        ExpiresDefault "access plus 1 month"
    </Directory>

    # WSGI
    WSGIDaemonProcess kb_helper python-home=/path/to/venv python-path=/path/to/kb-helper
    WSGIProcessGroup kb_helper
    WSGIScriptAlias / /path/to/kb-helper/kb_portal/wsgi.py

    <Directory /path/to/kb-helper/kb_portal>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>
</VirtualHost>
```

### 4. Verify Static Files Are Served
```bash
# Check files exist
ls -la /var/www/kb-helper/staticfiles/analyzer/css/

# Should see:
# base.css
# index.css
# analysis.css
# duplicates.css

# Test in browser
curl http://yourdomain.com/static/analyzer/css/base.css
```

---

## 🧪 Testing Checklist

### Visual Testing
```bash
# After deployment, verify each page renders correctly
```

#### Home Page (/)
- [ ] Feature cards display with gradients
- [ ] Cards have hover effects (lift + shadow)
- [ ] Icons display correctly
- [ ] Responsive on mobile (cards stack)
- [ ] Export buttons styled correctly

#### Stale Content (/stale-content/)
- [ ] Statistics cards show icons and gradients
- [ ] Form card has top accent border
- [ ] Table displays with gradient header
- [ ] Table data shows clean text (no colored bubbles)
- [ ] "Days since update" shows as orange text
- [ ] "Views" shows as blue text
- [ ] Row hover effects work
- [ ] Sorting works correctly

#### Low Engagement (/low-engagement/)
- [ ] Statistics cards show icons and gradients
- [ ] Form card has top accent border
- [ ] Table displays with gradient header
- [ ] Table data shows clean text (no colored bubbles)
- [ ] Engagement scores color-coded (red/orange/green)
- [ ] Row hover effects work
- [ ] Sorting works correctly

#### Duplicates (/duplicates/)
- [ ] Statistics cards show icons and gradients
- [ ] Duplicate pair cards have orange accent border
- [ ] Confidence badges display correctly
- [ ] Similarity meters show progress bars
- [ ] Article comparison boxes side-by-side
- [ ] Hover effects work on all cards

### Browser Testing
- [ ] Chrome/Edge (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Mobile Safari (iOS)
- [ ] Chrome Mobile (Android)

### Responsive Testing
```bash
# Use browser DevTools to test these breakpoints
```
- [ ] 375px (iPhone SE) - Mobile layout
- [ ] 768px (iPad) - Tablet layout
- [ ] 1920px (Desktop) - Full layout

### Functional Testing
- [ ] Forms submit correctly
- [ ] AJAX requests work
- [ ] Export buttons function
- [ ] Navigation works
- [ ] Login/logout functions
- [ ] Error messages display properly

### Performance Testing
```bash
# Use browser DevTools Network tab
```
- [ ] CSS files load quickly (< 100ms)
- [ ] Total page load < 2 seconds
- [ ] No console errors
- [ ] No 404s for static files

---

## 🐛 Troubleshooting

### Issue: CSS Not Loading / 404 Errors

**Symptoms:**
- Page looks unstyled
- Browser console shows 404 errors for CSS files
- Styling reverts to basic Materialize

**Solutions:**

1. **Check static files are collected:**
```bash
python manage.py collectstatic --noinput
ls -la staticfiles/analyzer/css/
```

2. **Verify STATIC_ROOT and STATIC_URL settings:**
```python
# settings.py
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

3. **Check web server configuration:**
```bash
# Nginx
sudo nginx -t
sudo systemctl restart nginx

# Apache
sudo apache2ctl configtest
sudo systemctl restart apache2
```

4. **Verify file permissions:**
```bash
chmod -R 755 staticfiles/
chown -R www-data:www-data staticfiles/  # Adjust user/group
```

### Issue: Colored Bubbles Still Showing in Tables

**Symptoms:**
- Table cells show colored pill bubbles
- Text is hard to read

**Solutions:**

1. **Hard refresh browser:**
```
Ctrl+Shift+R (Windows/Linux)
Cmd+Shift+R (Mac)
```

2. **Clear browser cache completely**

3. **Check CSS file has latest changes:**
```bash
grep "Table Data - Clean" analyzer/static/analyzer/css/analysis.css
# Should show: /* Table Data - Clean, readable text without badges */
```

4. **Verify template uses `data-value` class:**
```bash
grep "data-value" analyzer/templates/analyzer/stale_content.html
# Should show: class="data-value orange"
```

### Issue: Cards Look Flat / No Shadows

**Symptoms:**
- Cards appear flat
- No hover effects
- Missing rounded corners

**Solutions:**

1. **Check base.css is loading:**
```html
<!-- View page source, look for: -->
<link rel="stylesheet" href="/static/analyzer/css/base.css">
```

2. **Verify CSS variables are defined:**
```bash
grep "CSS Variables" analyzer/static/analyzer/css/base.css
```

3. **Check for CSS conflicts:**
- Open browser DevTools
- Inspect card element
- Check if styles are being overridden

### Issue: Slow Page Load

**Symptoms:**
- Pages take > 3 seconds to load
- CSS files load slowly

**Solutions:**

1. **Enable compression in web server:**
```nginx
# Nginx
gzip on;
gzip_types text/css application/javascript;
```

2. **Set cache headers:**
```nginx
location /static/ {
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

3. **Use CDN for Materialize CSS** (already configured)

---

## 🔍 Verification Commands

### Check Django Configuration
```bash
python manage.py check
python manage.py check --deploy
```

### Check Static Files
```bash
# Development
python manage.py findstatic analyzer/css/base.css

# Production
ls -la /var/www/kb-helper/staticfiles/analyzer/css/
```

### Check Web Server
```bash
# Nginx
sudo nginx -t
curl -I http://yourdomain.com/static/analyzer/css/base.css

# Apache
sudo apache2ctl configtest
curl -I http://yourdomain.com/static/analyzer/css/base.css
```

### Check Logs
```bash
# Django logs
tail -f logs/django.log

# Nginx logs
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log

# Apache logs
tail -f /var/log/apache2/error.log
tail -f /var/log/apache2/access.log
```

---

## 📊 Performance Benchmarks

### Target Metrics
- **Page Load Time**: < 2 seconds
- **CSS Load Time**: < 100ms per file
- **First Contentful Paint**: < 1.5 seconds
- **Time to Interactive**: < 3 seconds

### Testing Tools
```bash
# Lighthouse (Chrome DevTools)
# - Performance score: > 90
# - Accessibility score: > 90
# - Best Practices: > 90

# WebPageTest
https://www.webpagetest.org/

# GTmetrix
https://gtmetrix.com/
```

---

## 🔐 Security Checklist

### Production Security
- [ ] `DEBUG = False`
- [ ] `ALLOWED_HOSTS` configured
- [ ] `SECRET_KEY` is secret and unique
- [ ] SSL/TLS certificate installed
- [ ] `SECURE_SSL_REDIRECT = True`
- [ ] `SESSION_COOKIE_SECURE = True`
- [ ] `CSRF_COOKIE_SECURE = True`
- [ ] Security headers configured
- [ ] Static files served with proper CORS
- [ ] Database credentials secured
- [ ] Environment variables used for secrets

---

## 📝 Rollback Plan

### If Issues Occur in Production

1. **Quick Rollback:**
```bash
# Restore previous staticfiles directory
cp -r /backup/staticfiles /var/www/kb-helper/

# Restart web server
sudo systemctl restart nginx
```

2. **Revert Code Changes:**
```bash
git revert HEAD
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

3. **Clear CDN Cache** (if using CDN)

---

## 📞 Support

### Getting Help

1. **Check Documentation:**
   - [UI_MODERNIZATION.md](fleet-file://c8nucled93tur19j97fi/Users/Svetlana.Novikova/knowledge-helper/UI_MODERNIZATION.md?type=file&root=%252F) - Technical details
   - [CSS_REFERENCE.md](fleet-file://c8nucled93tur19j97fi/Users/Svetlana.Novikova/knowledge-helper/CSS_REFERENCE.md?type=file&root=%252F) - CSS class reference

2. **Check Browser Console:**
   - F12 → Console tab
   - Look for errors

3. **Check Network Tab:**
   - F12 → Network tab
   - Filter by CSS
   - Check for 404s

4. **Verify File Paths:**
   - All paths should be absolute
   - Use `{% static %}` template tag
   - Check STATIC_URL setting

---

## ✅ Post-Deployment Checklist

After deployment, verify:
- [ ] Home page loads with modern styling
- [ ] All analysis pages render correctly
- [ ] Tables display clean text (no bubbles)
- [ ] Export buttons work
- [ ] Mobile responsive design works
- [ ] No console errors
- [ ] No 404 errors for static files
- [ ] Performance metrics are good
- [ ] Security headers present
- [ ] SSL certificate valid

---

**Last Updated**: 2025-11-23
**Version**: 1.0
