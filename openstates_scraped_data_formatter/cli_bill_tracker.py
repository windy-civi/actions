#!/usr/bin/env python3
"""
CLI Tool for Wyoming Bill Tracker

Simple command-line interface for tracking bill evolution with LLM analysis.
"""

import click
import json
from pathlib import Path
import sys

# Add the current directory to the path
sys.path.append(str(Path(__file__).parent))

from wyoming_bill_tracker import WyomingBillTracker


@click.group()
def cli():
    """Track Wyoming bills through their legislative journey with LLM analysis."""
    pass


@cli.command()
@click.option(
    "--metadata",
    "-m",
    default="sample_data/wy_sample/metadata_wy_SAMPLE.json",
    help="Path to bill metadata JSON file",
)
@click.option(
    "--pdf-dir",
    "-p",
    default="sample_data/wy_sample",
    help="Directory containing PDF versions",
)
@click.option(
    "--output",
    "-o",
    default="bill_tracker_report.json",
    help="Output file for the report",
)
@click.option(
    "--api-key",
    "-k",
    envvar="OPENAI_API_KEY",
    help="OpenAI API key (or set OPENAI_API_KEY env var)",
)
@click.option(
    "--show-summary", "-s", is_flag=True, help="Show human-readable summary in terminal"
)
@click.option(
    "--verbose", "-v", is_flag=True, help="Show detailed progress information"
)
def analyze(metadata, pdf_dir, output, api_key, show_summary, verbose):
    """
    Track a Wyoming bill through its legislative journey with LLM analysis.

    This tool will:
    1. Load bill metadata and PDF versions
    2. Summarize the original bill
    3. Track changes between each version
    4. Generate a comprehensive report

    Example:
        python cli_bill_tracker.py --show-summary
    """

    if verbose:
        click.echo("🤖 Wyoming Bill Tracker CLI")
        click.echo("=" * 50)

    # Check if files exist
    if not Path(metadata).exists():
        click.echo(f"❌ Metadata file not found: {metadata}", err=True)
        return 1

    if not Path(pdf_dir).exists():
        click.echo(f"❌ PDF directory not found: {pdf_dir}", err=True)
        return 1

    # Initialize tracker
    tracker = WyomingBillTracker(api_key)

    # Load data
    if verbose:
        click.echo("📄 Loading bill data...")

    tracker.load_bill_data(metadata, pdf_dir)

    # Summarize original bill
    if verbose:
        click.echo("📋 Summarizing original bill...")

    summary = tracker.summarize_original_bill()

    # Track version changes
    if verbose:
        click.echo("🔄 Tracking version changes...")

    changes = tracker.track_version_changes()

    # Generate and save report
    if verbose:
        click.echo("📊 Generating final report...")

    report_path = tracker.save_report(output)

    # Show summary if requested
    if show_summary:
        click.echo("\n" + "=" * 60)
        click.echo("📋 BILL TRACKER SUMMARY")
        click.echo("=" * 60)

        # Bill info
        bill_info = summary.get("bill_info", {})
        click.echo(f"📄 Bill: {bill_info.get('identifier', 'Unknown')}")
        click.echo(f"📝 Title: {bill_info.get('title', 'Unknown')}")
        click.echo(f"🏛️ Session: {bill_info.get('session', 'Unknown')}")
        click.echo(f"👥 Sponsors: {', '.join(bill_info.get('sponsors', []))}")

        # Executive summary
        click.echo(f"\n📋 Executive Summary:")
        click.echo(f"   {summary.get('executive_summary', 'No summary available')}")

        # Key provisions
        provisions = summary.get("key_provisions", [])
        if provisions:
            click.echo(f"\n🔑 Key Provisions:")
            for provision in provisions:
                click.echo(f"   • {provision}")

        # Version changes
        click.echo(f"\n🔄 Version Changes ({len(changes)} total):")
        for change_key, change_data in changes.items():
            version_info = change_data.get("version_info", "")
            click.echo(f"   • {change_key}: {version_info}")

        # Evolution summary
        evolution = tracker._create_evolution_summary()
        if evolution and evolution != "No changes tracked":
            click.echo(f"\n📈 Bill Evolution:")
            # Show just the first few lines of evolution
            lines = evolution.split("\n")[:10]
            for line in lines:
                if line.strip():
                    click.echo(f"   {line}")

    click.echo(f"\n✅ Analysis complete!")
    click.echo(f"📄 Report saved to: {report_path}")

    if not api_key:
        click.echo(
            "\n💡 To get real LLM analysis, set your OPENAI_API_KEY environment variable"
        )
        click.echo("   Example: export OPENAI_API_KEY='your-api-key-here'")

    return 0


@cli.command()
@click.argument("report_file", default="bill_tracker_report.json")
def show_report(report_file):
    """
    Display a bill tracker report in a human-readable format.

    Example:
        python cli_bill_tracker.py show-report my_report.json
    """

    if not Path(report_file).exists():
        click.echo(f"❌ Report file not found: {report_file}", err=True)
        return 1

    # Load and display report
    with open(report_file, "r") as f:
        report = json.load(f)

    click.echo("📊 BILL TRACKER REPORT")
    click.echo("=" * 60)

    # Bill tracker info
    tracker_info = report.get("bill_tracker_info", {})
    click.echo(f"📄 Bill: {tracker_info.get('bill_identifier', 'Unknown')}")
    click.echo(f"📊 Total Versions: {tracker_info.get('total_versions', 0)}")
    click.echo(f"🕒 Analysis Time: {tracker_info.get('analysis_timestamp', 'Unknown')}")
    click.echo(f"🤖 LLM Model: {tracker_info.get('llm_model', 'Unknown')}")

    # Original summary
    original = report.get("original_summary", {})
    if original:
        click.echo(f"\n📋 ORIGINAL BILL SUMMARY")
        click.echo("-" * 40)

        bill_info = original.get("bill_info", {})
        click.echo(f"Title: {bill_info.get('title', 'Unknown')}")
        click.echo(f"Session: {bill_info.get('session', 'Unknown')}")
        click.echo(f"Sponsors: {', '.join(bill_info.get('sponsors', []))}")

        click.echo(f"\nExecutive Summary:")
        click.echo(f"  {original.get('executive_summary', 'No summary available')}")

        provisions = original.get("key_provisions", [])
        if provisions:
            click.echo(f"\nKey Provisions:")
            for provision in provisions:
                click.echo(f"  • {provision}")

        click.echo(f"\nQuality Score: {original.get('quality_score', 'Unknown')}/10")

    # Version changes
    changes = report.get("version_changes", {})
    if changes:
        click.echo(f"\n🔄 VERSION CHANGES")
        click.echo("-" * 40)

        for change_key, change_data in changes.items():
            version_info = change_data.get("version_info", "")
            human_summary = change_data.get("human_summary", "")

            click.echo(f"\n{change_key}: {version_info}")

            # Show key points from human summary
            lines = human_summary.split("\n")
            for line in lines:
                if line.startswith("- ") or line.startswith("**Impact:**"):
                    click.echo(f"  {line}")

    # Evolution summary
    evolution = report.get("bill_evolution_summary", "")
    if evolution and evolution != "No changes tracked":
        click.echo(f"\n📈 BILL EVOLUTION")
        click.echo("-" * 40)
        click.echo(evolution)

    return 0


if __name__ == "__main__":
    cli()
