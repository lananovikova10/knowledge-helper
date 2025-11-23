# YouTrack KB Helper - Web Application

A modern web interface for analyzing and maintaining YouTrack knowledge base articles. Built with Django and Material Design.

## Features

### ✅ Implemented
- **Web-based Interface**: User-friendly Material Design UI
- **Secure Credential Management**: Session-based token storage (no database persistence)
- **Stale Content Analysis**: Interactive analysis with sortable results
- **Real-time Statistics**: Visual dashboard showing key metrics
- **Responsive Design**: Works on desktop and mobile devices

### 🚧 Coming Soon
- Low engagement analysis
- Duplicate detection
- Comprehensive article statistics dashboard

## Quick Start

### 1. Install Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2. Run Database Migrations

```bash
python manage.py migrate
```

### 3. Start the Development Server

```bash
python manage.py runserver
```

The application will be available at: [http://localhost:8000](http://localhost:8000)

## Usage Guide

### First Time Setup

1. **Open the Application**
   - Navigate to http://localhost:8000 in your browser

2. **Configure Credentials**
   - Click "Configure" in the navigation bar
   - Enter your YouTrack Base URL (e.g., `https://youtrack.jetbrains.com`)
   - Enter your YouTrack API Token
   - Click "Save & Test Connection"

3. **Start Analyzing**
   - From the home page, click "Analyze Now" on the Stale Content card
   - Enter your Project ID (e.g., "JBKB", "HE")
   - Set the threshold in days (default: 180 days)
   - Click "Analyze"

### Security Features

- **Session-based Storage**: Credentials are stored only in your browser session
- **No Database Persistence**: Tokens are never saved to disk
- **Auto-expiration**: Sessions expire after 24 hours
- **Connection Testing**: Credentials are validated before being stored

### Using the Stale Content Analyzer

1. **Configure Analysis**:
   - Project ID: The YouTrack knowledge base project to analyze
   - Threshold: Number of days without updates to consider an article "stale"

2. **View Results**:
   - **Statistics Dashboard**: See total articles, stale count, and percentage
   - **Sortable Table**: Click column headers to sort by:
     - ID
     - Title
     - Days Since Update
     - View Count
     - Last Updated Date

3. **Interpret Results**:
   - **Orange badges**: Show days since last update
   - **Blue badges**: Show view counts
   - Articles are initially sorted by days since update (oldest first)

## Project Structure

```
knowledge-helper/
├── kb_portal/              # Django project settings
│   ├── settings.py        # Main configuration
│   ├── urls.py           # URL routing
│   └── wsgi.py           # WSGI application
├── analyzer/              # Main application
│   ├── models.py         # Data models
│   ├── views.py          # View logic
│   ├── urls.py           # URL patterns
│   └── templates/        # HTML templates
│       └── analyzer/
│           ├── base.html
│           ├── index.html
│           ├── credentials.html
│           └── stale_content.html
├── src/                   # Core logic (reused from CLI)
│   ├── api/              # YouTrack API client
│   ├── analyzers/        # Analysis engines
│   └── models/           # Data models
└── manage.py             # Django management script
```

## API Endpoints

### Web Pages
- `/` - Home page
- `/credentials/` - Configure YouTrack credentials
- `/stale-content/` - Stale content analysis page

### AJAX API
- `POST /api/analyze-stale/` - Run stale content analysis
  - Parameters:
    - `project_id` (required): Project ID
    - `threshold_days` (optional): Days threshold (default: 180)
  - Returns: JSON with analysis results

## Configuration

### Session Settings
Edit `kb_portal/settings.py` to customize:

```python
# Session expiration (in seconds)
SESSION_COOKIE_AGE = 86400  # 24 hours

# Session engine
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
```

### Static Files
For production deployment:

```bash
python manage.py collectstatic
```

## Development

### Running in Debug Mode

Debug mode is enabled by default in `settings.py`:

```python
DEBUG = True
```

**⚠️ Warning**: Disable debug mode in production!

### Testing Locally

1. Use `.env.local` for local credentials (not tracked by git)
2. Session data is stored in SQLite database
3. Clear sessions: `python manage.py clearsessions`

## Troubleshooting

### Port Already in Use

If port 8000 is busy:

```bash
# Use a different port
python manage.py runserver 8080
```

### Static Files Not Loading

```bash
# Collect static files
python manage.py collectstatic --noinput
```

### Session Issues

Clear all sessions:

```bash
python manage.py clearsessions
```

Or delete the database:

```bash
rm db.sqlite3
python manage.py migrate
```

### Credentials Not Working

1. Verify your YouTrack URL format is correct
2. Check your token has appropriate permissions
3. Test with the CLI tool first: `python kb-helper.py test-connection`

## Technology Stack

- **Backend**: Django 5.2
- **Frontend**: Materialize CSS (Material Design)
- **Database**: SQLite (development) / PostgreSQL (production recommended)
- **Session Storage**: Database-backed sessions
- **API Client**: Requests library
- **Analysis Engine**: Reuses CLI core logic

## Production Deployment

### Recommended Setup

1. **Use PostgreSQL** instead of SQLite
2. **Enable HTTPS** for secure token transmission
3. **Set DEBUG = False** in settings
4. **Configure ALLOWED_HOSTS** properly
5. **Use environment variables** for secrets
6. **Deploy with Gunicorn + Nginx**

### Example Production Settings

```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'kb_helper_db',
        # ... other settings
    }
}
```

## CLI vs Web Interface

Both interfaces share the same core analysis logic:

| Feature | CLI | Web |
|---------|-----|-----|
| Token Storage | `.env` file | Browser session |
| Multi-user | No | Yes |
| Sorting | Pre-sorted only | Interactive |
| Export | JSON/CSV files | Coming soon |
| Authentication | File-based | Session-based |

## Contributing

The web application reuses the core logic from the CLI tool in the `src/` directory. When adding new features:

1. Implement core logic in `src/analyzers/`
2. Add API endpoint in `analyzer/views.py`
3. Create/update template in `analyzer/templates/`
4. Update both CLI and web interfaces

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
- Check the troubleshooting section above
- Review the main README.md for CLI usage
- Test API connectivity with the CLI tool first
