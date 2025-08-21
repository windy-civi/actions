#!/usr/bin/env python3
"""
CLI Tool for State Bill Analysis

Simple command-line interface for analyzing state legislative bills with LLM.
"""

import click
import json
from pathlib import Path
import sys
import os

# Add the current directory to the path
sys.path.append(str(Path(__file__).parent))

from utils.simple_llm_agent import SimpleLLMAgent


@click.command()
@click.option(
    "--state",
    "-s",
    required=True,
    help="State abbreviation (e.g., wy, tx, il)",
)
@click.option(
    "--output",
    "-o",
    default="bill_analysis_report.json",
    help="Output file for the report",
)
@click.option(
    "--api-key",
    "-k",
    envvar="OPENAI_API_KEY",
    help="OpenAI API key (or set OPENAI_API_KEY env var)",
)
@click.option(
    "--show-summary", is_flag=True, help="Show human-readable summary in terminal"
)
@click.option(
    "--verbose", "-v", is_flag=True, help="Show detailed progress information"
)
def analyze(state, output, api_key, show_summary, verbose):
    """
    Analyze state legislative bills with LLM.

    This tool will:
    1. Find all bills in data_processed directory
    2. Analyze each bill's metadata and content
    3. Generate a comprehensive analysis report

    Example:
        python cli_bill_tracker.py analyze --show-summary
    """

    if verbose:
        click.echo("🤖 State Bill Analysis CLI")
        click.echo("=" * 50)

    # Check if data_processed directory exists
    data_processed_path = Path("data_output/data_processed")
    if not data_processed_path.exists():
        click.echo(
            f"❌ Data processed directory not found: {data_processed_path}", err=True
        )
        click.echo("Make sure the data pipeline has been run first", err=True)
        return 1

    # Find all bill files in the correct structure
    # Look for: data_processed/country:us/state:{state}/sessions/*/bills/*.json
    bill_files = list(
        data_processed_path.glob(f"country:us/state:{state}/sessions/*/bills/*.json")
    )
    if not bill_files:
        click.echo(f"❌ No bill files found in {data_processed_path}", err=True)
        click.echo(
            "Expected structure: data_processed/country:us/state:*/sessions/*/bills/*.json",
            err=True,
        )
        return 1

    if verbose:
        click.echo(f"📄 Found {len(bill_files)} bill files")

    # Initialize LLM agent
    agent = SimpleLLMAgent(api_key)

    # Analyze each bill file
    results = []
    for bill_file in bill_files[:10]:  # Limit to first 10 bills for now
        if verbose:
            click.echo(f"📋 Analyzing {bill_file.name}...")

        try:
            with open(bill_file, "r") as f:
                metadata = json.load(f)

            # Extract session and state info from path
            path_parts = bill_file.parts
            state_part = next(
                (part for part in path_parts if part.startswith("state:")), "unknown"
            )
            session_part = next(
                (part for part in path_parts if part.isdigit()), "unknown"
            )

            # Analyze the bill metadata
            analysis = agent.analyze_bill_content(
                str(metadata),
                f"Bill {bill_file.stem} from {state_part} session {session_part}",
            )

            results.append(
                {
                    "bill_id": bill_file.stem,
                    "state": state_part,
                    "session": session_part,
                    "file_path": str(bill_file),
                    "analysis": analysis,
                }
            )

            if verbose:
                click.echo(f"✅ Analyzed {bill_file.name}")
        except Exception as e:
            if verbose:
                click.echo(f"❌ Error analyzing {bill_file.name}: {e}")
            continue

    # Save results
    with open(output, "w") as f:
        json.dump(results, f, indent=2)

    if show_summary:
        click.echo("\n📊 Analysis Summary")
        click.echo("=" * 50)
        for result in results:
            click.echo(f"📄 {result['bill_id']} ({result['session']})")
            if "analysis" in result and "key_topics" in result["analysis"]:
                click.echo(f"   Topics: {', '.join(result['analysis']['key_topics'])}")
            click.echo()

    click.echo(f"✅ Analysis complete! Results saved to {output}")
    return 0


if __name__ == "__main__":
    analyze()
