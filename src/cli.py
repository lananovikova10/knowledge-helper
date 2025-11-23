"""Command-line interface for YouTrack KB Helper"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from tabulate import tabulate

from .config import Config
from .api.client import YouTrackClient, YouTrackAPIError
from .analyzers.stale_content import StaleContentAnalyzer
from .analyzers.low_engagement import LowEngagementAnalyzer
from .analyzers.duplicates import DuplicateDetector


def format_table_output(report):
    """Format stale article report as a table"""
    if not report.stale_articles:
        return "No stale articles found!"

    # Prepare table data
    headers = ["ID", "Title", "Last Updated", "Days Since Update", "Views"]
    rows = []

    for article in report.get_sorted_articles():
        last_update = article.updated if article.updated else article.created
        rows.append([
            article.id,
            article.summary[:60] + "..." if len(article.summary) > 60 else article.summary,
            last_update.strftime("%Y-%m-%d"),
            article.days_since_update(),
            article.view_count
        ])

    return tabulate(rows, headers=headers, tablefmt="grid")


def format_json_output(report):
    """Format stale article report as JSON"""
    import json

    data = {
        "project_id": report.project_id,
        "threshold_days": report.threshold_days,
        "total_articles": report.total_articles,
        "stale_count": report.stale_count,
        "stale_percentage": round(report.stale_percentage, 2),
        "generated_at": report.generated_at.isoformat(),
        "articles": [
            {
                "id": article.id,
                "summary": article.summary,
                "created": article.created.isoformat(),
                "updated": article.updated.isoformat() if article.updated else None,
                "days_since_update": article.days_since_update(),
                "view_count": article.view_count
            }
            for article in report.get_sorted_articles()
        ]
    }

    return json.dumps(data, indent=2)


def format_csv_output(report):
    """Format stale article report as CSV"""
    import csv
    from io import StringIO

    output = StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(["ID", "Title", "Created", "Last Updated", "Days Since Update", "Views"])

    # Write data rows
    for article in report.get_sorted_articles():
        last_update = article.updated if article.updated else article.created
        writer.writerow([
            article.id,
            article.summary,
            article.created.strftime("%Y-%m-%d %H:%M:%S"),
            last_update.strftime("%Y-%m-%d %H:%M:%S"),
            article.days_since_update(),
            article.view_count
        ])

    return output.getvalue()


def save_report(report, output_file: str, format_type: str):
    """Save report to file"""
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    if format_type == "json":
        content = format_json_output(report)
    elif format_type == "csv":
        content = format_csv_output(report)
    else:
        content = format_table_output(report)

    with open(output_file, 'w') as f:
        f.write(content)

    print(f"\nReport saved to: {output_file}")


def cmd_stale_content(args, config: Config):
    """Handle stale-content command"""
    # Initialize API client
    client = YouTrackClient(config.youtrack_base_url, config.youtrack_token)

    # Test connection
    print("Testing connection to YouTrack...")
    if not client.test_connection():
        print("ERROR: Failed to connect to YouTrack. Please check your credentials.")
        return 1

    print("✓ Connected successfully\n")

    # Get threshold from args or config
    threshold = args.threshold if args.threshold else config.stale_threshold_days

    # Initialize analyzer
    analyzer = StaleContentAnalyzer(client, threshold_days=threshold)

    # Run analysis
    try:
        report = analyzer.analyze(args.project_id, batch_size=config.batch_size)
    except YouTrackAPIError as e:
        print(f"ERROR: {e}")
        return 1

    # Display summary
    print(f"\n{'='*70}")
    print(f"Stale Content Analysis Report")
    print(f"{'='*70}")
    print(f"Project ID: {report.project_id}")
    print(f"Threshold: {report.threshold_days} days")
    print(f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nTotal articles: {report.total_articles}")
    print(f"Stale articles: {report.stale_count} ({report.stale_percentage:.1f}%)")
    print(f"{'='*70}\n")

    # Format output
    output_format = args.format if args.format else config.output_format

    if output_format == "json":
        output = format_json_output(report)
    elif output_format == "csv":
        output = format_csv_output(report)
    else:
        output = format_table_output(report)

    # Display or save output
    if args.output:
        save_report(report, args.output, output_format)
        print("\nPreview:")
        # Show first few lines of table output
        if report.stale_articles:
            print(format_table_output(report).split('\n')[:10])
            if report.stale_count > 5:
                print(f"... and {report.stale_count - 5} more articles (see full report in file)")
    else:
        print(output)

    return 0


def cmd_low_engagement(args, config: Config):
    """Handle low-engagement command"""
    # Initialize API client
    client = YouTrackClient(config.youtrack_base_url, config.youtrack_token)

    # Test connection
    print("Testing connection to YouTrack...")
    if not client.test_connection():
        print("ERROR: Failed to connect to YouTrack. Please check your credentials.")
        return 1

    print("✓ Connected successfully\n")

    # Get parameters from args
    score_threshold = args.score if hasattr(args, 'score') and args.score else 1.0
    min_age_days = args.min_age if args.min_age else 7

    # Initialize analyzer
    analyzer = LowEngagementAnalyzer(client, score_threshold=score_threshold, min_age_days=min_age_days)

    # Run analysis
    try:
        report = analyzer.analyze(args.project_id, batch_size=config.batch_size)
    except YouTrackAPIError as e:
        print(f"ERROR: {e}")
        return 1

    # Display summary
    print(f"\n{'='*70}")
    print(f"Low Engagement Analysis Report")
    print(f"{'='*70}")
    print(f"Project ID: {report.project_id}")
    print(f"Score threshold: ≤ {report.score_threshold} views/day")
    print(f"Minimum age: {report.min_age_days} days (filters out very new articles)")
    print(f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nTotal articles: {report.total_articles}")
    print(f"Low engagement articles: {report.low_engagement_count} ({report.low_engagement_percentage:.1f}%)")
    print(f"{'='*70}\n")

    # Format output
    output_format = args.format if args.format else config.output_format

    if not report.low_engagement_articles:
        print("✓ No low engagement articles found!")
        return 0

    # Prepare table data
    headers = ["ID", "Title", "Views", "Days Old", "Score", "Last Updated"]
    rows = []

    for article in report.get_sorted_articles(sort_by='views'):
        last_update = article.updated if article.updated else article.created
        engagement_score = analyzer.get_engagement_score(article)
        rows.append([
            article.id,
            article.summary[:60] + "..." if len(article.summary) > 60 else article.summary,
            article.view_count,
            article.days_since_update(),
            engagement_score,
            last_update.strftime("%Y-%m-%d")
        ])

    if output_format == "json":
        import json
        data = {
            "project_id": report.project_id,
            "score_threshold": report.score_threshold,
            "min_age_days": report.min_age_days,
            "total_articles": report.total_articles,
            "low_engagement_count": report.low_engagement_count,
            "low_engagement_percentage": round(report.low_engagement_percentage, 2),
            "generated_at": report.generated_at.isoformat(),
            "articles": [
                {
                    "id": article.id,
                    "summary": article.summary,
                    "view_count": article.view_count,
                    "days_since_update": article.days_since_update(),
                    "engagement_score": analyzer.get_engagement_score(article),
                    "last_update": (article.updated if article.updated else article.created).isoformat()
                }
                for article in report.get_sorted_articles()
            ]
        }
        output = json.dumps(data, indent=2)
    elif output_format == "csv":
        import csv
        from io import StringIO
        output_io = StringIO()
        writer = csv.writer(output_io)
        writer.writerow(headers)
        writer.writerows(rows)
        output = output_io.getvalue()
    else:
        output = tabulate(rows, headers=headers, tablefmt="grid")

    # Display or save output
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"\nReport saved to: {args.output}")
        print("\nPreview:")
        print(tabulate(rows[:5], headers=headers, tablefmt="grid"))
        if len(rows) > 5:
            print(f"... and {len(rows) - 5} more articles (see full report in file)")
    else:
        print(output)

    return 0


def cmd_duplicates(args, config: Config):
    """Handle duplicates command"""
    # Initialize API client
    client = YouTrackClient(config.youtrack_base_url, config.youtrack_token)

    # Test connection
    print("Testing connection to YouTrack...")
    if not client.test_connection():
        print("ERROR: Failed to connect to YouTrack. Please check your credentials.")
        return 1

    print("✓ Connected successfully\n")

    # Get parameters from args
    confidence_threshold = args.threshold if hasattr(args, 'threshold') and args.threshold else 0.75

    # Initialize detector
    detector = DuplicateDetector(client, confidence_threshold=confidence_threshold)

    # Run analysis
    try:
        report = detector.analyze(args.project_id, batch_size=config.batch_size)
    except YouTrackAPIError as e:
        print(f"ERROR: {e}")
        return 1

    # Display summary
    print(f"\n{'='*70}")
    print(f"Duplicate Detection Report")
    print(f"{'='*70}")
    print(f"Project ID: {report.project_id}")
    print(f"Confidence threshold: {report.confidence_threshold:.0%}")
    print(f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nTotal articles: {report.total_articles}")
    print(f"Duplicate pairs found: {report.duplicate_count}")
    print(f"Articles with duplicates: {report.articles_with_duplicates}")
    print(f"{'='*70}\n")

    if not report.duplicate_pairs:
        print("✓ No duplicate articles found!")
        return 0

    # Format output
    output_format = args.format if args.format else config.output_format

    if output_format == "json":
        import json
        data = {
            "project_id": report.project_id,
            "confidence_threshold": report.confidence_threshold,
            "total_articles": report.total_articles,
            "duplicate_count": report.duplicate_count,
            "articles_with_duplicates": report.articles_with_duplicates,
            "generated_at": report.generated_at.isoformat(),
            "duplicate_pairs": [
                {
                    "article1_id": pair.article1.id,
                    "article1_title": pair.article1.summary,
                    "article2_id": pair.article2.id,
                    "article2_title": pair.article2.summary,
                    "confidence_score": round(pair.confidence_score, 3),
                    "title_similarity": round(pair.title_similarity, 3),
                    "content_similarity": round(pair.content_similarity, 3),
                    "reasons": pair.reasons
                }
                for pair in report.get_sorted_pairs()
            ]
        }
        output = json.dumps(data, indent=2)
        print(output)
    else:  # table format
        headers = ["Article 1", "Article 2", "Confidence", "Title Sim", "Content Sim", "Reasons"]
        rows = []

        for pair in report.get_sorted_pairs()[:20]:  # Show top 20
            rows.append([
                f"{pair.article1.id}\n{pair.article1.summary[:40]}...",
                f"{pair.article2.id}\n{pair.article2.summary[:40]}...",
                f"{pair.confidence_score:.1%}",
                f"{pair.title_similarity:.1%}",
                f"{pair.content_similarity:.1%}",
                "\n".join(pair.reasons[:2])  # Show first 2 reasons
            ])

        print(tabulate(rows, headers=headers, tablefmt="grid"))

        if report.duplicate_count > 20:
            print(f"\n... and {report.duplicate_count - 20} more duplicate pairs")
            print(f"Use --format json to see all results")

    return 0


def cmd_test_connection(args, config: Config):
    """Handle test-connection command"""
    print("Testing connection to YouTrack...")
    print(f"URL: {config.youtrack_base_url}")

    client = YouTrackClient(config.youtrack_base_url, config.youtrack_token)

    if client.test_connection():
        print("✓ Connection successful!")

        # Try to get project info if provided
        if args.project_id:
            print(f"\nTesting project access: {args.project_id}")
            project = client.get_project_info(args.project_id)
            if project:
                print(f"✓ Project found: {project.get('name', 'N/A')} ({project.get('shortName', 'N/A')})")
            else:
                print(f"✗ Project '{args.project_id}' not found or not accessible")
                return 1
        return 0
    else:
        print("✗ Connection failed. Please check your credentials.")
        return 1


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="YouTrack Knowledge Base Helper - Analyze and maintain KB articles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze stale content with default threshold (180 days)
  %(prog)s stale-content PROJECT_ID

  # Custom threshold
  %(prog)s stale-content PROJECT_ID --threshold 90

  # Save report to JSON file
  %(prog)s stale-content PROJECT_ID --format json --output report.json

  # Test connection
  %(prog)s test-connection --project-id PROJECT_ID

Environment Variables:
  YOUTRACK_BASE_URL - Your YouTrack instance URL (required)
  YOUTRACK_TOKEN    - Your YouTrack API token (required)
  STALE_THRESHOLD_DAYS - Default threshold for stale articles (default: 180)

Configuration:
  Create a .env file in the current directory with:
    YOUTRACK_BASE_URL=https://youtrack.jetbrains.com
    YOUTRACK_TOKEN=your_token_here
        """
    )

    parser.add_argument(
        "--config",
        help="Path to YAML configuration file",
        type=str
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Stale content command
    stale_parser = subparsers.add_parser(
        "stale-content",
        help="Analyze stale (outdated) articles"
    )
    stale_parser.add_argument(
        "project_id",
        help="YouTrack project ID (e.g., HE for Help)"
    )
    stale_parser.add_argument(
        "--threshold",
        type=int,
        help="Days threshold for stale articles (default: from config or 180)"
    )
    stale_parser.add_argument(
        "--format",
        choices=["table", "json", "csv"],
        help="Output format (default: table)"
    )
    stale_parser.add_argument(
        "--output",
        help="Save report to file instead of printing"
    )

    # Low engagement command
    engagement_parser = subparsers.add_parser(
        "low-engagement",
        help="Analyze articles with low engagement (views per day)"
    )
    engagement_parser.add_argument(
        "project_id",
        help="YouTrack project ID (e.g., HE for Help)"
    )
    engagement_parser.add_argument(
        "--score",
        type=float,
        help="Engagement score threshold in views/day (default: 1.0). Articles with score ≤ this are considered low engagement."
    )
    engagement_parser.add_argument(
        "--min-age",
        type=int,
        help="Minimum age in days to include articles (default: 7). Filters out very new articles."
    )
    engagement_parser.add_argument(
        "--format",
        choices=["table", "json", "csv"],
        help="Output format (default: table)"
    )
    engagement_parser.add_argument(
        "--output",
        help="Save report to file instead of printing"
    )

    # Duplicate detection command
    duplicates_parser = subparsers.add_parser(
        "duplicates",
        help="Detect duplicate or similar articles"
    )
    duplicates_parser.add_argument(
        "project_id",
        help="YouTrack project ID (e.g., HE for Help)"
    )
    duplicates_parser.add_argument(
        "--threshold",
        type=float,
        help="Confidence threshold (0.0-1.0, default: 0.75). Higher = stricter matching"
    )
    duplicates_parser.add_argument(
        "--format",
        choices=["table", "json"],
        help="Output format (default: table)"
    )

    # Test connection command
    test_parser = subparsers.add_parser(
        "test-connection",
        help="Test YouTrack API connection"
    )
    test_parser.add_argument(
        "--project-id",
        help="Optional: Test access to specific project"
    )

    args = parser.parse_args()

    # Show help if no command provided
    if not args.command:
        parser.print_help()
        return 0

    # Load configuration
    config = Config(config_file=args.config)

    # Validate configuration
    is_valid, error_msg = config.validate()
    if not is_valid:
        print(f"Configuration Error: {error_msg}")
        print("\nPlease create a .env file with:")
        print("  YOUTRACK_BASE_URL=https://youtrack.jetbrains.com")
        print("  YOUTRACK_TOKEN=your_token_here")
        return 1

    # Route to appropriate command handler
    if args.command == "stale-content":
        return cmd_stale_content(args, config)
    elif args.command == "low-engagement":
        return cmd_low_engagement(args, config)
    elif args.command == "duplicates":
        return cmd_duplicates(args, config)
    elif args.command == "test-connection":
        return cmd_test_connection(args, config)

    return 0


if __name__ == "__main__":
    sys.exit(main())
