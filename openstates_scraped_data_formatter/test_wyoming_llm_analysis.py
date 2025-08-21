#!/usr/bin/env python3
"""
Test LLM Agent with Wyoming Bill Data

This script demonstrates how the LLM agent can analyze the Wyoming bill versions
and help with version comparison and strikethrough detection.
"""

import json
import pdfplumber
from pathlib import Path
import sys

# Add the utils directory to the path
sys.path.append(str(Path(__file__).parent / "utils"))

from simple_llm_agent import SimpleLLMAgent


def extract_pdf_text(pdf_path: str) -> str:
    """Extract text from a PDF file."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text_parts = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            return "\n".join(text_parts)
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""


def analyze_wyoming_bill_versions():
    """Analyze the Wyoming bill versions using our LLM agent."""
    print("🤖 Analyzing Wyoming Bill Versions with LLM Agent")
    print("=" * 60)

    # Initialize the LLM agent
    agent = SimpleLLMAgent()

    # Path to Wyoming sample data
    wy_sample_dir = Path("sample_data/wy_sample")

    # Extract text from different versions
    versions = {}

    print("📄 Extracting text from PDF versions...")
    for pdf_file in sorted(wy_sample_dir.glob("HB0011_v*.pdf")):
        version_num = pdf_file.stem.split("_v")[1]
        print(f"   Processing {pdf_file.name}...")

        text = extract_pdf_text(str(pdf_file))
        if text:
            versions[version_num] = text
            print(f"   ✅ Extracted {len(text)} characters")
        else:
            print(f"   ❌ Failed to extract text")

    print(f"\n📊 Extracted {len(versions)} versions")

    # Analyze each version
    print("\n🔍 Analyzing individual versions...")
    version_analyses = {}

    for version_num, text in versions.items():
        print(f"\n📋 Analyzing Version {version_num}...")

        # Get a sample of the text for analysis
        sample_text = text[:2000] if len(text) > 2000 else text

        # Analyze with LLM agent
        analysis = agent.analyze_bill_content(
            sample_text, f"Wyoming HB0011 Version {version_num}"
        )

        version_analyses[version_num] = analysis
        print(f"   Document Type: {analysis.get('document_type', 'Unknown')}")
        print(f"   Quality Score: {analysis.get('quality_score', 'Unknown')}")
        print(f"   Key Topics: {', '.join(analysis.get('key_topics', []))}")

    # Compare versions
    print("\n🔄 Comparing versions...")
    if len(versions) >= 2:
        version_nums = sorted(versions.keys())

        # Compare first and last versions
        v1_num = version_nums[0]
        v2_num = version_nums[-1]

        print(f"\n📊 Comparing Version {v1_num} vs Version {v2_num}...")

        comparison = agent.compare_versions(
            versions[v1_num][:1500],
            versions[v2_num][:1500],
            f"Version {v1_num} (Introduced)",
            f"Version {v2_num} (Final)",
        )

        print("Comparison Results:")
        print(f"   Added Text: {len(comparison.get('added_text', []))} sections")
        print(f"   Removed Text: {len(comparison.get('removed_text', []))} sections")
        print(f"   Amendments: {len(comparison.get('amendments', []))} detected")
        print(f"   Impact: {comparison.get('impact', 'Unknown')}")

    # Test strikethrough detection on the final version
    print("\n🔍 Testing strikethrough detection on final version...")
    final_version = versions.get(version_nums[-1] if version_nums else "8", "")

    if final_version:
        strikethrough_result = agent.detect_strikethroughs(final_version[:2000])

        print("Strikethrough Detection Results:")
        print(
            f"   Has Strikethroughs: {strikethrough_result.get('has_strikethroughs', False)}"
        )
        print(
            f"   Deleted Sections: {len(strikethrough_result.get('deleted_sections', []))}"
        )
        print(
            f"   Changes Detected: {len(strikethrough_result.get('changes_detected', []))}"
        )
        print(f"   Confidence: {strikethrough_result.get('confidence', 'Unknown')}")

    # Save results
    results = {
        "version_analyses": version_analyses,
        "comparison": comparison if "comparison" in locals() else None,
        "strikethrough_detection": (
            strikethrough_result if "strikethrough_result" in locals() else None
        ),
    }

    output_file = Path("llm_analysis_results.json")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Results saved to {output_file}")
    print("\n✅ Analysis complete!")
    print("\n💡 To get real LLM analysis, set your OPENAI_API_KEY environment variable")


if __name__ == "__main__":
    analyze_wyoming_bill_versions()
