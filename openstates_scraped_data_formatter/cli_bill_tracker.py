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
import requests
import time

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
@click.option(
    "--download-pdfs", is_flag=True, help="Download PDFs from URLs in metadata for analysis"
)
def analyze(state, output, api_key, show_summary, verbose, download_pdfs):
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

    # Find all bill metadata files in the correct structure
    # Look for: data_processed/country:us/state:{state}/sessions/*/bills/*/metadata.json
    bill_metadata_files = list(
        data_processed_path.glob(
            f"country:us/state:{state}/sessions/*/bills/*/metadata.json"
        )
    )
    if not bill_metadata_files:
        click.echo(
            f"❌ No bill metadata files found in {data_processed_path}", err=True
        )
        click.echo(
            "Expected structure: data_processed/country:us/state:*/sessions/*/bills/*/metadata.json",
            err=True,
        )
        return 1

    if verbose:
        click.echo(f"📄 Found {len(bill_metadata_files)} bill metadata files")

    # Initialize LLM agent
    agent = SimpleLLMAgent(api_key)

    # Analyze each bill metadata file
    results = []
    for metadata_file in bill_metadata_files:  # Analyze all bills
        if verbose:
            click.echo(f"📋 Analyzing {metadata_file.parent.name}...")

        try:
            with open(metadata_file, "r") as f:
                metadata = json.load(f)

            # Extract session and state info from path
            path_parts = metadata_file.parts
            state_part = next(
                (part for part in path_parts if part.startswith("state:")), "unknown"
            )
            session_part = next(
                (part for part in path_parts if part.isdigit()), "unknown"
            )
            bill_id = metadata_file.parent.name  # The bill folder name (e.g., HB0001)

            # Look for extracted bill text files
            files_dir = metadata_file.parent / "files"
            bill_text = ""

            # If download_pdfs is enabled, try to download PDFs from metadata URLs
            if download_pdfs:
                try:
                    # Look for PDF URLs in metadata
                    versions = metadata.get("versions", [])
                    pdf_urls = []
                    
                    for version in versions:
                        links = version.get("links", [])
                        for link in links:
                            url = link.get("url", "")
                            media_type = link.get("media_type", "")
                            if url and "pdf" in media_type.lower():
                                pdf_urls.append(url)
                    
                    if pdf_urls and verbose:
                        click.echo(f"   🔗 Found {len(pdf_urls)} PDF URLs in metadata")
                    
                    # Download and analyze first PDF
                    if pdf_urls:
                        try:
                            import pdfplumber
                            import io
                            
                            # Download first PDF
                            response = requests.get(pdf_urls[0], timeout=30)
                            response.raise_for_status()
                            
                            # Extract text from PDF
                            pdf_file = io.BytesIO(response.content)
                            with pdfplumber.open(pdf_file) as pdf:
                                pdf_content = ""
                                for page in pdf.pages[:5]:  # Limit to first 5 pages
                                    page_text = page.extract_text()
                                    if page_text:
                                        pdf_content += page_text + "\n\n"
                                
                                if pdf_content:
                                    bill_text = f"[PDF CONTENT FROM URL]\n\n{pdf_content[:5000]}..."
                                    if verbose:
                                        click.echo(f"   🤖 Downloaded and extracted {len(pdf_content)} characters from PDF URL")
                            
                            time.sleep(1)  # Be respectful to servers
                            
                        except Exception as e:
                            if verbose:
                                click.echo(f"   ⚠️ Could not download PDF from URL: {e}")
                
                except Exception as e:
                    if verbose:
                        click.echo(f"   ⚠️ Error processing PDF URLs: {e}")

            if files_dir.exists():
                # Look for extracted text files
                text_files = list(files_dir.glob("*_extracted.txt"))
                if text_files:
                    # Read the first (or most recent) extracted text file
                    with open(text_files[0], "r", encoding="utf-8") as f:
                        bill_text = f.read()
                    if verbose:
                        click.echo(
                            f"   📄 Found extracted text: {len(bill_text)} characters"
                        )
                else:
                    # Look for original PDF/XML files
                    pdf_files = list(files_dir.glob("*.pdf"))
                    xml_files = list(files_dir.glob("*.xml"))
                    if pdf_files or xml_files:
                        if verbose:
                            click.echo(
                                f"   📄 Found original files (PDF: {len(pdf_files)}, XML: {len(xml_files)})"
                            )
                        
                        # Try to read PDF content for LLM analysis
                        if pdf_files:
                            try:
                                import pdfplumber
                                pdf_content = ""
                                for pdf_file in pdf_files[:3]:  # Limit to first 3 PDFs
                                    with pdfplumber.open(pdf_file) as pdf:
                                        for page in pdf.pages[:5]:  # Limit to first 5 pages
                                            page_text = page.extract_text()
                                            if page_text:
                                                pdf_content += page_text + "\n\n"
                                
                                if pdf_content:
                                    bill_text = f"[PDF CONTENT FOR LLM ANALYSIS]\n\n{pdf_content[:5000]}..."  # Limit content length
                                    if verbose:
                                        click.echo(f"   🤖 Extracted {len(pdf_content)} characters from PDF for LLM analysis")
                            except Exception as e:
                                if verbose:
                                    click.echo(f"   ⚠️ Could not read PDF: {e}")
                                bill_text = f"[Bill text available in {len(pdf_files)} PDF and {len(xml_files)} XML files]"
                        else:
                            bill_text = f"[Bill text available in {len(pdf_files)} PDF and {len(xml_files)} XML files]"

            # Combine metadata and bill text for analysis
            analysis_content = {
                "metadata": metadata,
                "bill_text": bill_text if bill_text else "No extracted text available",
            }

            # Analyze the combined content
            analysis = agent.analyze_bill_content(
                str(analysis_content),
                f"Bill {bill_id} from {state_part} session {session_part}",
            )

            results.append(
                {
                    "bill_id": bill_id,
                    "state": state_part,
                    "session": session_part,
                    "file_path": str(metadata_file),
                    "analysis": analysis,
                }
            )

            if verbose:
                click.echo(f"✅ Analyzed {bill_id}")
        except Exception as e:
            if verbose:
                click.echo(f"❌ Error analyzing {metadata_file.parent.name}: {e}")
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
