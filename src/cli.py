"""Command-line interface for YouTrack KB Helper"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from tabulate import tabulate

from .config import Config
from .api.client import YouTrackClient, YouTrackAPIError
from .analyzers.stale_content import StaleContentAnalyzer


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
    elif args.command == "test-connection":
        return cmd_test_connection(args, config)

    return 0


if __name__ == "__main__":
    sys.exit(main())
