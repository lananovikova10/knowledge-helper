"""Low engagement analyzer for identifying articles with low view counts"""

from typing import List
from datetime import datetime
from dataclasses import dataclass

from ..api.client import YouTrackClient
from ..models.article import Article


@dataclass
class LowEngagementReport:
    """Report of low engagement analysis"""

    project_id: str
    score_threshold: float  # Changed from view_threshold
    min_age_days: int
    total_articles: int
    low_engagement_articles: List[Article]
    generated_at: datetime

    @property
    def low_engagement_count(self) -> int:
        """Number of low engagement articles"""
        return len(self.low_engagement_articles)

    @property
    def low_engagement_percentage(self) -> float:
        """Percentage of articles with low engagement"""
        if self.total_articles == 0:
            return 0.0
        return (self.low_engagement_count / self.total_articles) * 100

    def get_sorted_articles(self, sort_by: str = 'score') -> List[Article]:
        """
        Get low engagement articles sorted by specified field

        Args:
            sort_by: Field to sort by ('views', 'age', 'score')

        Returns:
            Sorted list of articles
        """
        if sort_by == 'views':
            return sorted(self.low_engagement_articles, key=lambda a: a.view_count)
        elif sort_by == 'age':
            return sorted(self.low_engagement_articles, key=lambda a: a.days_since_update(), reverse=True)
        else:  # score or default
            return sorted(self.low_engagement_articles, key=lambda a: a.view_count)

    def __str__(self):
        """Human-readable string representation"""
        return (f"Low Engagement Report for {self.project_id}\n"
                f"Score threshold: {self.score_threshold} (views/day)\n"
                f"Min age: {self.min_age_days} days\n"
                f"Low engagement articles: {self.low_engagement_count}/{self.total_articles} "
                f"({self.low_engagement_percentage:.1f}%)")


class LowEngagementAnalyzer:
    """Analyzer for detecting articles with low engagement based on views per day"""

    def __init__(self, client: YouTrackClient, score_threshold: float = 1.0, min_age_days: int = 7):
        """
        Initialize low engagement analyzer

        Args:
            client: YouTrack API client
            score_threshold: Maximum engagement score (views/day) to consider low engagement
            min_age_days: Minimum age in days for articles to be considered (filters out very new articles)
        """
        self.client = client
        self.score_threshold = score_threshold
        self.min_age_days = min_age_days

    def analyze(self, project_id: str, batch_size: int = 100) -> LowEngagementReport:
        """
        Analyze articles in a project to find low engagement content based on views per day

        Args:
            project_id: YouTrack project ID
            batch_size: Number of articles to fetch per API request

        Returns:
            LowEngagementReport containing analysis results
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

        # Filter articles: old enough AND low engagement score (views/day)
        low_engagement_articles = [
            article for article in articles
            if article.days_since_update() >= self.min_age_days
            and self.get_engagement_score(article) <= self.score_threshold
        ]

        # Create report
        report = LowEngagementReport(
            project_id=project_id,
            score_threshold=self.score_threshold,
            min_age_days=self.min_age_days,
            total_articles=len(articles),
            low_engagement_articles=low_engagement_articles,
            generated_at=datetime.now()
        )

        return report

    def get_engagement_score(self, article: Article) -> float:
        """
        Calculate an engagement score for an article (views per day)

        Score is simply the cumulative views divided by days since creation.
        This normalizes engagement by article age.

        Args:
            article: Article to score

        Returns:
            Engagement score (views per day)
        """
        days_old = max(article.days_since_update(), 1)  # Avoid division by zero
        views_per_day = article.view_count / days_old
        return round(views_per_day, 2)

    def get_articles_by_engagement_score(
        self,
        project_id: str,
        min_score: float = 0,
        max_score: float = 25
    ) -> List[tuple[Article, float]]:
        """
        Get articles within a specific engagement score range

        Args:
            project_id: YouTrack project ID
            min_score: Minimum engagement score
            max_score: Maximum engagement score

        Returns:
            List of (article, score) tuples sorted by score
        """
        # Fetch all articles
        raw_articles = self.client.get_all_articles(project_id)

        # Convert to Article objects
        articles = [
            Article.from_api_response(data, project_id=project_id)
            for data in raw_articles
        ]

        # Calculate scores and filter
        articles_with_scores = [
            (article, self.get_engagement_score(article))
            for article in articles
        ]

        filtered = [
            (article, score) for article, score in articles_with_scores
            if min_score <= score <= max_score
        ]

        # Sort by score (lowest first)
        return sorted(filtered, key=lambda x: x[1])

    def find_lowest_engagement(self, project_id: str, limit: int = 10) -> List[tuple[Article, float]]:
        """
        Find articles with the lowest engagement scores

        Args:
            project_id: YouTrack project ID
            limit: Maximum number of articles to return

        Returns:
            List of (article, score) tuples with lowest engagement
        """
        # Fetch all articles
        raw_articles = self.client.get_all_articles(project_id)

        # Convert to Article objects and calculate scores
        articles = [
            Article.from_api_response(data, project_id=project_id)
            for data in raw_articles
        ]

        articles_with_scores = [
            (article, self.get_engagement_score(article))
            for article in articles
        ]

        # Sort by score (lowest first) and return top N
        sorted_articles = sorted(articles_with_scores, key=lambda x: x[1])
        return sorted_articles[:limit]
