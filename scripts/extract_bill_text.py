#!/usr/bin/env python3
"""
Extract bill text from URLs found in metadata.json files.
Uses the new metadata.json structure for easier access.
"""

import json
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import time
import re


def extract_clean_text_from_xml(xml_content: str) -> Dict[str, str]:
    """
    Extract clean text from bill XML content.

    Returns:
        dict: {
            "title": "Bill title",
            "official_title": "Official title",
            "sections": "All section text combined",
            "raw_text": "All text without formatting"
        }
    """
    try:
        root = ET.fromstring(xml_content)

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
        print(f"Error processing XML: {e}")
        return {}


def download_bill_text(url: str, timeout: int = 30) -> Optional[str]:
    """
    Download bill text from URL.

    Args:
        url: URL to download from
        timeout: Request timeout in seconds

    Returns:
        str: Downloaded content or None if failed
    """
    try:
        print(f"  📥 Downloading: {url}")
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()

        # Check if it's XML content
        content_type = response.headers.get("content-type", "")
        if "xml" in content_type:
            return response.text
        else:
            print(f"  ⚠️ Unexpected content type: {content_type}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"  ❌ Download failed: {e}")
        return None
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return None


def get_version_urls_from_metadata(metadata_file: Path) -> List[Tuple[str, str]]:
    """
    Extract version URLs from metadata.json file.

    Args:
        metadata_file: Path to metadata.json

    Returns:
        List of (version_note, xml_url) tuples
    """
    try:
        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        versions = metadata.get("versions", [])
        urls = []

        for version in versions:
            note = version.get("note", "Unknown")
            links = version.get("links", [])

            # Find XML URL
            xml_url = None
            for link in links:
                if link.get("media_type") == "text/xml":
                    xml_url = link.get("url")
                    break

            if xml_url:
                urls.append((note, xml_url))

        return urls

    except Exception as e:
        print(f"❌ Error reading metadata: {e}")
        return []


def process_bill_folder(bill_folder: Path, download_delay: float = 1.0) -> bool:
    """
    Process a single bill folder to extract text from all versions.

    Args:
        bill_folder: Path to bill folder (e.g., .../bills/HR1/)
        download_delay: Delay between downloads to be respectful

    Returns:
        bool: True if successful, False otherwise
    """
    print(f"📁 Processing: {bill_folder.name}")

    # Check for metadata.json
    metadata_file = bill_folder / "metadata.json"
    if not metadata_file.exists():
        print(f"  ❌ No metadata.json found")
        return False

    # Get version URLs
    version_urls = get_version_urls_from_metadata(metadata_file)
    if not version_urls:
        print(f"  ⚠️ No version URLs found")
        return False

    print(f"  📋 Found {len(version_urls)} versions:")
    for note, url in version_urls:
        print(f"    - {note}")

    # Create files directory if it doesn't exist
    files_dir = bill_folder / "files"
    files_dir.mkdir(exist_ok=True)

    # Process each version
    success_count = 0
    for note, url in version_urls:
        print(f"\n  🔄 Processing: {note}")

        # Download XML content
        xml_content = download_bill_text(url)
        if not xml_content:
            continue

        # Extract clean text
        text_data = extract_clean_text_from_xml(xml_content)
        if not text_data:
            print(f"    ❌ Failed to extract text from XML")
            continue

        # Create safe filename
        safe_note = re.sub(r"[^\w\s-]", "", note).strip().replace(" ", "_").lower()
        if not safe_note:
            safe_note = "unknown_version"

        # Save XML file
        xml_file = files_dir / f"bill_text_{safe_note}.xml"
        try:
            with open(xml_file, "w", encoding="utf-8") as f:
                f.write(xml_content)
            print(f"    ✅ Saved XML: {xml_file.name}")
        except Exception as e:
            print(f"    ❌ Failed to save XML: {e}")
            continue

        # Save extracted text
        text_file = files_dir / f"bill_text_{safe_note}.txt"
        try:
            with open(text_file, "w", encoding="utf-8") as f:
                f.write(f"Title: {text_data.get('title', '')}\n")
                f.write(f"Official Title: {text_data.get('official_title', '')}\n")
                f.write(f"Version: {note}\n")
                f.write(f"Source URL: {url}\n")
                f.write("\n" + "=" * 80 + "\n\n")
                f.write(text_data.get("sections", ""))

            print(f"    ✅ Saved text: {text_file.name}")
            print(
                f"    📊 Text stats: {len(text_data.get('sections', '')):,} characters"
            )
            success_count += 1

        except Exception as e:
            print(f"    ❌ Failed to save text: {e}")
            continue

        # Be respectful with delays
        if download_delay > 0:
            time.sleep(download_delay)

    print(
        f"  📊 Summary: {success_count}/{len(version_urls)} versions processed successfully"
    )
    return success_count > 0


def find_and_process_bills(
    data_processed_folder: Path, max_bills: Optional[int] = None
) -> None:
    """
    Find all bill folders and process them for text extraction.

    Args:
        data_processed_folder: Path to data_processed folder
        max_bills: Maximum number of bills to process (for testing)
    """
    print("🔍 SEARCHING FOR BILL FOLDERS")
    print("=" * 60)

    # Find all bill folders
    bill_folders = list(data_processed_folder.glob("**/bills/*"))

    if not bill_folders:
        print("❌ No bill folders found!")
        return

    print(f"📁 Found {len(bill_folders)} bill folders")

    # Limit for testing if specified
    if max_bills:
        bill_folders = bill_folders[:max_bills]
        print(f"🔬 Testing mode: Processing first {len(bill_folders)} bills")

    # Process each bill
    successful_bills = 0
    total_bills = len(bill_folders)

    print(f"\n🔄 PROCESSING BILLS")
    print("=" * 60)

    for i, bill_folder in enumerate(bill_folders, 1):
        print(f"\n[{i}/{total_bills}] ", end="")

        if process_bill_folder(bill_folder):
            successful_bills += 1

        print("-" * 40)

    print(f"\n✅ PROCESSING COMPLETE")
    print("=" * 60)
    print(f"📊 Results:")
    print(f"  - Total bills processed: {total_bills}")
    print(f"  - Successful bills: {successful_bills}")
    print(f"  - Success rate: {(successful_bills/total_bills)*100:.1f}%")


def main():
    """Main function to run bill text extraction."""

    # Check if we have sample data to test with
    sample_metadata = Path(
        "sample_data/restructure_demo/country:us/congress/sessions/119/bills/HR1/metadata.json"
    )

    if sample_metadata.exists():
        print("🧪 TESTING WITH SAMPLE DATA")
        print("=" * 60)

        bill_folder = sample_metadata.parent
        process_bill_folder(bill_folder)

        # Show results
        files_dir = bill_folder / "files"
        if files_dir.exists():
            print(f"\n📁 Generated files:")
            for file in files_dir.glob("*"):
                size = file.stat().st_size
                print(f"  - {file.name} ({size:,} bytes)")

    else:
        print("❌ No sample data found. Please run the restructure demo first.")
        print("Run: python scripts/restructure_bill_data.py")


if __name__ == "__main__":
    main()
