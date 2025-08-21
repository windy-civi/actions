#!/usr/bin/env python3
"""
Wyoming Bill Tracker with LLM Analysis

This system tracks a bill through its legislative journey:
1. Summarizes the original bill
2. Compares each version to the previous one
3. Creates human-readable change summaries
4. Tracks the bill's evolution over time
"""

import json
import pdfplumber
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import sys

# Add the utils directory to the path
sys.path.append(str(Path(__file__).parent / "utils"))

from simple_llm_agent import SimpleLLMAgent


class WyomingBillTracker:
    """
    Tracks a Wyoming bill through its legislative journey using LLM analysis.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the bill tracker."""
        self.agent = SimpleLLMAgent(api_key)
        self.bill_data = {}
        self.versions = {}
        self.summaries = {}
        self.changes = {}

    def load_bill_data(self, metadata_path: str, pdf_dir: str):
        """Load bill metadata and PDF versions."""
        print("📄 Loading bill data...")

        # Load metadata
        with open(metadata_path, "r") as f:
            self.bill_data = json.load(f)

        # Load PDF versions
        pdf_path = Path(pdf_dir)
        for pdf_file in sorted(pdf_path.glob("HB0011_v*.pdf")):
            version_num = pdf_file.stem.split("_v")[1]
            print(f"   Loading version {version_num}...")

            text = self._extract_pdf_text(str(pdf_file))
            if text:
                self.versions[version_num] = {
                    "text": text,
                    "file": pdf_file.name,
                    "timestamp": datetime.now().isoformat(),
                }

        print(f"✅ Loaded {len(self.versions)} versions")

    def _extract_pdf_text(self, pdf_path: str) -> str:
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

    def summarize_original_bill(self) -> Dict[str, Any]:
        """Create a comprehensive summary of the original bill."""
        print("\n📋 Summarizing original bill...")

        if "1" not in self.versions:
            print("❌ No original version found")
            return {}

        original_text = self.versions["1"]["text"]

        # Use LLM to create a comprehensive summary
        summary_prompt = f"""
        Create a comprehensive summary of this legislative bill:

        BILL INFO:
        - Title: {self.bill_data.get('title', 'Unknown')}
        - Bill Number: {self.bill_data.get('identifier', 'Unknown')}
        - Session: {self.bill_data.get('legislative_session', 'Unknown')}

        BILL TEXT:
        {original_text[:3000]}...

        Please provide:
        1. Executive Summary (2-3 sentences)
        2. Main Purpose and Goals
        3. Key Provisions
        4. Impact and Significance
        5. Stakeholders Affected
        6. Timeline/Effective Date

        Return as JSON with these fields.
        """

        # For now, use the basic analysis function
        analysis = self.agent.analyze_bill_content(
            original_text[:2000],
            f"Wyoming {self.bill_data.get('identifier', 'HB0011')} Original",
        )

        # Create a simple summary structure
        summary = {
            "bill_info": {
                "title": self.bill_data.get("title", "Unknown"),
                "identifier": self.bill_data.get("identifier", "Unknown"),
                "session": self.bill_data.get("legislative_session", "Unknown"),
                "sponsors": [
                    s.get("name", "") for s in self.bill_data.get("sponsorships", [])
                ],
            },
            "executive_summary": f"This bill addresses {analysis.get('key_topics', ['legislation'])}",
            "main_purpose": "To be determined by LLM analysis",
            "key_provisions": analysis.get("key_topics", []),
            "impact": "To be determined by LLM analysis",
            "stakeholders": "To be determined by LLM analysis",
            "timeline": "To be determined by LLM analysis",
            "quality_score": analysis.get("quality_score", 0),
            "analysis_timestamp": datetime.now().isoformat(),
        }

        self.summaries["original"] = summary
        print("✅ Original bill summarized")
        return summary

    def track_version_changes(self) -> Dict[str, Any]:
        """Track changes between each version."""
        print("\n🔄 Tracking version changes...")

        version_nums = sorted(self.versions.keys())
        changes = {}

        for i in range(1, len(version_nums)):
            prev_version = version_nums[i - 1]
            curr_version = version_nums[i]

            print(f"   Comparing v{prev_version} → v{curr_version}...")

            # Get version info from metadata
            version_info = self._get_version_info(curr_version)

            # Compare versions using LLM
            comparison = self.agent.compare_versions(
                self.versions[prev_version]["text"][:1500],
                self.versions[curr_version]["text"][:1500],
                f"Version {prev_version}",
                f"Version {curr_version} ({version_info})",
            )

            # Create human-readable change summary
            change_summary = self._create_change_summary(
                prev_version, curr_version, comparison, version_info
            )

            changes[f"v{prev_version}_to_v{curr_version}"] = {
                "from_version": prev_version,
                "to_version": curr_version,
                "version_info": version_info,
                "llm_analysis": comparison,
                "human_summary": change_summary,
                "timestamp": datetime.now().isoformat(),
            }

        self.changes = changes
        print(f"✅ Tracked {len(changes)} version changes")
        return changes

    def _get_version_info(self, version_num: str) -> str:
        """Get version information from metadata."""
        if "versions" in self.bill_data:
            for version in self.bill_data["versions"]:
                # Try to match version number with metadata
                note = version.get("note", "")
                if version_num in note or "Introduced" in note and version_num == "1":
                    return note
        return f"Version {version_num}"

    def _create_change_summary(
        self, prev_version: str, curr_version: str, comparison: Dict, version_info: str
    ) -> str:
        """Create a human-readable summary of changes."""

        # Extract key information
        added_text = comparison.get("added_text", [])
        removed_text = comparison.get("removed_text", [])
        amendments = comparison.get("amendments", [])
        impact = comparison.get("impact", "Unknown")

        # Create summary
        summary_parts = []
        summary_parts.append(f"**Version {curr_version} Changes**")
        summary_parts.append(f"*{version_info}*")
        summary_parts.append("")

        if added_text:
            summary_parts.append("**Added:**")
            for text in added_text[:3]:  # Limit to first 3 additions
                summary_parts.append(f"- {text}")
            if len(added_text) > 3:
                summary_parts.append(f"- ... and {len(added_text) - 3} more additions")

        if removed_text:
            summary_parts.append("**Removed:**")
            for text in removed_text[:3]:  # Limit to first 3 removals
                summary_parts.append(f"- {text}")
            if len(removed_text) > 3:
                summary_parts.append(f"- ... and {len(removed_text) - 3} more removals")

        if amendments:
            summary_parts.append("**Amendments:**")
            for amendment in amendments[:3]:
                summary_parts.append(f"- {amendment}")
            if len(amendments) > 3:
                summary_parts.append(f"- ... and {len(amendments) - 3} more amendments")

        summary_parts.append(f"**Impact:** {impact}")

        return "\n".join(summary_parts)

    def generate_final_report(self) -> Dict[str, Any]:
        """Generate a comprehensive final report."""
        print("\n📊 Generating final report...")

        report = {
            "bill_tracker_info": {
                "bill_identifier": self.bill_data.get("identifier", "Unknown"),
                "total_versions": len(self.versions),
                "analysis_timestamp": datetime.now().isoformat(),
                "llm_model": self.agent.model,
            },
            "original_summary": self.summaries.get("original", {}),
            "version_changes": self.changes,
            "bill_evolution_summary": self._create_evolution_summary(),
        }

        return report

    def _create_evolution_summary(self) -> str:
        """Create a summary of the bill's evolution."""
        if not self.changes:
            return "No changes tracked"

        evolution_parts = []
        evolution_parts.append("**Bill Evolution Summary**")
        evolution_parts.append("")

        total_changes = len(self.changes)
        evolution_parts.append(
            f"This bill went through {total_changes} major revisions:"
        )
        evolution_parts.append("")

        for change_key, change_data in self.changes.items():
            version_info = change_data.get("version_info", "")
            human_summary = change_data.get("human_summary", "")

            # Extract just the key points from the human summary
            lines = human_summary.split("\n")
            key_points = []
            for line in lines:
                if line.startswith("- ") or line.startswith("**Impact:**"):
                    key_points.append(line)

            evolution_parts.append(f"**{version_info}**")
            if key_points:
                evolution_parts.extend(key_points[:2])  # Just first 2 key points
            evolution_parts.append("")

        return "\n".join(evolution_parts)

    def save_report(self, output_path: str = "wyoming_bill_tracker_report.json"):
        """Save the complete report to a file."""
        report = self.generate_final_report()

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"💾 Report saved to {output_path}")
        return output_path


def main():
    """Main function to run the Wyoming bill tracker."""
    print("🤖 Wyoming Bill Tracker with LLM Analysis")
    print("=" * 50)

    # Initialize tracker
    tracker = WyomingBillTracker()

    # Load data
    metadata_path = "sample_data/wy_sample/metadata_wy_SAMPLE.json"
    pdf_dir = "sample_data/wy_sample"

    if not Path(metadata_path).exists():
        print(f"❌ Metadata file not found: {metadata_path}")
        return

    if not Path(pdf_dir).exists():
        print(f"❌ PDF directory not found: {pdf_dir}")
        return

    tracker.load_bill_data(metadata_path, pdf_dir)

    # Summarize original bill
    tracker.summarize_original_bill()

    # Track version changes
    tracker.track_version_changes()

    # Generate and save report
    report_path = tracker.save_report()

    print("\n✅ Analysis complete!")
    print(f"📄 Report saved to: {report_path}")
    print("\n💡 To get real LLM analysis, set your OPENAI_API_KEY environment variable")


if __name__ == "__main__":
    main()
