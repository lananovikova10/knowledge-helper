"""
Priority Queue Analyzer for Knowledge Base Articles

Combines multiple risk factors to create actionable priorities:
- Stale content with high traffic
- Trending articles that need updating
- Engagement patterns
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional
from ..models.article import Article


@dataclass
class ArticleRiskScore:
    """Risk assessment for a single article"""
    article: Article
    score: int
    priority: str  # CRITICAL, HIGH, MEDIUM, LOW
    factors: List[str]  # List of contributing risk factors
    recommended_action: str
    urgency_reasons: List[str]  # Detailed reasons for the urgency

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'article': {
                'id': self.article.id,
                'summary': self.article.summary,
                'created': self.article.created.isoformat() if self.article.created else None,
                'updated': self.article.updated.isoformat() if self.article.updated else None,
                'view_count': self.article.view_count,
                'days_since_update': self.article.days_since_update(),
                'project_id': self.article.project_id
            },
            'score': self.score,
            'priority': self.priority,
            'factors': self.factors,
            'recommended_action': self.recommended_action,
            'urgency_reasons': self.urgency_reasons
        }


@dataclass
class PriorityQueueReport:
    """Report containing prioritized articles by risk level"""
    project_id: str
    total_articles: int
    critical_articles: List[ArticleRiskScore]
    high_articles: List[ArticleRiskScore]
    medium_articles: List[ArticleRiskScore]
    low_articles: List[ArticleRiskScore]
    generated_at: datetime

    @property
    def critical_count(self) -> int:
        return len(self.critical_articles)

    @property
    def high_count(self) -> int:
        return len(self.high_articles)

    @property
    def medium_count(self) -> int:
        return len(self.medium_articles)

    @property
    def low_count(self) -> int:
        return len(self.low_articles)

    @property
    def action_required_count(self) -> int:
        """Count of articles requiring immediate action (CRITICAL + HIGH)"""
        return self.critical_count + self.high_count

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'project_id': self.project_id,
            'total_articles': self.total_articles,
            'summary': {
                'critical_count': self.critical_count,
                'high_count': self.high_count,
                'medium_count': self.medium_count,
                'low_count': self.low_count,
                'action_required_count': self.action_required_count
            },
            'critical_articles': [a.to_dict() for a in self.critical_articles],
            'high_articles': [a.to_dict() for a in self.high_articles],
            'medium_articles': [a.to_dict() for a in self.medium_articles],
            'low_articles': [a.to_dict() for a in self.low_articles],
            'generated_at': self.generated_at.isoformat()
        }


class ArticleRiskAnalyzer:
    """
    Analyzes articles to identify high-priority items needing attention.

    Combines multiple risk factors:
    1. Staleness + Traffic (high views on old content = critical)
    2. Trending patterns (sudden view increase on stale content)
    3. Low engagement (potential for archiving/consolidation)
    4. Content age vs. update frequency
    """

    # Configuration constants
    STALE_THRESHOLD_DAYS = 180  # 6 months
    HIGH_TRAFFIC_THRESHOLD = 1000  # views
    VERY_HIGH_TRAFFIC_THRESHOLD = 5000  # views
    LOW_TRAFFIC_THRESHOLD = 100  # views
    HIGH_ENGAGEMENT_THRESHOLD = 2.0  # views per day
    LOW_ENGAGEMENT_THRESHOLD = 0.5  # views per day
    TRENDING_MULTIPLIER = 2.0  # Current rate vs historical average

    def __init__(self, articles: List[Article]):
        """
        Initialize analyzer with articles.

        Args:
            articles: List of Article objects to analyze
        """
        self.articles = articles
        self._calculate_stats()

    def _calculate_stats(self):
        """Pre-calculate statistics for relative comparisons"""
        if not self.articles:
            self.avg_views = 0
            self.avg_engagement = 0
            return

        total_views = sum(a.view_count for a in self.articles)
        self.avg_views = total_views / len(self.articles)

        # Calculate average engagement score
        engagement_scores = []
        for article in self.articles:
            days_old = article.days_since_update() or 1
            if days_old > 0:
                engagement_scores.append(article.view_count / days_old)

        self.avg_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0

    def calculate_urgency_score(self, article: Article) -> ArticleRiskScore:
        """
        Calculate comprehensive urgency score for an article.

        Scoring factors:
        - Stale + High Views = CRITICAL (100+ points)
        - Stale + Medium Views = HIGH (50-80 points)
        - Trending up but outdated = HIGH (50+ points)
        - Low engagement + old = MEDIUM (30-50 points)
        - Recent + high views = LOW (monitor only)

        Args:
            article: Article to score

        Returns:
            ArticleRiskScore with detailed assessment
        """
        score = 0
        factors = []
        urgency_reasons = []

        days_since_update = article.days_since_update()
        days_old = (datetime.now() - article.created).days if article.created else days_since_update
        view_count = article.view_count

        # Calculate engagement score (views per day)
        engagement_score = view_count / days_old if days_old > 0 else 0

        # Factor 1: High-traffic stale content (CRITICAL)
        if days_since_update > self.STALE_THRESHOLD_DAYS:
            if view_count > self.VERY_HIGH_TRAFFIC_THRESHOLD:
                score += 100
                factors.append("Very high traffic + stale")
                urgency_reasons.append(f"🔥 Gets {view_count:,} views but hasn't been updated in {days_since_update} days")
            elif view_count > self.HIGH_TRAFFIC_THRESHOLD:
                score += 80
                factors.append("High traffic + stale")
                urgency_reasons.append(f"⚠️ Gets {view_count:,} views but is {days_since_update} days old")
            else:
                score += 30
                factors.append("Stale content")
                urgency_reasons.append(f"📅 Not updated in {days_since_update} days")

        # Factor 2: Trending content that needs updates
        # If article has high recent engagement relative to its lifetime average
        if days_since_update > 90 and engagement_score > self.avg_engagement * self.TRENDING_MULTIPLIER:
            score += 50
            factors.append("Trending but outdated")
            urgency_reasons.append(f"📈 High engagement ({engagement_score:.1f} views/day) but outdated")

        # Factor 3: Low engagement on old content (consider archiving)
        if days_old > self.STALE_THRESHOLD_DAYS and engagement_score < self.LOW_ENGAGEMENT_THRESHOLD:
            score += 25
            factors.append("Low engagement + old")
            urgency_reasons.append(f"📉 Only {engagement_score:.2f} views/day - consider archiving or improving")

        # Factor 4: Very low traffic (potential candidates for consolidation)
        if view_count < self.LOW_TRAFFIC_THRESHOLD and days_old > 90:
            score += 15
            factors.append("Very low traffic")
            urgency_reasons.append(f"👁️ Only {view_count} total views in {days_old} days")

        # Factor 5: High engagement bonus (reduce priority for well-performing recent content)
        if days_since_update < 90 and engagement_score > self.HIGH_ENGAGEMENT_THRESHOLD:
            score -= 20  # Reduce priority for well-maintained high-traffic content
            factors.append("Well-maintained + high engagement")

        # Factor 6: Recent updates (reduce priority)
        if days_since_update < 30:
            score -= 30
            factors.append("Recently updated")

        # Ensure score is non-negative
        score = max(0, score)

        # Determine priority level
        if score >= 80:
            priority = "CRITICAL"
        elif score >= 50:
            priority = "HIGH"
        elif score >= 25:
            priority = "MEDIUM"
        else:
            priority = "LOW"

        # Generate recommended action
        recommended_action = self._get_recommendation(article, score, engagement_score, days_since_update)

        return ArticleRiskScore(
            article=article,
            score=score,
            priority=priority,
            factors=factors,
            recommended_action=recommended_action,
            urgency_reasons=urgency_reasons
        )

    def _get_recommendation(self, article: Article, score: int, engagement_score: float,
                           days_since_update: int) -> str:
        """
        Generate specific actionable recommendation based on article characteristics.

        Args:
            article: Article being analyzed
            score: Calculated urgency score
            engagement_score: Views per day
            days_since_update: Days since last update

        Returns:
            Specific action recommendation
        """
        view_count = article.view_count

        # Critical: High traffic + stale
        if score >= 80 and view_count > self.HIGH_TRAFFIC_THRESHOLD and days_since_update > self.STALE_THRESHOLD_DAYS:
            return "🚨 URGENT: Update immediately - high traffic content is outdated"

        # High priority: Trending but old
        if score >= 50 and engagement_score > self.avg_engagement * self.TRENDING_MULTIPLIER:
            return "⚡ Update trending sections and verify accuracy"

        # Medium priority: Stale but moderate traffic
        if days_since_update > self.STALE_THRESHOLD_DAYS and view_count > 500:
            return "📝 Schedule content review and update"

        # Low engagement: Consider archiving
        if engagement_score < self.LOW_ENGAGEMENT_THRESHOLD and days_since_update > self.STALE_THRESHOLD_DAYS:
            if view_count < self.LOW_TRAFFIC_THRESHOLD:
                return "🗑️ Consider archiving or consolidating with related articles"
            else:
                return "🔄 Improve content quality or SEO to boost engagement"

        # Recent updates: monitor
        if days_since_update < 90:
            return "✅ Monitor for quality and user feedback"

        # Default
        return "📊 Schedule regular review"

    def analyze(self, min_priority: Optional[str] = None) -> PriorityQueueReport:
        """
        Analyze all articles and generate prioritized report.

        Args:
            min_priority: Optional filter - only return articles with this priority or higher
                         Options: 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'

        Returns:
            PriorityQueueReport with articles categorized by priority
        """
        # Calculate risk scores for all articles
        scored_articles = [self.calculate_urgency_score(article) for article in self.articles]

        # Categorize by priority
        critical = [a for a in scored_articles if a.priority == "CRITICAL"]
        high = [a for a in scored_articles if a.priority == "HIGH"]
        medium = [a for a in scored_articles if a.priority == "MEDIUM"]
        low = [a for a in scored_articles if a.priority == "LOW"]

        # Sort each category by score (descending)
        critical.sort(key=lambda x: x.score, reverse=True)
        high.sort(key=lambda x: x.score, reverse=True)
        medium.sort(key=lambda x: x.score, reverse=True)
        low.sort(key=lambda x: x.score, reverse=True)

        # Apply priority filter if specified
        priority_levels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        if min_priority and min_priority.upper() in priority_levels:
            min_index = priority_levels.index(min_priority.upper())
            if min_index > 0:
                low = []
            if min_index > 1:
                medium = []
            if min_index > 2:
                high = []

        # Get project_id from first article if available
        project_id = self.articles[0].project_id if self.articles and self.articles[0].project_id else "unknown"

        return PriorityQueueReport(
            project_id=project_id,
            total_articles=len(self.articles),
            critical_articles=critical,
            high_articles=high,
            medium_articles=medium,
            low_articles=low,
            generated_at=datetime.now()
        )

    def get_top_priorities(self, limit: int = 10) -> List[ArticleRiskScore]:
        """
        Get top N articles requiring immediate attention.

        Args:
            limit: Maximum number of articles to return

        Returns:
            List of ArticleRiskScore sorted by urgency (highest first)
        """
        scored_articles = [self.calculate_urgency_score(article) for article in self.articles]
        scored_articles.sort(key=lambda x: x.score, reverse=True)
        return scored_articles[:limit]

    def get_archive_candidates(self, max_engagement: float = 0.5,
                               min_age_days: int = 180) -> List[ArticleRiskScore]:
        """
        Identify articles that could potentially be archived.

        Articles with very low engagement over a long period may be candidates
        for archiving or consolidation.

        Args:
            max_engagement: Maximum views per day threshold
            min_age_days: Minimum age in days

        Returns:
            List of ArticleRiskScore for potential archive candidates
        """
        candidates = []

        for article in self.articles:
            days_old = article.days_since_update()
            if days_old >= min_age_days:
                engagement = article.view_count / days_old if days_old > 0 else 0
                if engagement <= max_engagement:
                    risk_score = self.calculate_urgency_score(article)
                    candidates.append(risk_score)

        candidates.sort(key=lambda x: x.article.view_count)  # Sort by views (lowest first)
        return candidates
