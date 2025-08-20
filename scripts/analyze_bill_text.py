#!/usr/bin/env python3
"""
Analyze bill text files to understand structure and extract clean text.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import re
from typing import Dict, List, Optional
import json


def extract_clean_text_from_xml(xml_file: Path) -> Dict[str, str]:
    """
    Extract clean text from bill XML file.

    Returns:
        dict: {
            "title": "Bill title",
            "official_title": "Official title",
            "sections": "All section text combined",
            "raw_text": "All text without formatting"
        }
    """
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Extract metadata
        title = ""
        official_title = ""

        # Get title from metadata
        for dc_title in root.findall(
            ".//dc:title", namespaces={"dc": "http://purl.org/dc/elements/1.1/"}
        ):
            title = dc_title.text or ""
            break

        # Get official title
        for official in root.findall(".//official-title"):
            official_title = "".join(official.itertext()).strip()
            break

        # Extract all text from legis-body
        sections_text = []
        raw_text = []

        for element in root.iter():
            if element.text and element.text.strip():
                raw_text.append(element.text.strip())

            # Extract section text specifically
            if element.tag in ["section", "subsection", "paragraph", "subparagraph"]:
                section_text = "".join(element.itertext()).strip()
                if section_text:
                    sections_text.append(section_text)

        return {
            "title": title,
            "official_title": official_title,
            "sections": "\n\n".join(sections_text),
            "raw_text": " ".join(raw_text),
        }

    except Exception as e:
        print(f"Error processing {xml_file}: {e}")
        return {}


def analyze_bill_versions():
    """Analyze all HR1 versions to understand differences."""

    files_dir = Path("sample_data/files_from_links")
    hr1_files = list(files_dir.glob("BILLS-119hr1*.xml"))

    print(f"Found {len(hr1_files)} HR1 versions:")
    for f in hr1_files:
        print(f"  - {f.name}")

    print("\n" + "=" * 80)

    # Analyze each version
    versions_data = {}

    for xml_file in hr1_files:
        print(f"\n📄 Analyzing: {xml_file.name}")
        print("-" * 60)

        # Get file info
        file_size = xml_file.stat().st_size
        line_count = sum(1 for _ in xml_file.open())

        print(f"File size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
        print(f"Line count: {line_count:,}")

        # Extract text
        text_data = extract_clean_text_from_xml(xml_file)

        if text_data:
            print(f"Title: {text_data.get('title', 'N/A')}")
            print(f"Official title: {text_data.get('official_title', 'N/A')[:100]}...")

            sections_text = text_data.get("sections", "")
            raw_text = text_data.get("raw_text", "")

            print(f"Sections text length: {len(sections_text):,} characters")
            print(f"Raw text length: {len(raw_text):,} characters")

            # Count sections
            section_count = len(
                [line for line in sections_text.split("\n") if line.strip()]
            )
            print(f"Section count: {section_count}")

            versions_data[xml_file.name] = {
                "file_size": file_size,
                "line_count": line_count,
                "title": text_data.get("title", ""),
                "official_title": text_data.get("official_title", ""),
                "sections_length": len(sections_text),
                "raw_length": len(raw_text),
                "section_count": section_count,
            }

            # Save extracted text
            output_dir = Path("sample_data/extracted_text")
            output_dir.mkdir(exist_ok=True)

            text_file = output_dir / f"{xml_file.stem}_extracted.txt"
            with open(text_file, "w", encoding="utf-8") as f:
                f.write(f"Title: {text_data.get('title', '')}\n")
                f.write(f"Official Title: {text_data.get('official_title', '')}\n")
                f.write("\n" + "=" * 80 + "\n\n")
                f.write(text_data.get("sections", ""))

            print(f"Saved extracted text to: {text_file}")

    # Compare versions
    print("\n" + "=" * 80)
    print("📊 VERSION COMPARISON")
    print("=" * 80)

    if versions_data:
        # Sort by file size to see progression
        sorted_versions = sorted(versions_data.items(), key=lambda x: x[1]["file_size"])

        print(
            f"{'Version':<20} {'Size (MB)':<10} {'Lines':<8} {'Sections':<10} {'Title'}"
        )
        print("-" * 80)

        for version, data in sorted_versions:
            size_mb = data["file_size"] / 1024 / 1024
            print(
                f"{version:<20} {size_mb:<10.1f} {data['line_count']:<8,} {data['section_count']:<10} {data['title'][:30]}..."
            )

    # Save comparison data
    comparison_file = Path("sample_data/version_comparison.json")
    with open(comparison_file, "w") as f:
        json.dump(versions_data, f, indent=2)

    print(f"\nSaved comparison data to: {comparison_file}")


if __name__ == "__main__":
    analyze_bill_versions()
