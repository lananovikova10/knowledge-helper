# Rate Limiting Documentation

This document explains the rate limiting implementation in the Knowledge Base Portal.

## Overview

Rate limiting has been implemented to protect the API endpoints from abuse and ensure fair resource usage. The implementation uses `django-ratelimit` to restrict the number of requests users can make to computationally expensive analysis endpoints.

## Configuration

### Settings

Rate limiting is configured in `kb_portal/settings.py`:

```python
# Rate limiting settings
RATELIMIT_ENABLE = True  # Set to False to disable rate limiting
RATELIMIT_USE_CACHE = 'default'  # Use Django cache framework

# Cache configuration (required for rate limiting)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
```

### Protected Endpoints

The following API endpoints are protected with rate limiting:

1. **`/api/analyze-stale/`** - Stale content analysis
2. **`/api/analyze-low-engagement/`** - Low engagement analysis
3. **`/api/analyze-duplicates/`** - Duplicate detection

Each endpoint is limited to **10 requests per minute per session**.

## Implementation Details

### Decorator Usage

Rate limiting is applied using the `@ratelimit` decorator:

```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='session', rate='10/m', method='POST')
def analyze_stale_content(request):
    """API endpoint with rate limiting"""
    # ... endpoint logic
```

### Parameters Explained

- **`key='session'`**: Rate limiting is tracked per user session
  - Each user session gets its own rate limit counter
  - Different users don't affect each other's limits
  - Anonymous sessions are tracked separately

- **`rate='10/m'`**: 10 requests per minute
  - Users can make up to 10 requests per minute
  - After 10 requests, additional requests return HTTP 429
  - Counter resets after one minute

- **`method='POST'`**: Only POST requests are rate limited
  - GET requests (page loads) are not affected
  - Only API calls trigger rate limiting

## Rate Limit Response

When a user exceeds the rate limit, they receive:

**HTTP Status Code:** `429 Too Many Requests`

**Response Headers:**
- `Retry-After`: Number of seconds until the rate limit resets
- `X-RateLimit-Limit`: Maximum requests allowed (10)
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Unix timestamp when the limit resets

## Testing Rate Limiting

### Automated Testing

Use the provided test script to verify rate limiting:

```bash
# Start the Django development server
python manage.py runserver

# In another terminal, run the test script
python test_rate_limiting.py
```

The test script will:
1. Send 15 requests rapidly (more than the 10/minute limit)
2. Track successful and rate-limited responses
3. Report whether rate limiting is working correctly

Expected output:
```
Total requests sent:       15
Successful (allowed):      10
Rate limited (blocked):    5
✅ Rate limiting is WORKING correctly!
```

### Manual Testing

You can also test manually using curl:

```bash
# Send multiple requests quickly
for i in {1..15}; do
  echo "Request $i:"
  curl -X POST http://localhost:8000/api/analyze-stale/ \
    -d "project_id=TEST&threshold_days=180" \
    -c cookies.txt -b cookies.txt \
    -w "\nStatus: %{http_code}\n" \
    -s -o /dev/null
  sleep 0.5
done
```

You should see status code `200` (or `400`/`401`) for the first 10 requests, then `429` for requests 11-15.

## Disabling Rate Limiting

### For Development

To disable rate limiting temporarily (e.g., during development or testing):

```python
# In kb_portal/settings.py
RATELIMIT_ENABLE = False
```

### For Specific Tests

You can override rate limiting in Django tests:

```python
from django.test import override_settings

@override_settings(RATELIMIT_ENABLE=False)
def test_my_view():
    # Rate limiting disabled for this test
    pass
```

## Customizing Rate Limits

### Changing the Rate

To adjust the rate limit, modify the decorator in `analyzer/views.py`:

```python
# Increase to 20 requests per minute
@ratelimit(key='session', rate='20/m', method='POST')

# Decrease to 5 requests per minute
@ratelimit(key='session', rate='5/m', method='POST')

# Different time periods
@ratelimit(key='session', rate='100/h', method='POST')  # Per hour
@ratelimit(key='session', rate='1000/d', method='POST') # Per day
```

### Different Rate Limit Keys

You can change how rate limits are tracked:

```python
# Per IP address (stricter - shared across all users from same IP)
@ratelimit(key='ip', rate='10/m', method='POST')

# Per authenticated user (requires Django authentication)
@ratelimit(key='user', rate='10/m', method='POST')

# Custom key function
def get_rate_limit_key(request):
    return request.META.get('HTTP_X_API_KEY')

@ratelimit(key=get_rate_limit_key, rate='10/m', method='POST')
```

### Per-Endpoint Rates

Different endpoints can have different limits:

```python
# Expensive operation - stricter limit
@ratelimit(key='session', rate='5/m', method='POST')
def analyze_duplicates(request):
    pass

# Lighter operation - more lenient limit
@ratelimit(key='session', rate='20/m', method='POST')
def analyze_stale_content(request):
    pass
```

## Production Recommendations

### Use Redis for Distributed Rate Limiting

For production environments with multiple servers, use Redis:

1. **Install Redis and django-redis:**
   ```bash
   pip install redis django-redis
   ```

2. **Update settings.py:**
   ```python
   CACHES = {
       'default': {
           'BACKEND': 'django_redis.cache.RedisCache',
           'LOCATION': 'redis://127.0.0.1:6379/1',
           'OPTIONS': {
               'CLIENT_CLASS': 'django_redis.client.DefaultClient',
           }
       }
   }
   ```

### Monitoring

Consider adding monitoring for rate limit events:

```python
from django_ratelimit.decorators import ratelimit
import logging

logger = logging.getLogger(__name__)

@ratelimit(key='session', rate='10/m', method='POST')
def analyze_stale_content(request):
    if getattr(request, 'limited', False):
        logger.warning(f"Rate limit exceeded for session {request.session.session_key}")
    # ... rest of endpoint
```

### API Documentation

Update your API documentation to inform users about rate limits:

- Document the rate limits for each endpoint
- Explain the HTTP 429 response
- Show the `Retry-After` header usage
- Provide guidance on handling rate limit errors

## Troubleshooting

### Rate Limiting Not Working

1. **Check django-ratelimit is installed:**
   ```bash
   pip list | grep django-ratelimit
   ```

2. **Verify RATELIMIT_ENABLE setting:**
   ```python
   # In settings.py
   RATELIMIT_ENABLE = True
   ```

3. **Ensure cache is configured:**
   ```python
   # CACHES setting must exist in settings.py
   CACHES = { 'default': { ... } }
   ```

4. **Check decorator is applied:**
   ```python
   # Each view should have the decorator
   @ratelimit(key='session', rate='10/m', method='POST')
   def my_view(request):
       pass
   ```

### Rate Limits Too Strict

If legitimate users are being rate limited:

1. Increase the rate limit: `rate='20/m'` → `rate='50/m'`
2. Use a longer time window: `rate='10/m'` → `rate='100/h'`
3. Switch to per-user limits if using shared IPs: `key='user'` instead of `key='ip'`

### Session Issues

If rate limiting isn't working with session keys:

1. Check session middleware is enabled in `MIDDLEWARE`
2. Verify session backend is configured: `SESSION_ENGINE`
3. Ensure cookies are being sent and received properly

## Additional Resources

- [django-ratelimit Documentation](https://django-ratelimit.readthedocs.io/)
- [Django Caching Framework](https://docs.djangoproject.com/en/stable/topics/cache/)
- [HTTP 429 Too Many Requests](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429)
