from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
import sys
import os

# Add parent directory to path to import our existing modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.client import YouTrackClient, YouTrackAPIError
from src.analyzers.stale_content import StaleContentAnalyzer


def index(request):
    """Home page - check if credentials are set"""
    has_credentials = (
        request.session.get('youtrack_url') and
        request.session.get('youtrack_token')
    )

    context = {
        'has_credentials': has_credentials,
        'youtrack_url': request.session.get('youtrack_url', ''),
    }
    return render(request, 'analyzer/index.html', context)


@require_http_methods(["GET", "POST"])
def credentials(request):
    """Manage YouTrack credentials"""
    if request.method == 'POST':
        youtrack_url = request.POST.get('youtrack_url', '').strip()
        youtrack_token = request.POST.get('youtrack_token', '').strip()

        if not youtrack_url or not youtrack_token:
            messages.error(request, 'Both URL and token are required')
            return render(request, 'analyzer/credentials.html')

        # Test the credentials
        try:
            client = YouTrackClient(youtrack_url, youtrack_token)
            if client.test_connection():
                # Store in session
                request.session['youtrack_url'] = youtrack_url
                request.session['youtrack_token'] = youtrack_token
                messages.success(request, 'Credentials validated successfully!')
                return redirect('index')
            else:
                messages.error(request, 'Failed to connect. Please check your credentials.')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    context = {
        'youtrack_url': request.session.get('youtrack_url', 'https://youtrack.jetbrains.com'),
    }
    return render(request, 'analyzer/credentials.html', context)


def clear_credentials(request):
    """Clear stored credentials"""
    request.session.flush()
    messages.success(request, 'Credentials cleared')
    return redirect('index')


def stale_content(request):
    """Analyze stale content"""
    # Check if credentials are set
    youtrack_url = request.session.get('youtrack_url')
    youtrack_token = request.session.get('youtrack_token')

    if not youtrack_url or not youtrack_token:
        messages.error(request, 'Please configure your YouTrack credentials first')
        return redirect('credentials')

    context = {
        'youtrack_url': youtrack_url,
    }
    return render(request, 'analyzer/stale_content.html', context)


def analyze_stale_content(request):
    """API endpoint to perform analysis"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    # Check credentials
    youtrack_url = request.session.get('youtrack_url')
    youtrack_token = request.session.get('youtrack_token')

    if not youtrack_url or not youtrack_token:
        return JsonResponse({'error': 'Credentials not configured'}, status=401)

    # Get parameters
    project_id = request.POST.get('project_id', '').strip()
    threshold_days = int(request.POST.get('threshold_days', 180))

    if not project_id:
        return JsonResponse({'error': 'Project ID is required'}, status=400)

    try:
        # Create client and analyzer
        client = YouTrackClient(youtrack_url, youtrack_token)
        analyzer = StaleContentAnalyzer(client, threshold_days=threshold_days)

        # Run analysis
        report = analyzer.analyze(project_id)

        # Convert to JSON-serializable format
        articles_data = []
        for article in report.get_sorted_articles():
            last_update = article.updated if article.updated else article.created
            articles_data.append({
                'id': article.id,
                'summary': article.summary,
                'created': article.created.isoformat(),
                'updated': article.updated.isoformat() if article.updated else None,
                'last_update': last_update.isoformat(),
                'days_since_update': article.days_since_update(),
                'view_count': article.view_count,
            })

        response_data = {
            'project_id': report.project_id,
            'threshold_days': report.threshold_days,
            'total_articles': report.total_articles,
            'stale_count': report.stale_count,
            'stale_percentage': round(report.stale_percentage, 2),
            'generated_at': report.generated_at.isoformat(),
            'articles': articles_data,
        }

        return JsonResponse(response_data)

    except YouTrackAPIError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)
