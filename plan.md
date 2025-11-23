# Knowledge Base Helper for YouTrack - Implementation Plan

## Project Overview
A helper service for knowledge base maintainers that leverages both documented and undocumented YouTrack APIs to provide insights and analytics for KB articles.

## Core Features

### 1. Stale Content Detection ✅ COMPLETED
**Objective**: Identify articles that haven't been updated for a long time
- ✅ Track last update timestamps for all articles
- ✅ Configurable threshold for "stale" articles (e.g., 6 months, 1 year)
- ✅ Generate reports of articles needing review
- ✅ Sort by last update date (oldest first)
- ✅ CLI interface with table/JSON/CSV output
- ✅ Web interface with Material Design
- ✅ Interactive sorting and filtering

**Status**: Fully implemented in both CLI and Web interfaces

### 2. Low Engagement Analysis ✅ COMPLETED
**Objective**: Surface articles with low view counts
- ✅ Collect view statistics for all articles (already fetched)
- ✅ Identify articles below view count threshold
- ✅ Consider article age when determining "low views"
- ✅ Flag potentially irrelevant or poorly discoverable content
- ✅ Age-normalized scoring system (views per day)
- ✅ CLI interface with table/JSON/CSV output
- ✅ Web interface with Material Design
- ✅ Interactive sorting and filtering
- ✅ Color-coded engagement scores (red/orange/green)

**Status**: Fully implemented in both CLI and Web interfaces

### 3. Duplicate Detection ✅ COMPLETED
**Objective**: Find possible duplicate articles
- ✅ Text similarity analysis using:
  - ✅ Title comparison (exact and fuzzy matching with rapidfuzz)
  - ✅ Content similarity algorithms (TF-IDF + cosine similarity with scikit-learn)
  - Tag/category overlap (skipped - not critical for MVP)
- ✅ Generate confidence scores for duplicates (weighted: 40% title, 60% content)
- ✅ Present side-by-side comparison of potential duplicates
- ✅ CLI interface with table/JSON output
- ✅ Web interface with Material Design
- ✅ Interactive cards showing similarity analysis
- ✅ Color-coded confidence levels (high/medium/low)
- ✅ Graceful degradation without NLP libraries

**Status**: Fully implemented in both CLI and Web interfaces

### 4. Article Statistics Dashboard 🔲 TODO
**Objective**: Provide sortable article statistics per KB project
- ✅ View counts per article (available in stale content)
- ✅ Last update dates (available in stale content)
- 🔲 Author information
- 🔲 Article status (published, draft, archived)
- ✅ Sort capabilities: views, date, title (in web interface)
- ✅ Export capabilities (CSV, JSON in CLI)

**Status**: Partially implemented, needs dedicated view

## Technical Architecture

### 1. API Integration Layer
**YouTrack API Types:**
- **Documented APIs**: Official REST API for article metadata, projects
- **Undocumented APIs**: Analytics endpoints, advanced statistics (need to reverse-engineer)

**Components:**
- API client with authentication (token-based)
- Rate limiting and retry logic
- Response caching to minimize API calls
- Error handling and logging

### 2. Data Collection Module
- Fetch all articles from specified KB project(s)
- Collect metadata: title, content, views, dates, authors, tags
- Store data locally for analysis (SQLite or JSON)
- Incremental updates to reduce API load

### 3. Analysis Engine
**Modules:**
- **Stale Content Analyzer**: Date-based filtering and ranking
- **Engagement Analyzer**: View count analysis with age normalization
- **Duplicate Detector**: NLP-based similarity matching
- **Statistics Generator**: Aggregation and sorting

### 4. Reporting Interface
**Options:**
- CLI tool with formatted output
- Web dashboard (optional, future enhancement)
- Report export (JSON, CSV, HTML)

## Technology Stack

### Backend
- **Language**: Python 3.9+
- **HTTP Client**: `requests` or `httpx`
- **Data Processing**: `pandas` for data manipulation
- **NLP/Similarity**:
  - `scikit-learn` for TF-IDF and cosine similarity
  - `fuzzywuzzy` or `rapidfuzz` for fuzzy string matching
- **Storage**: SQLite for local caching
- **Configuration**: YAML or JSON config files

### Dependencies
```
requests>=2.31.0
pandas>=2.0.0
scikit-learn>=1.3.0
rapidfuzz>=3.0.0
pyyaml>=6.0
python-dotenv>=1.0.0
tabulate>=0.9.0  # for CLI table output
```

## Implementation Phases

### Phase 1: Foundation (Core Setup)
1. Project structure setup
2. YouTrack API client implementation
3. Authentication and configuration management
4. Basic article fetching functionality
5. Data models for articles and statistics

### Phase 2: Data Collection
1. Implement article metadata collection
2. Set up local caching/storage
3. Build incremental update mechanism
4. Add logging and error handling

### Phase 3: Analysis Features
1. **Stale content detector**
   - Date comparison logic
   - Configurable thresholds
   - Report generation
2. **Low views analyzer**
   - View count analysis
   - Age-normalized scoring
   - Threshold-based filtering
3. **Article statistics**
   - Sorting functionality
   - Filtering by project
   - Export capabilities

### Phase 4: Duplicate Detection
1. Text preprocessing (cleaning, normalization)
2. Title similarity matching
3. Content similarity analysis (TF-IDF + cosine similarity)
4. Duplicate pair generation with confidence scores
5. Deduplication report

### Phase 5: Reporting & CLI
1. CLI interface using `argparse` or `click`
2. Formatted output (tables, JSON)
3. Report export functionality
4. Configuration file support

### Phase 6: Polish & Documentation
1. Error handling improvements
2. Unit tests
3. User documentation
4. Configuration examples

## Project Structure
```
knowledge-helper/
├── src/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── client.py          # YouTrack API client
│   │   └── endpoints.py       # API endpoint definitions
│   ├── models/
│   │   ├── __init__.py
│   │   └── article.py         # Article data models
│   ├── analyzers/
│   │   ├── __init__.py
│   │   ├── stale_content.py   # Stale article detection
│   │   ├── engagement.py      # Low views analysis
│   │   ├── duplicates.py      # Duplicate detection
│   │   └── statistics.py      # Statistics generation
│   ├── storage/
│   │   ├── __init__.py
│   │   └── cache.py           # Local data storage
│   ├── reports/
│   │   ├── __init__.py
│   │   └── generator.py       # Report generation
│   └── cli.py                 # CLI interface
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_analyzers.py
│   └── test_duplicates.py
├── config/
│   └── config.example.yaml
├── .env.example
├── .gitignore
├── requirements.txt
├── setup.py
├── README.md
└── plan.md                    # This file
```

## Configuration Requirements

### Environment Variables
- `YOUTRACK_BASE_URL`: YouTrack instance URL
- `YOUTRACK_TOKEN`: API authentication token
- `KB_PROJECT_ID`: Target KB project ID(s)

### Configuration File (config.yaml)
```yaml
youtrack:
  base_url: "${YOUTRACK_BASE_URL}"
  token: "${YOUTRACK_TOKEN}"

analysis:
  stale_threshold_days: 180
  low_views_threshold: 50
  low_views_age_days: 30
  duplicate_similarity_threshold: 0.85

storage:
  cache_enabled: true
  cache_path: "./data/cache.db"

reports:
  output_dir: "./reports"
  formats: ["json", "csv"]
```

## YouTrack API Endpoints (To Investigate)

### Documented
- GET `/api/articles` - List articles
- GET `/api/articles/{articleId}` - Get article details
- GET `/api/admin/projects` - List KB projects

### Undocumented (Need to Research)
- Article view statistics endpoint
- Analytics/metrics endpoints
- Bulk article metadata endpoints

## Success Criteria
1. Successfully authenticate and fetch articles from YouTrack
2. Accurately identify stale articles based on update dates
3. Report articles with low view counts
4. Detect duplicate articles with >85% accuracy
5. Generate sortable statistics reports
6. Complete CLI interface for all features
7. Proper error handling and logging

## Future Enhancements (Out of Scope)
- Web-based dashboard
- Automated notifications for stale content
- AI-powered content recommendations
- Integration with other KB platforms
- Article quality scoring
- Search effectiveness analysis

## Timeline Estimate
- Phase 1: 1-2 days
- Phase 2: 2-3 days
- Phase 3: 2-3 days
- Phase 4: 2-3 days
- Phase 5: 1-2 days
- Phase 6: 1-2 days

**Total**: ~2 weeks for full implementation

## Next Steps
1. Set up YouTrack API access and test credentials
2. Research undocumented API endpoints
3. Initialize project structure
4. Begin Phase 1 implementation
