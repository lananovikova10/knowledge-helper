#!/usr/bin/env python
"""
Test script to verify rate limiting is working correctly.
This script simulates multiple requests to test the rate limiting decorator.

Usage:
    python test_rate_limiting.py

Note: This requires the Django development server to be running.
"""

import requests
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_ENDPOINT = "/api/analyze-stale/"
NUM_REQUESTS = 15  # More than the 10/minute limit
RATE_LIMIT = 10  # Expected rate limit per minute

def test_rate_limiting():
    """Test rate limiting by sending multiple requests"""
    print(f"Testing rate limiting on {API_ENDPOINT}")
    print(f"Rate limit: {RATE_LIMIT} requests per minute")
    print(f"Sending {NUM_REQUESTS} requests...\n")

    # Create a session to maintain cookies
    session = requests.Session()

    # Results tracking
    successful_requests = 0
    rate_limited_requests = 0

    for i in range(1, NUM_REQUESTS + 1):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        try:
            # Send POST request (rate limit applies to POST only)
            response = session.post(
                f"{BASE_URL}{API_ENDPOINT}",
                data={
                    'project_id': 'TEST',
                    'threshold_days': 180
                },
                timeout=5
            )

            if response.status_code == 429:
                rate_limited_requests += 1
                print(f"[{timestamp}] Request {i:2d}: ❌ RATE LIMITED (429)")
            elif response.status_code in [200, 400, 401]:
                # 400/401 means the request went through but failed validation
                # This is fine for our rate limiting test
                successful_requests += 1
                print(f"[{timestamp}] Request {i:2d}: ✓ Allowed (status {response.status_code})")
            else:
                print(f"[{timestamp}] Request {i:2d}: ? Unexpected status {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"[{timestamp}] Request {i:2d}: ⚠ Error: {e}")

        # Small delay between requests
        time.sleep(0.1)

    print("\n" + "="*60)
    print("RESULTS:")
    print("="*60)
    print(f"Total requests sent:       {NUM_REQUESTS}")
    print(f"Successful (allowed):      {successful_requests}")
    print(f"Rate limited (blocked):    {rate_limited_requests}")
    print(f"Expected rate limit:       {RATE_LIMIT} requests/minute")
    print()

    if rate_limited_requests > 0 and successful_requests <= RATE_LIMIT:
        print("✅ Rate limiting is WORKING correctly!")
    elif rate_limited_requests == 0 and successful_requests > RATE_LIMIT:
        print("⚠️  Rate limiting may NOT be working - all requests succeeded")
        print("   Check that:")
        print("   1. django-ratelimit is installed: pip install django-ratelimit")
        print("   2. RATELIMIT_ENABLE = True in settings.py")
        print("   3. CACHES is configured in settings.py")
    else:
        print("ℹ️  Results inconclusive - check the output above")

def check_server():
    """Check if the Django server is running"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=2)
        return True
    except requests.exceptions.RequestException:
        return False

if __name__ == "__main__":
    print("Django Rate Limiting Test")
    print("="*60)

    if not check_server():
        print(f"❌ Cannot connect to Django server at {BASE_URL}")
        print("\nPlease start the Django development server first:")
        print("    python manage.py runserver")
        exit(1)

    print(f"✓ Django server is running at {BASE_URL}\n")

    try:
        test_rate_limiting()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
