#!/usr/bin/env python3
"""
Test script for the Priority Queue Analyzer

This script tests the ArticleRiskAnalyzer with sample data.
"""

from datetime import datetime, timedelta
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.models.article import Article
from src.analyzers.priority import ArticleRiskAnalyzer


def create_sample_articles():
    """Create sample articles with various characteristics for testing"""
    now = datetime.now()
    articles = []

    # 1. CRITICAL: Very stale + very high views
    articles.append(Article(
        id="KB-1001",
        summary="Authentication Guide - OAuth 2.0 Setup",
        created=now - timedelta(days=400),
        updated=now - timedelta(days=250),
        view_count=5234,
        project_id="TEST"
    ))

    # 2. CRITICAL: Stale + high views
    articles.append(Article(
        id="KB-1002",
        summary="Database Migration Guide",
        created=now - timedelta(days=365),
        updated=now - timedelta(days=200),
        view_count=3500,
        project_id="TEST"
    ))

    # 3. HIGH: Moderately stale + high views
    articles.append(Article(
        id="KB-1003",
        summary="API Integration Tutorial",
        created=now - timedelta(days=300),
        updated=now - timedelta(days=150),
        view_count=2800,
        project_id="TEST"
    ))

    # 4. MEDIUM: Old + low engagement
    articles.append(Article(
        id="KB-1004",
        summary="Legacy System Documentation",
        created=now - timedelta(days=400),
        updated=now - timedelta(days=380),
        view_count=250,
        project_id="TEST"
    ))

    # 5. LOW: Recent + high engagement
    articles.append(Article(
        id="KB-1005",
        summary="New Feature Announcement - 2024",
        created=now - timedelta(days=30),
        updated=now - timedelta(days=5),
        view_count=1500,
        project_id="TEST"
    ))

    # 6. LOW: Recent + moderate views
    articles.append(Article(
        id="KB-1006",
        summary="Weekly Tips and Tricks",
        created=now - timedelta(days=60),
        updated=now - timedelta(days=10),
        view_count=800,
        project_id="TEST"
    ))

    # 7. MEDIUM: Very low traffic + old
    articles.append(Article(
        id="KB-1007",
        summary="Archived Tool Documentation",
        created=now - timedelta(days=500),
        updated=now - timedelta(days=450),
        view_count=75,
        project_id="TEST"
    ))

    # 8. HIGH: High engagement but outdated
    articles.append(Article(
        id="KB-1008",
        summary="Deployment Best Practices",
        created=now - timedelta(days=200),
        updated=now - timedelta(days=120),
        view_count=4200,
        project_id="TEST"
    ))

    return articles


def print_separator(char="=", length=80):
    """Print a separator line"""
    print(char * length)


def test_priority_analyzer():
    """Test the priority analyzer with sample data"""
    print_separator()
    print("PRIORITY QUEUE ANALYZER - TEST")
    print_separator()
    print()

    # Create sample articles
    articles = create_sample_articles()
    print(f"✓ Created {len(articles)} sample articles")
    print()

    # Initialize analyzer
    analyzer = ArticleRiskAnalyzer(articles)
    print(f"✓ Initialized ArticleRiskAnalyzer")
    print(f"  - Average views: {analyzer.avg_views:.1f}")
    print(f"  - Average engagement: {analyzer.avg_engagement:.2f} views/day")
    print()

    # Run analysis
    report = analyzer.analyze()
    print("✓ Analysis complete!")
    print()

    print_separator("-")
    print("SUMMARY STATISTICS")
    print_separator("-")
    print(f"Total Articles:       {report.total_articles}")
    print(f"Critical Priority:    {report.critical_count}")
    print(f"High Priority:        {report.high_count}")
    print(f"Medium Priority:      {report.medium_count}")
    print(f"Low Priority:         {report.low_count}")
    print(f"Action Required:      {report.action_required_count} (CRITICAL + HIGH)")
    print()

    # Display articles by priority
    priorities = [
        ("CRITICAL", report.critical_articles, "🔴"),
        ("HIGH", report.high_articles, "🟠"),
        ("MEDIUM", report.medium_articles, "🟡"),
        ("LOW", report.low_articles, "🟢")
    ]

    for priority_name, articles_list, emoji in priorities:
        if articles_list:
            print_separator("-")
            print(f"{emoji} {priority_name} PRIORITY ({len(articles_list)} articles)")
            print_separator("-")

            for risk_score in articles_list:
                article = risk_score.article
                print()
                print(f"📄 {article.summary} ({article.id})")
                print(f"   Score: {risk_score.score}")
                print(f"   Days since update: {article.days_since_update()}")
                print(f"   View count: {article.view_count:,}")
                print(f"   Engagement: {article.view_count / article.days_since_update():.2f} views/day")
                print(f"   Factors: {', '.join(risk_score.factors)}")
                print(f"   🎯 Action: {risk_score.recommended_action}")

                if risk_score.urgency_reasons:
                    print("   Reasons:")
                    for reason in risk_score.urgency_reasons:
                        print(f"      • {reason}")
            print()

    # Test get_top_priorities
    print_separator("-")
    print("TOP 5 PRIORITIES")
    print_separator("-")
    top_5 = analyzer.get_top_priorities(limit=5)
    for i, risk_score in enumerate(top_5, 1):
        article = risk_score.article
        print(f"{i}. [{risk_score.priority}] {article.summary} (Score: {risk_score.score})")
    print()

    # Test get_archive_candidates
    print_separator("-")
    print("ARCHIVE CANDIDATES (Low engagement + old)")
    print_separator("-")
    archive_candidates = analyzer.get_archive_candidates(max_engagement=0.5, min_age_days=180)
    if archive_candidates:
        for risk_score in archive_candidates:
            article = risk_score.article
            engagement = article.view_count / article.days_since_update()
            print(f"• {article.summary} - {article.view_count} views, {engagement:.2f} views/day")
    else:
        print("No archive candidates found.")
    print()

    print_separator()
    print("✓ ALL TESTS COMPLETED SUCCESSFULLY")
    print_separator()


if __name__ == "__main__":
    try:
        test_priority_analyzer()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
