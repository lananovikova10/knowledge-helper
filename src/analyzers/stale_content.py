"""Stale content analyzer for identifying outdated articles"""

from typing import List
from datetime import datetime

from ..api.client import YouTrackClient
from ..models.article import Article, StaleArticleReport


class StaleContentAnalyzer:
    """Analyzer for detecting stale (not recently updated) articles"""

    def __init__(self, client: YouTrackClient, threshold_days: int = 180):
        """
        Initialize stale content analyzer

        Args:
            client: YouTrack API client
            threshold_days: Number of days after which an article is considered stale
        """
        self.client = client
        self.threshold_days = threshold_days

    def analyze(self, project_id: str, batch_size: int = 100) -> StaleArticleReport:
        """
        Analyze articles in a project to find stale content

        Args:
            project_id: YouTrack project ID
            batch_size: Number of articles to fetch per API request

        Returns:
            StaleArticleReport containing analysis results
        """
        # Fetch all articles from the project
        print(f"Fetching articles from project '{project_id}'...")
        raw_articles = self.client.get_all_articles(project_id, batch_size=batch_size)

        # Convert to Article objects
        articles = [
            Article.from_api_response(data, project_id=project_id)
            for data in raw_articles
        ]

        print(f"Found {len(articles)} articles. Analyzing...")

        # Filter stale articles
        stale_articles = [
            article for article in articles
            if article.is_stale(self.threshold_days)
        ]

        # Create report
        report = StaleArticleReport(
            project_id=project_id,
            threshold_days=self.threshold_days,
            total_articles=len(articles),
            stale_articles=stale_articles,
            generated_at=datetime.now()
        )

        return report

    def find_oldest_articles(self, project_id: str, limit: int = 10) -> List[Article]:
        """
        Find the oldest (least recently updated) articles in a project

        Args:
            project_id: YouTrack project ID
            limit: Maximum number of articles to return

        Returns:
            List of oldest articles, sorted by update date
        """
        # Fetch all articles
        raw_articles = self.client.get_all_articles(project_id)

        # Convert to Article objects
        articles = [
            Article.from_api_response(data, project_id=project_id)
            for data in raw_articles
        ]

        # Sort by update date (oldest first)
        sorted_articles = sorted(
            articles,
            key=lambda a: a.updated if a.updated else a.created
        )

        return sorted_articles[:limit]

    def get_articles_by_age_range(
        self,
        project_id: str,
        min_days: int = 0,
        max_days: int = 365
    ) -> List[Article]:
        """
        Get articles within a specific age range (days since last update)

        Args:
            project_id: YouTrack project ID
            min_days: Minimum days since last update
            max_days: Maximum days since last update

        Returns:
            List of articles within the age range
        """
        # Fetch all articles
        raw_articles = self.client.get_all_articles(project_id)

        # Convert to Article objects
        articles = [
            Article.from_api_response(data, project_id=project_id)
            for data in raw_articles
        ]

        # Filter by age range
        filtered_articles = [
            article for article in articles
            if min_days <= article.days_since_update() <= max_days
        ]

        # Sort by update date (oldest first)
        return sorted(
            filtered_articles,
            key=lambda a: a.updated if a.updated else a.created
        )
