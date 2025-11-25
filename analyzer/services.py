"""Services for managing article and view history data"""

from typing import List
from datetime import datetime
from django.db import transaction
from django.utils import timezone

from analyzer.models import Article as DBArticle, ViewHistory
from src.models.article import Article


def sync_articles_to_database(articles: List[Article]) -> None:
    """
    Sync articles and their view histories to the database

    Args:
        articles: List of Article objects from API
    """
    for article in articles:
        sync_article_to_database(article)


def sync_article_to_database(article: Article) -> DBArticle:
    """
    Sync a single article and its view history to the database

    Args:
        article: Article object from API

    Returns:
        Database Article instance
    """
    with transaction.atomic():
        # Get or create article record
        db_article, created = DBArticle.objects.get_or_create(
            article_id=article.id,
            defaults={
                'project_id': article.project_id or '',
                'summary': article.summary,
                'created': article.created,
                'updated': article.updated,
            }
        )

        # Update article metadata if it changed
        if not created:
            db_article.project_id = article.project_id or ''
            db_article.summary = article.summary
            db_article.updated = article.updated
            db_article.save()

        # Sync view timestamps if available
        if article.view_timestamps:
            sync_view_timestamps(db_article, article.view_timestamps)

        return db_article


def sync_view_timestamps(db_article: DBArticle, timestamps: List[datetime]) -> int:
    """
    Sync view timestamps to the database

    Args:
        db_article: Database Article instance
        timestamps: List of view timestamps

    Returns:
        Number of new views added
    """
    new_views_count = 0

    for timestamp in timestamps:
        # Make timezone aware if needed
        if timezone.is_naive(timestamp):
            timestamp = timezone.make_aware(timestamp)

        # Create view record (unique constraint prevents duplicates)
        _, created = ViewHistory.objects.get_or_create(
            article=db_article,
            viewed_at=timestamp
        )

        if created:
            new_views_count += 1

    return new_views_count


def get_views_in_date_range(article_id: str, start_date: datetime, end_date: datetime) -> int:
    """
    Get view count for an article within a date range

    Args:
        article_id: Article ID
        start_date: Start of date range
        end_date: End of date range

    Returns:
        Number of views in date range
    """
    try:
        db_article = DBArticle.objects.get(article_id=article_id)

        # Make timezone aware if needed
        if timezone.is_naive(start_date):
            start_date = timezone.make_aware(start_date)
        if timezone.is_naive(end_date):
            end_date = timezone.make_aware(end_date)

        return ViewHistory.objects.filter(
            article=db_article,
            viewed_at__gte=start_date,
            viewed_at__lte=end_date
        ).count()
    except DBArticle.DoesNotExist:
        return 0


def get_article_view_history(article_id: str) -> List[datetime]:
    """
    Get all view timestamps for an article

    Args:
        article_id: Article ID

    Returns:
        List of view timestamps
    """
    try:
        db_article = DBArticle.objects.get(article_id=article_id)
        return list(
            ViewHistory.objects.filter(article=db_article)
            .values_list('viewed_at', flat=True)
            .order_by('viewed_at')
        )
    except DBArticle.DoesNotExist:
        return []
