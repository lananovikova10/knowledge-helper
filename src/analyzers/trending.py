"""Trending Analysis Analyzer

This analyzer identifies articles that are gaining or losing popularity over time
by comparing recent view rates with historical view rates.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional

from src.models.article import Article


@dataclass
class TrendingArticle:
    """Represents an article with trending metrics"""
    article: Article
    recent_views: int  # Views in recent period
    historical_views: int  # Views in historical period
    recent_rate: float  # Views per day (recent)
    historical_rate: float  # Views per day (historical)
    velocity: float  # Rate of change (recent_rate / historical_rate)
    trend_direction: str  # 'increasing', 'decreasing', 'stable'
    trend_strength: str  # 'strong', 'moderate', 'weak'
    percentage_change: float  # Percentage change in view rate


@dataclass
class TrendingAnalysisReport:
    """Report containing trending analysis results"""
    project_id: str
    recent_days: int
    historical_days: int
    total_articles: int
    trending_up: List[TrendingArticle]
    trending_down: List[TrendingArticle]
    stable: List[TrendingArticle]
    generated_at: datetime

    @property
    def trending_up_count(self) -> int:
        """Number of articles trending up"""
        return len(self.trending_up)

    @property
    def trending_down_count(self) -> int:
        """Number of articles trending down"""
        return len(self.trending_down)

    @property
    def stable_count(self) -> int:
        """Number of stable articles"""
        return len(self.stable)


class TrendingAnalyzer:
    """Analyzer for identifying trending articles"""

    def __init__(
        self,
        recent_days: int = 30,
        historical_days: int = 90,
        min_views_threshold: int = 10,
        stability_threshold: float = 0.15  # 15% change considered stable
    ):
        """
        Initialize trending analyzer

        Args:
            recent_days: Number of recent days to analyze (default: 30)
            historical_days: Number of historical days to compare (default: 90)
            min_views_threshold: Minimum total views to consider (default: 10)
            stability_threshold: Threshold for considering trend stable (default: 0.15 = 15%)
        """
        self.recent_days = recent_days
        self.historical_days = historical_days
        self.min_views_threshold = min_views_threshold
        self.stability_threshold = stability_threshold

    def analyze(self, articles: List[Article], project_id: str) -> TrendingAnalysisReport:
        """
        Perform trending analysis on articles

        Args:
            articles: List of articles to analyze
            project_id: Project ID

        Returns:
            TrendingAnalysisReport with results
        """
        trending_up = []
        trending_down = []
        stable = []

        for article in articles:
            # Skip articles without view data
            if not article.view_timestamps or article.view_count < self.min_views_threshold:
                continue

            trending_article = self._analyze_article(article)

            if trending_article.trend_direction == 'increasing':
                trending_up.append(trending_article)
            elif trending_article.trend_direction == 'decreasing':
                trending_down.append(trending_article)
            else:
                stable.append(trending_article)

        # Sort by velocity (most significant trends first)
        trending_up.sort(key=lambda x: x.velocity, reverse=True)
        trending_down.sort(key=lambda x: x.velocity)

        return TrendingAnalysisReport(
            project_id=project_id,
            recent_days=self.recent_days,
            historical_days=self.historical_days,
            total_articles=len(articles),
            trending_up=trending_up,
            trending_down=trending_down,
            stable=stable,
            generated_at=datetime.now()
        )

    def _analyze_article(self, article: Article) -> TrendingArticle:
        """
        Analyze a single article for trending metrics

        Args:
            article: Article to analyze

        Returns:
            TrendingArticle with metrics
        """
        # Get views for different periods
        recent_views = article.get_recent_views(self.recent_days)
        historical_views = article.get_recent_views(self.historical_days)

        # Calculate daily rates
        recent_rate = recent_views / self.recent_days
        historical_rate = historical_views / self.historical_days

        # Calculate velocity
        if historical_rate == 0:
            velocity = float('inf') if recent_rate > 0 else 1.0
        else:
            velocity = recent_rate / historical_rate

        # Calculate percentage change
        if historical_rate == 0:
            percentage_change = 100.0 if recent_rate > 0 else 0.0
        else:
            percentage_change = ((recent_rate - historical_rate) / historical_rate) * 100

        # Determine trend direction and strength
        trend_direction, trend_strength = self._classify_trend(velocity, percentage_change)

        return TrendingArticle(
            article=article,
            recent_views=recent_views,
            historical_views=historical_views,
            recent_rate=recent_rate,
            historical_rate=historical_rate,
            velocity=velocity,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            percentage_change=percentage_change
        )

    def _classify_trend(self, velocity: float, percentage_change: float) -> tuple[str, str]:
        """
        Classify trend direction and strength

        Args:
            velocity: View velocity ratio
            percentage_change: Percentage change in view rate

        Returns:
            Tuple of (direction, strength)
        """
        # Determine direction
        abs_change = abs(percentage_change)

        if abs_change <= self.stability_threshold * 100:
            direction = 'stable'
            strength = 'weak'
        elif velocity > 1.0:
            direction = 'increasing'
            # Classify strength based on percentage change
            if abs_change >= 100:  # 100%+ increase
                strength = 'strong'
            elif abs_change >= 50:  # 50-100% increase
                strength = 'moderate'
            else:
                strength = 'weak'
        else:
            direction = 'decreasing'
            # Classify strength based on percentage change
            if abs_change >= 50:  # 50%+ decrease
                strength = 'strong'
            elif abs_change >= 25:  # 25-50% decrease
                strength = 'moderate'
            else:
                strength = 'weak'

        return direction, strength


def format_trending_report(report: TrendingAnalysisReport) -> str:
    """
    Format trending analysis report as human-readable text

    Args:
        report: TrendingAnalysisReport to format

    Returns:
        Formatted report string
    """
    lines = [
        f"Trending Analysis Report for {report.project_id}",
        f"=" * 60,
        f"Analysis Period:",
        f"  Recent: Last {report.recent_days} days",
        f"  Historical: Last {report.historical_days} days",
        f"",
        f"Summary:",
        f"  Total articles analyzed: {report.total_articles}",
        f"  Trending up: {report.trending_up_count}",
        f"  Trending down: {report.trending_down_count}",
        f"  Stable: {report.stable_count}",
        f"",
    ]

    # Trending up articles
    if report.trending_up:
        lines.extend([
            f"Articles Trending Up ({report.trending_up_count}):",
            f"-" * 60,
        ])

        for ta in report.trending_up[:20]:  # Show top 20
            lines.append(
                f"  [{ta.article.id}] {ta.article.summary[:50]}"
            )
            lines.append(
                f"    Recent: {ta.recent_views} views ({ta.recent_rate:.2f}/day) | "
                f"Historical: {ta.historical_views} views ({ta.historical_rate:.2f}/day)"
            )
            lines.append(
                f"    Velocity: {ta.velocity:.2f}x | "
                f"Change: +{ta.percentage_change:.1f}% | "
                f"Strength: {ta.trend_strength}"
            )
            lines.append("")

    # Trending down articles
    if report.trending_down:
        lines.extend([
            f"",
            f"Articles Trending Down ({report.trending_down_count}):",
            f"-" * 60,
        ])

        for ta in report.trending_down[:20]:  # Show top 20
            lines.append(
                f"  [{ta.article.id}] {ta.article.summary[:50]}"
            )
            lines.append(
                f"    Recent: {ta.recent_views} views ({ta.recent_rate:.2f}/day) | "
                f"Historical: {ta.historical_views} views ({ta.historical_rate:.2f}/day)"
            )
            lines.append(
                f"    Velocity: {ta.velocity:.2f}x | "
                f"Change: {ta.percentage_change:.1f}% | "
                f"Strength: {ta.trend_strength}"
            )
            lines.append("")

    lines.append(f"Generated at: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")

    return "\n".join(lines)
