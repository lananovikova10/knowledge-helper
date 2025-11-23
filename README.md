# YouTrack Knowledge Base Helper

A comprehensive tool for knowledge base maintainers to analyze and maintain YouTrack KB articles. Available as both a **CLI tool** and a **web application** with Material Design interface.

## 🎨 Two Interfaces Available

### 1. **Web Application** (NEW!)
- Modern Material Design interface
- User-friendly forms and interactive tables
- Real-time statistics dashboard
- Sortable results with visual indicators
- Session-based credential management

👉 **[See Web App Documentation](WEB_APP_README.md)**

### 2. **Command Line Interface**
- Fast and scriptable
- Multiple output formats (table, JSON, CSV)
- Perfect for automation and CI/CD
- File-based configuration

## Features

### ✅ Stale Content Detection (Implemented)
- Identify articles that haven't been updated for a configurable time period
- Track last update timestamps for all articles
- Configurable threshold for "stale" articles (default: 180 days)
- Generate reports sorted by last update date (oldest first)
- View counts for each article
- Multiple output formats: web interface, table, JSON, CSV

### 🚧 Coming Soon
- Low engagement analysis (articles with low view counts)
- Duplicate detection using NLP techniques
- Article statistics dashboard with sorting capabilities

## Quick Start

### Automated Setup (Recommended)

```bash
# Run the setup script
./setup.sh
```

The script will:
- Create a Python virtual environment
- Install all dependencies
- Help you create a `.env` configuration file

### Manual Setup

1. **Create and activate virtual environment**:
   ```bash
   # Create virtual environment
   python3 -m venv venv

   # Activate it (macOS/Linux)
   source venv/bin/activate

   # Activate it (Windows)
   venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your YouTrack credentials**:
   ```bash
   # Copy the example file
   cp .env.example .env

   # Edit with your credentials
   nano .env
   ```

   Add your credentials (use the correct URL format for your instance):
   ```
   # Choose the correct format based on your YouTrack instance:
   # Standalone/InCloud: https://youtrack.example.com
   # Cloud (default): https://example.youtrack.cloud
   # Cloud (MyJetBrains): https://example.myjetbrains.com/youtrack

   YOUTRACK_BASE_URL=https://youtrack.jetbrains.com
   YOUTRACK_TOKEN="perm:your_token_here"
   STALE_THRESHOLD_DAYS=180
   ```

   **Important Notes**:
   - The tool automatically appends `/api` to your base URL, so don't include it yourself
   - If your token contains `=` or other special characters, wrap it in quotes: `YOUTRACK_TOKEN="your_token_here"`
   - You can use `.env.local` for local overrides (useful if sharing the project)

### How to Get Your YouTrack Token

1. Log in to your YouTrack instance
2. Click your avatar → **Profile**
3. Go to **Authentication** tab
4. Click **"New token..."** under "Tokens"
5. Give it a name (e.g., "KB Helper") and set scope to read articles
6. Copy the token (starts with `perm:`) and paste it into your `.env` file

### Verify Setup

```bash
# Make sure virtual environment is activated (you should see (venv) in your prompt)
python kb-helper.py test-connection
```

## 🚀 Which Interface Should You Use?

### Use the **Web Application** if you:
- Prefer a visual, point-and-click interface
- Want interactive sorting and filtering
- Need to share access with team members
- Like real-time statistics dashboards

**Start the web app:**
```bash
python manage.py migrate
python manage.py runserver
# Visit http://localhost:8000
```

### Use the **CLI** if you:
- Need to automate analysis (scripts, cron jobs)
- Want to export reports to files (JSON, CSV)
- Prefer command-line workflows
- Need to integrate with CI/CD pipelines

**Use the CLI:**
```bash
python kb-helper.py stale-content YOUR_PROJECT_ID
```

## Usage

### Test Connection

Before running analysis, test your connection:

```bash
python kb-helper.py test-connection
```

Test connection with specific project access:

```bash
python kb-helper.py test-connection --project-id HE
```

### Stale Content Analysis

Basic usage with default threshold (180 days):

```bash
python kb-helper.py stale-content PROJECT_ID
```

Example:
```bash
python kb-helper.py stale-content HE
```

#### Options

**Custom threshold** (e.g., 90 days):
```bash
python kb-helper.py stale-content HE --threshold 90
```

**Output as JSON**:
```bash
python kb-helper.py stale-content HE --format json
```

**Save report to file**:
```bash
python kb-helper.py stale-content HE --format json --output reports/stale-articles.json
```

**Save as CSV**:
```bash
python kb-helper.py stale-content HE --format csv --output reports/stale-articles.csv
```

### Advanced Configuration

You can create a `config.yaml` file for more detailed configuration:

```bash
cp config.example.yaml config.yaml
```

Edit `config.yaml` to customize settings, then use it:

```bash
python kb-helper.py --config config.yaml stale-content HE
```

## Output Examples

### Table Output (Default)

```
======================================================================
Stale Content Analysis Report
======================================================================
Project ID: HE
Threshold: 180 days
Generated: 2025-01-22 14:30:00

Total articles: 1250
Stale articles: 127 (10.2%)
======================================================================

+--------+--------------------------------------------------+--------------+--------------------+-------+
| ID     | Title                                            | Last Updated | Days Since Update  | Views |
+--------+--------------------------------------------------+--------------+--------------------+-------+
| HE-123 | Getting Started with API Integration             | 2023-05-15   | 587                | 1234  |
| HE-456 | Database Configuration Guide                     | 2023-06-20   | 551                | 892   |
| HE-789 | Legacy Authentication Methods                    | 2023-07-10   | 531                | 456   |
+--------+--------------------------------------------------+--------------+--------------------+-------+
```

### JSON Output

```json
{
  "project_id": "HE",
  "threshold_days": 180,
  "total_articles": 1250,
  "stale_count": 127,
  "stale_percentage": 10.16,
  "generated_at": "2025-01-22T14:30:00",
  "articles": [
    {
      "id": "HE-123",
      "summary": "Getting Started with API Integration",
      "created": "2022-01-15T10:00:00",
      "updated": "2023-05-15T14:30:00",
      "days_since_update": 587,
      "view_count": 1234
    }
  ]
}
```

## Project Structure

```
knowledge-helper/
├── src/
│   ├── api/
│   │   └── client.py          # YouTrack API client
│   ├── models/
│   │   └── article.py         # Article data models
│   ├── analyzers/
│   │   └── stale_content.py   # Stale content analyzer
│   ├── config.py              # Configuration management
│   └── cli.py                 # CLI interface
├── kb-helper.py               # Main entry point
├── requirements.txt           # Python dependencies
├── .env.example              # Example environment configuration
├── config.example.yaml       # Example YAML configuration
└── README.md                 # This file
```

## API Information

This tool uses both documented and undocumented YouTrack APIs:

- **Documented API**: [YouTrack REST API](https://www.jetbrains.com/help/youtrack/devportal/youtrack-rest-api.html)
- **Undocumented API**: `/api/admin/projects/{projectId}/articles` with view counters

The undocumented endpoint provides additional metadata including:
- View statistics per article
- Detailed view history
- Extended article metadata

## Troubleshooting

### "Configuration Error: YOUTRACK_TOKEN is not set"

Make sure you have created a `.env` file with your YouTrack credentials. See the Configuration section above.

### "ERROR: Failed to connect to YouTrack"

1. **Verify your `YOUTRACK_BASE_URL` is correct** - The URL format varies by instance type:
   - **Standalone/InCloud**: `https://youtrack.example.com` (no /api suffix)
   - **Cloud (default)**: `https://example.youtrack.cloud` (no /api suffix)
   - **Cloud (MyJetBrains)**: `https://example.myjetbrains.com/youtrack` (include /youtrack, no /api)

   The tool automatically appends `/api` - don't include it in your base URL!

2. **Check your token format** - If your token contains `=` signs or special characters, wrap it in quotes:
   ```
   YOUTRACK_TOKEN="perm-abc123=.xyz456=.token789"
   ```
   Without quotes, the `=` characters will be misinterpreted.

3. Check that your token is valid and not expired
4. Ensure your token has appropriate permissions to access KB articles
5. Run `python kb-helper.py test-connection` to diagnose the issue

### "Project not found or not accessible"

1. Verify the project ID is correct (case-sensitive)
2. Ensure your token has permissions to access that project
3. Check if the project is a KB project (not a regular issue tracker project)

## Contributing

This is an active development project. Future features include:

- Low engagement analysis
- Duplicate detection
- Article statistics dashboard
- Web-based interface
- Automated notifications

## License

MIT License - feel free to use and modify as needed.

## Support

For issues related to:
- **YouTrack API**: See [official documentation](https://www.jetbrains.com/help/youtrack/devportal/youtrack-rest-api.html)
- **This tool**: Open an issue in the project repository
