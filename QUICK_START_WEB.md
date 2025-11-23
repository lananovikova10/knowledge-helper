# Quick Start Guide - Web Application

Get started with the YouTrack KB Helper web interface in 3 simple steps!

## Step 1: Start the Server

```bash
# Make sure you're in the project directory
cd knowledge-helper

# Activate virtual environment
source venv/bin/activate

# Run migrations (first time only)
python manage.py migrate

# Start the server
python manage.py runserver
```

## Step 2: Configure Your Credentials

1. **Open your browser** and go to: http://localhost:8000

2. **Click "Configure"** in the navigation bar

3. **Enter your details**:
   - **YouTrack Base URL**: Your instance URL (e.g., `https://youtrack.jetbrains.com`)
   - **API Token**: Your personal token (starts with `perm:`)

4. **Click "Save & Test Connection"**
   - The system will validate your credentials
   - If successful, you'll be redirected to the home page

## Step 3: Analyze Your KB

1. **From the home page**, click "Analyze Now" on the Stale Content card

2. **Enter analysis parameters**:
   - **Project ID**: Your KB project (e.g., "JBKB", "HE")
   - **Threshold**: Days without update to consider stale (default: 180)

3. **Click "Analyze"**
   - The system will fetch all articles
   - Results appear in an interactive table

4. **View and Sort Results**:
   - Click any column header to sort
   - See statistics at the top:
     - Total articles
     - Stale count
     - Percentage
     - Threshold used

## Features

### Statistics Dashboard
- **Total Articles**: All articles in the project
- **Stale Count**: Articles exceeding the threshold
- **Stale Percentage**: Visual metric of content health
- **Threshold Display**: Current analysis parameters

### Interactive Table
- **Sortable Columns**: Click any header to sort
- **Visual Indicators**:
  - Orange badges = Days since update
  - Blue badges = View counts
- **Detailed Information**:
  - Article ID (linked to YouTrack)
  - Title
  - Days since last update
  - Total views
  - Last update date

### Navigation
- **Home**: Overview and feature cards
- **Stale Content**: Analysis page
- **Settings**: Update credentials
- **Logout**: Clear session data

## Tips

### Getting Your API Token
1. Log in to YouTrack
2. Click your avatar → Profile
3. Go to Authentication tab
4. Click "New token..."
5. Name it "KB Helper"
6. Copy the token (starts with `perm:`)

### URL Formats
Choose the correct format for your instance:

- **Standalone**: `https://youtrack.example.com`
- **Cloud**: `https://example.youtrack.cloud`
- **MyJetBrains**: `https://example.myjetbrains.com/youtrack`

Don't include `/api` - it's added automatically!

### Security
- Credentials stored only in browser session
- Sessions expire after 24 hours
- No database persistence
- Click "Logout" to clear immediately

## Troubleshooting

### "Connection failed"
- Check your URL format (no `/api` at the end)
- Verify token is wrapped in quotes if it contains `=`
- Ensure token has appropriate permissions
- Test with CLI first: `python kb-helper.py test-connection`

### Server won't start
```bash
# Check if port 8000 is busy
lsof -i :8000

# Use a different port
python manage.py runserver 8080
```

### Page not loading
```bash
# Clear browser cache
# Or try incognito/private mode

# Check server logs in terminal
# Look for error messages
```

### Forgot to activate venv
```bash
# You'll see: ModuleNotFoundError
# Solution:
source venv/bin/activate
```

## Next Steps

### For Daily Use
1. Start server: `python manage.py runserver`
2. Visit: http://localhost:8000
3. Enter credentials (if needed)
4. Run analysis!

### For Production
See [WEB_APP_README.md](WEB_APP_README.md) for:
- PostgreSQL setup
- HTTPS configuration
- Gunicorn + Nginx deployment
- Environment variables

### For Automation
Use the CLI instead:
```bash
python kb-helper.py stale-content JBKB --format json --output report.json
```

## Screenshots & Visual Guide

### Home Page
- Feature cards showing available analyzers
- Connection status indicator
- Quick navigation

### Credentials Page
- Simple two-field form
- Helpful hints and examples
- Step-by-step token guide
- Instant validation

### Analysis Page
- Configuration form
- Loading indicator
- Statistics dashboard (4 cards)
- Sortable results table
- Color-coded badges

## Support

- **Documentation**: See [WEB_APP_README.md](WEB_APP_README.md)
- **CLI Guide**: See [README.md](README.md)
- **Quick Reference**: See [QUICKSTART.md](QUICKSTART.md)

Enjoy analyzing your knowledge base! 🎉
