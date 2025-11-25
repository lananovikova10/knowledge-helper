"""Article data models"""

from dataclasses import dataclass
from datetime import datetime, timedelta
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
    view_timestamps: Optional[List[datetime]] = None

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

        # Extract view count and timestamps from viewCounters structure
        view_counters = data.get('viewCounters', {})
        view_count = cls._extract_view_count(view_counters)
        view_timestamps = cls._extract_view_timestamps(view_counters)

        return cls(
            id=data.get('id', ''),
            summary=data.get('summary', 'Untitled'),
            created=created,
            updated=updated,
            view_count=view_count,
            project_id=project_id,
            view_timestamps=view_timestamps
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

    @staticmethod
    def _extract_view_timestamps(view_counters: dict) -> Optional[List[datetime]]:
        """
        Extract individual view timestamps from viewCounters structure

        Args:
            view_counters: ViewCounters dictionary from API

        Returns:
            List of datetime objects representing individual view timestamps, or None if no views
        """
        if not view_counters or 'views' not in view_counters:
            return None

        views = view_counters.get('views', [])
        if not isinstance(views, list) or len(views) == 0:
            return None

        timestamps = []
        for view in views:
            if isinstance(view, dict) and 'created' in view:
                timestamp = view.get('created')
                if timestamp:
                    timestamps.append(datetime.fromtimestamp(timestamp / 1000))

        return timestamps if timestamps else None

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

    def get_views_in_date_range(self, start_date: datetime, end_date: datetime) -> int:
        """
        Count views within a specific date range

        Args:
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)

        Returns:
            Number of views within the date range
        """
        if not self.view_timestamps:
            return 0

        # Normalize dates to start/end of day
        start = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        count = 0
        for timestamp in self.view_timestamps:
            if start <= timestamp <= end:
                count += 1

        return count

    def get_recent_views(self, days: int) -> int:
        """
        Count views in the last N days

        Args:
            days: Number of days to look back

        Returns:
            Number of views in the last N days
        """
        if not self.view_timestamps:
            return 0

        cutoff_date = datetime.now() - timedelta(days=days)

        count = 0
        for timestamp in self.view_timestamps:
            if timestamp >= cutoff_date:
                count += 1

        return count

    def calculate_view_velocity(self, recent_days: int = 30, historical_days: int = 90) -> float:
        """
        Calculate view velocity (change in view rate)

        Args:
            recent_days: Number of recent days to compare (default: 30)
            historical_days: Number of historical days to compare against (default: 90)

        Returns:
            View velocity ratio (recent_rate / historical_rate)
            > 1.0 = increasing views (trending up)
            < 1.0 = decreasing views (trending down)
            = 1.0 = stable
        """
        if not self.view_timestamps:
            return 0.0

        recent_views = self.get_recent_views(recent_days)
        historical_views = self.get_recent_views(historical_days)

        # Calculate views per day
        recent_rate = recent_views / recent_days
        historical_rate = historical_views / historical_days

        # Avoid division by zero
        if historical_rate == 0:
            return 1.0 if recent_rate == 0 else float('inf')

        return recent_rate / historical_rate

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
