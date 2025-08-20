#!/usr/bin/env python3
"""
Compare different versions of the same bill to understand what changes.
"""

import difflib
from pathlib import Path
import json
from typing import Dict, List, Tuple


def load_extracted_text(file_path: Path) -> str:
    """Load extracted text from file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return ""


def compare_bill_versions():
    """Compare different versions of HR1 to understand changes."""

    extracted_dir = Path("sample_data/extracted_text")

    # Load all HR1 versions
    hr1_files = {
        "Reported in House": extracted_dir / "BILLS-119hr1rh_extracted.txt",
        "Engrossed in House": extracted_dir / "BILLS-119hr1eh_extracted.txt",
        "Placed on Calendar Senate": extracted_dir / "BILLS-119hr1pcs_extracted.txt",
        "Enrolled Bill": extracted_dir / "BILLS-119hr1enr_extracted.txt",
    }

    print("📊 COMPARING HR1 VERSIONS")
    print("=" * 80)

    # Load all versions
    versions = {}
    for version_name, file_path in hr1_files.items():
        if file_path.exists():
            content = load_extracted_text(file_path)
            versions[version_name] = content
            print(f"✅ Loaded {version_name}: {len(content):,} characters")
        else:
            print(f"❌ Missing {version_name}: {file_path}")

    if len(versions) < 2:
        print("Need at least 2 versions to compare")
        return

    # Compare versions
    print("\n" + "=" * 80)
    print("🔍 VERSION COMPARISONS")
    print("=" * 80)

    # Compare Reported vs Enrolled (most dramatic change)
    if "Reported in House" in versions and "Enrolled Bill" in versions:
        print("\n📋 REPORTED vs ENROLLED (Major Changes)")
        print("-" * 60)

        reported = versions["Reported in House"]
        enrolled = versions["Enrolled Bill"]

        # Basic stats
        print(f"Reported length: {len(reported):,} characters")
        print(f"Enrolled length: {len(enrolled):,} characters")
        print(
            f"Size difference: {len(enrolled) - len(reported):,} characters ({((len(enrolled) - len(reported)) / len(reported) * 100):.1f}%)"
        )

        # Find major differences
        reported_lines = reported.split("\n")
        enrolled_lines = enrolled.split("\n")

        # Compare titles
        reported_title = reported_lines[0] if reported_lines else ""
        enrolled_title = enrolled_lines[0] if enrolled_lines else ""

        print(f"\nTitle changes:")
        print(f"  Reported: {reported_title}")
        print(f"  Enrolled: {enrolled_title}")

        # Look for section differences
        reported_sections = [
            line for line in reported_lines if line.strip().startswith("Sec.")
        ]
        enrolled_sections = [
            line for line in enrolled_lines if line.strip().startswith("Sec.")
        ]

        print(f"\nSection counts:")
        print(f"  Reported: {len(reported_sections)} sections")
        print(f"  Enrolled: {len(enrolled_sections)} sections")

        # Find unique sections
        reported_set = set(reported_sections)
        enrolled_set = set(enrolled_sections)

        added_sections = enrolled_set - reported_set
        removed_sections = reported_set - enrolled_set

        print(f"\nSection changes:")
        print(f"  Added: {len(added_sections)} sections")
        print(f"  Removed: {len(removed_sections)} sections")

        if added_sections:
            print(f"\nSample added sections:")
            for section in list(added_sections)[:5]:
                print(f"  + {section}")

        if removed_sections:
            print(f"\nSample removed sections:")
            for section in list(removed_sections)[:5]:
                print(f"  - {section}")

    # Compare all versions for progression
    print("\n" + "=" * 80)
    print("📈 VERSION PROGRESSION")
    print("=" * 80)

    version_order = [
        "Reported in House",
        "Engrossed in House",
        "Placed on Calendar Senate",
        "Enrolled Bill",
    ]
    available_versions = [v for v in version_order if v in versions]

    print(f"Version progression: {' → '.join(available_versions)}")

    for i, version in enumerate(available_versions):
        content = versions[version]
        print(f"\n{version}:")
        print(f"  Length: {len(content):,} characters")
        lines_count = len(content.split("\n"))
        print(f"  Lines: {lines_count:,}")

        # Count sections
        sections = [
            line for line in content.split("\n") if line.strip().startswith("Sec.")
        ]
        print(f"  Sections: {len(sections):,}")

        # Show title
        lines = content.split("\n")
        title = lines[0] if lines else "No title"
        print(f"  Title: {title}")

    # Save comparison data
    comparison_data = {"version_stats": {}, "section_changes": {}}

    for version_name, content in versions.items():
        lines = content.split("\n")
        sections = [line for line in lines if line.strip().startswith("Sec.")]

        comparison_data["version_stats"][version_name] = {
            "length": len(content),
            "lines": len(lines),
            "sections": len(sections),
            "title": lines[0] if lines else "",
        }

    # Save to file
    comparison_file = Path("sample_data/version_comparison_detailed.json")
    with open(comparison_file, "w") as f:
        json.dump(comparison_data, f, indent=2)

    print(f"\nSaved detailed comparison to: {comparison_file}")


if __name__ == "__main__":
    compare_bill_versions()
