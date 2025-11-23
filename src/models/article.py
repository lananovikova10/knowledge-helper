"""Article data models"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class Article:
    """Represents a YouTrack KB article"""

    id: str
    summary: str
    created: datetime
    updated: Optional[datetime] = None
    view_count: int = 0
    project_id: Optional[str] = None

    @classmethod
    def from_api_response(cls, data: dict, project_id: Optional[str] = None) -> 'Article':
        """
        Create Article instance from YouTrack API response

        Args:
            data: API response dictionary
            project_id: Project ID to associate with article

        Returns:
            Article instance
        """
        # Parse created timestamp
        created = cls._parse_timestamp(data.get('created', 0))

        # Parse updated timestamp (may be None)
        updated_ts = data.get('updated')
        updated = cls._parse_timestamp(updated_ts) if updated_ts else None

        # Extract view count from viewCounters structure
        view_count = cls._extract_view_count(data.get('viewCounters', {}))

        return cls(
            id=data.get('id', ''),
            summary=data.get('summary', 'Untitled'),
            created=created,
            updated=updated,
            view_count=view_count,
            project_id=project_id
        )

    @staticmethod
    def _parse_timestamp(timestamp: int) -> datetime:
        """
        Parse YouTrack timestamp (milliseconds since epoch) to datetime

        Args:
            timestamp: Milliseconds since epoch

        Returns:
            datetime object
        """
        return datetime.fromtimestamp(timestamp / 1000)

    @staticmethod
    def _extract_view_count(view_counters: dict) -> int:
        """
        Extract total view count from viewCounters structure

        ViewCounters structure example:
        {
            "views": [
                {"created": timestamp1},
                {"created": timestamp2},
                ...
            ]
        }

        Args:
            view_counters: ViewCounters dictionary from API

        Returns:
            Total number of views
        """
        if not view_counters or 'views' not in view_counters:
            return 0

        views = view_counters.get('views', [])
        return len(views) if isinstance(views, list) else 0

    def days_since_update(self) -> int:
        """
        Calculate number of days since last update

        Returns:
            Days since last update (or creation if never updated)
        """
        reference_date = self.updated if self.updated else self.created
        delta = datetime.now() - reference_date
        return delta.days

    def is_stale(self, threshold_days: int) -> bool:
        """
        Check if article is considered stale

        Args:
            threshold_days: Number of days after which an article is stale

        Returns:
            True if article hasn't been updated for threshold_days
        """
        return self.days_since_update() >= threshold_days

    def __str__(self):
        """Human-readable string representation"""
        last_update = self.updated if self.updated else self.created
        return f"Article({self.id}): {self.summary} (updated: {last_update.strftime('%Y-%m-%d')})"


@dataclass
class StaleArticleReport:
    """Report of stale articles analysis"""

    project_id: str
    threshold_days: int
    total_articles: int
    stale_articles: List[Article]
    generated_at: datetime

    @property
    def stale_count(self) -> int:
        """Number of stale articles"""
        return len(self.stale_articles)

    @property
    def stale_percentage(self) -> float:
        """Percentage of articles that are stale"""
        if self.total_articles == 0:
            return 0.0
        return (self.stale_count / self.total_articles) * 100

    def get_sorted_articles(self) -> List[Article]:
        """
        Get stale articles sorted by update date (oldest first)

        Returns:
            List of articles sorted by last update date
        """
        return sorted(
            self.stale_articles,
            key=lambda a: a.updated if a.updated else a.created
        )

    def __str__(self):
        """Human-readable string representation"""
        return (f"Stale Article Report for {self.project_id}\n"
                f"Threshold: {self.threshold_days} days\n"
                f"Stale articles: {self.stale_count}/{self.total_articles} "
                f"({self.stale_percentage:.1f}%)")
