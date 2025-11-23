# Quick Start Cheat Sheet

## First Time Setup

```bash
# 1. Run automated setup
./setup.sh

# 2. Edit your credentials
nano .env

# 3. Test connection
source venv/bin/activate
python kb-helper.py test-connection
```

## Daily Usage

```bash
# Always activate the virtual environment first!
source venv/bin/activate

# Analyze stale content
python kb-helper.py stale-content YOUR_PROJECT_ID

# When done
deactivate
```

## Common Commands

```bash
# Test connection
python kb-helper.py test-connection

# Test with specific project
python kb-helper.py test-connection --project-id HE

# Stale content with defaults (180 days)
python kb-helper.py stale-content HE

# Custom threshold (90 days)
python kb-helper.py stale-content HE --threshold 90

# Save as JSON
python kb-helper.py stale-content HE --format json --output report.json

# Save as CSV
python kb-helper.py stale-content HE --format csv --output report.csv

# Get help
python kb-helper.py --help
python kb-helper.py stale-content --help
```

## Troubleshooting

### Virtual environment not activated
**Symptom**: `ModuleNotFoundError` or similar errors

**Solution**:
```bash
source venv/bin/activate
```
You should see `(venv)` in your prompt.

### Missing credentials
**Symptom**: "Configuration Error: YOUTRACK_TOKEN is not set"

**Solution**:
```bash
cp .env.example .env
nano .env
# Add your YOUTRACK_BASE_URL and YOUTRACK_TOKEN
# URL format depends on your instance type:
#   Standalone: https://youtrack.example.com
#   Cloud: https://example.youtrack.cloud
#   MyJetBrains: https://example.myjetbrains.com/youtrack
```

### Can't find python3
**Try**:
```bash
python --version  # Check if python works
python -m venv venv  # Use python instead of python3
```

### Setup script not executable
```bash
chmod +x setup.sh
./setup.sh
```

## File Structure

```
.env                    ← Your credentials (NOT in git)
kb-helper.py           ← Main script
setup.sh               ← Automated setup
venv/                  ← Virtual environment (created by setup)
src/                   ← Source code
README.md              ← Full documentation
```

## Getting Your YouTrack Token

1. Go to your YouTrack instance
2. Avatar → Profile → Authentication tab
3. "New token..." button
4. Name it "KB Helper"
5. Copy token (starts with `perm:`)
6. Paste into `.env` file

## Windows Users

Replace:
- `source venv/bin/activate` → `venv\Scripts\activate`
- `./setup.sh` → Use manual setup from README.md
- `nano` → `notepad` or your preferred editor
