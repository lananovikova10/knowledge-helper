# Quick Setup Guide

## Step 1: Create Virtual Environment

```bash
# Create a virtual environment named 'venv'
python3 -m venv venv
```

## Step 2: Activate Virtual Environment

### On macOS/Linux:
```bash
source venv/bin/activate
```

### On Windows:
```bash
venv\Scripts\activate
```

You should see `(venv)` prefix in your terminal prompt when activated.

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Configure Your Credentials

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file with your credentials
nano .env   # or use your preferred editor (vim, code, etc.)
```

Add your YouTrack credentials:
```
YOUTRACK_BASE_URL=https://youtrack.jetbrains.com
YOUTRACK_TOKEN=perm:your_token_here
STALE_THRESHOLD_DAYS=180
```

## Step 5: Test the Setup

```bash
# Test connection
python kb-helper.py test-connection

# If you have a project ID, test with it
python kb-helper.py test-connection --project-id YOUR_PROJECT_ID
```

## Step 6: Run Analysis

```bash
# Analyze stale content
python kb-helper.py stale-content YOUR_PROJECT_ID

# With custom threshold
python kb-helper.py stale-content YOUR_PROJECT_ID --threshold 90

# Save as JSON
python kb-helper.py stale-content YOUR_PROJECT_ID --format json --output report.json
```

## Deactivating Virtual Environment

When you're done:
```bash
deactivate
```

## Troubleshooting

### "python3: command not found"
Try `python` instead of `python3`:
```bash
python -m venv venv
```

### "pip: command not found"
Try:
```bash
python -m pip install -r requirements.txt
```

### Permission denied
On macOS/Linux, you might need to make the script executable:
```bash
chmod +x kb-helper.py
./kb-helper.py test-connection
```

### Virtual environment already exists
If you need to recreate it:
```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```
