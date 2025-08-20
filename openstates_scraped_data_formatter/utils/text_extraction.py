import requests
import xml.etree.ElementTree as ET
import re
import time
from pathlib import Path
from typing import List, Dict, Optional
import json


def download_bill_text(url: str, delay: float = 1.0) -> Optional[str]:
    """
    Download bill text from a URL.

    Args:
        url: URL to download from
        delay: Delay between requests to be respectful

    Returns:
        XML content as string, or None if failed
    """
    try:
        time.sleep(delay)  # Be respectful to the server
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        content_type = response.headers.get("content-type", "").lower()
        if "xml" in content_type:
            return response.text
        else:
            print(f"⚠️ Unexpected content type: {content_type}")
            return None

    except Exception as e:
        print(f"❌ Error downloading {url}: {e}")
        return None


def extract_text_from_xml(xml_content: str) -> Dict[str, str]:
    """
    Extract clean text from XML bill content.

    Args:
        xml_content: XML content as string

    Returns:
        Dictionary with extracted text components
    """
    try:
        root = ET.fromstring(xml_content)

        # Extract title
        title = ""
        title_elem = root.find(".//title")
        if title_elem is not None:
            title = title_elem.text or ""

        # Extract official title
        official_title = ""
        official_title_elem = root.find(".//official-title")
        if official_title_elem is not None:
            official_title = official_title_elem.text or ""

        # Extract sections
        sections = []
        for section in root.findall(".//section"):
            section_text = ET.tostring(section, encoding="unicode", method="text")
            if section_text.strip():
                sections.append(section_text.strip())

        # Extract raw text (all text content)
        raw_text = ET.tostring(root, encoding="unicode", method="text")

        return {
            "title": title.strip(),
            "official_title": official_title.strip(),
            "sections": sections,
            "raw_text": raw_text.strip(),
        }

    except Exception as e:
        print(f"❌ Error parsing XML: {e}")
        return {"error": f"Failed to parse XML: {e}"}


def create_safe_filename(url: str, version_note: str = "") -> str:
    """
    Create a safe filename from URL and version note.

    Args:
        url: The URL to extract filename from
        version_note: Version note to include in filename

    Returns:
        Safe filename
    """
    # Extract filename from URL
    filename = url.split("/")[-1]
    if not filename.endswith(".xml"):
        filename += ".xml"

    # Clean up version note for filename
    safe_version = re.sub(r"[^\w\s-]", "", version_note).strip()
    safe_version = re.sub(r"[-\s]+", "_", safe_version)

    if safe_version:
        name, ext = filename.rsplit(".", 1)
        filename = f"{name}_{safe_version}.{ext}"

    return filename


def extract_bill_text_from_metadata(metadata_file: Path, files_dir: Path) -> bool:
    """
    Extract bill text for a single bill from its metadata.json file.

    Args:
        metadata_file: Path to metadata.json file
        files_dir: Path to files/ directory for this bill

    Returns:
        True if successful, False otherwise
    """
    try:
        # Load metadata
        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        # Get versions array
        versions = metadata.get("versions", [])
        if not versions:
            print(f"⚠️ No versions found in {metadata_file}")
            return False

        success_count = 0
        for version in versions:
            url = version.get("url")
            version_note = version.get("note", "")

            if not url:
                continue

            # Download XML content
            xml_content = download_bill_text(url)
            if not xml_content:
                continue

            # Extract text
            extracted_data = extract_text_from_xml(xml_content)
            if "error" in extracted_data:
                continue

            # Create filenames
            xml_filename = create_safe_filename(url, version_note)
            text_filename = xml_filename.replace(".xml", "_extracted.txt")

            # Save XML content
            xml_file = files_dir / xml_filename
            with open(xml_file, "w", encoding="utf-8") as f:
                f.write(xml_content)

            # Save extracted text
            text_file = files_dir / text_filename
            with open(text_file, "w", encoding="utf-8") as f:
                f.write(f"Title: {extracted_data['title']}\n")
                f.write(f"Official Title: {extracted_data['official_title']}\n")
                f.write(f"Number of Sections: {len(extracted_data['sections'])}\n")
                f.write("\n" + "=" * 80 + "\n\n")

                for i, section in enumerate(extracted_data["sections"], 1):
                    f.write(f"Section {i}:\n{section}\n\n")

                f.write("\n" + "=" * 80 + "\n\n")
                f.write("Raw Text:\n")
                f.write(extracted_data["raw_text"])

            success_count += 1
            print(f"✅ Extracted text for version: {version_note or 'default'}")

        return success_count > 0

    except Exception as e:
        print(f"❌ Error processing {metadata_file}: {e}")
        return False


def process_bills_in_batch(
    processed_folder: Path, batch_size: int = 100
) -> Dict[str, int]:
    """
    Process bills in batches for text extraction.

    Args:
        processed_folder: Path to the processed data folder
        batch_size: Number of bills to process in each batch

    Returns:
        Dictionary with processing statistics
    """
    # Find all metadata.json files
    metadata_files = list(processed_folder.rglob("metadata.json"))

    total_bills = len(metadata_files)
    processed_count = 0
    success_count = 0
    error_count = 0

    print(f"📊 Found {total_bills} bills to process for text extraction")

    # Process in batches
    for i in range(0, total_bills, batch_size):
        batch = metadata_files[i : i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total_bills + batch_size - 1) // batch_size

        print(f"\n🔄 Processing batch {batch_num}/{total_batches} ({len(batch)} bills)")

        for metadata_file in batch:
            try:
                # Get the files directory for this bill
                files_dir = metadata_file.parent / "files"
                files_dir.mkdir(exist_ok=True)

                # Extract text for this bill
                success = extract_bill_text_from_metadata(metadata_file, files_dir)

                if success:
                    success_count += 1
                else:
                    error_count += 1

                processed_count += 1

                # Progress indicator
                if processed_count % 10 == 0:
                    print(f"   Processed {processed_count}/{total_bills} bills...")

            except Exception as e:
                print(f"❌ Error processing {metadata_file}: {e}")
                error_count += 1
                processed_count += 1

        print(
            f"✅ Batch {batch_num} complete. Success: {success_count}, Errors: {error_count}"
        )

    return {
        "total_bills": total_bills,
        "processed": processed_count,
        "successful": success_count,
        "errors": error_count,
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python text_extraction.py <processed_folder_path>")
        sys.exit(1)

    processed_folder = Path(sys.argv[1])
    if not processed_folder.exists():
        print(f"❌ Folder does not exist: {processed_folder}")
        sys.exit(1)

    print("🚀 Starting bill text extraction...")
    stats = process_bills_in_batch(processed_folder)

    print(f"\n📊 Extraction Complete!")
    print(f"Total bills: {stats['total_bills']}")
    print(f"Processed: {stats['processed']}")
    print(f"Successful: {stats['successful']}")
    print(f"Errors: {stats['errors']}")
