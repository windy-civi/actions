import requests
import xml.etree.ElementTree as ET
import re
import time
import random
from pathlib import Path
from typing import List, Dict, Optional
import json
import urllib3
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from datetime import datetime

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create multiple sessions for rotation
sessions = []
for i in range(3):
    session = requests.Session()

    # Configure retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )

    # Mount adapter with retry strategy
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    sessions.append(session)

# Current session index for rotation
current_session_index = 0

# Global error tracking
failed_bills_tracker = {
    "failed_downloads": [],
    "failed_parsing": [],
    "failed_saves": [],
    "total_failed": 0,
}


def get_realistic_headers() -> dict:
    """Get realistic browser headers to avoid blocking."""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    ]

    return {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
        "Referer": "https://www.congress.gov/",
        "DNT": "1",
        "Sec-GPC": "1",
    }


def get_congress_gov_headers() -> dict:
    """Get specialized headers for congress.gov to avoid blocking."""
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Referer": "https://www.congress.gov/",
        "Origin": "https://www.congress.gov",
    }


def rotate_session():
    """Rotate to the next session for load balancing."""
    global current_session_index
    current_session_index = (current_session_index + 1) % len(sessions)
    return sessions[current_session_index]


def record_failed_bill(
    bill_id: str,
    error_type: str,
    error_message: str,
    url: str = "",
    metadata_file: str = "",
    additional_info: Dict = None,
    output_folder: Path = None,
):
    """Record a failed bill for error tracking and reporting."""
    global failed_bills_tracker

    error_record = {
        "bill_id": bill_id,
        "error_type": error_type,
        "error_message": error_message,
        "url": url,
        "metadata_file": metadata_file,
        "timestamp": datetime.now().isoformat(),
        "additional_info": additional_info or {},
    }

    # Add to global tracker
    if error_type == "download":
        failed_bills_tracker["failed_downloads"].append(error_record)
    elif error_type == "parsing":
        failed_bills_tracker["failed_parsing"].append(error_record)
    elif error_type == "save":
        failed_bills_tracker["failed_saves"].append(error_record)

    failed_bills_tracker["total_failed"] += 1

    # Save individual error file to data_not_processed if output folder provided
    if output_folder:
        save_individual_error_file(error_record, output_folder)


def save_individual_error_file(error_record: Dict, output_folder: Path):
    """Save an individual failed bill error file to data_not_processed following the existing pattern."""
    try:
        # Create data_not_processed folder structure
        data_not_processed = output_folder / "data_not_processed"
        error_category = f"{error_record['error_type']}_failures"
        error_folder = data_not_processed / "text_extraction_errors" / error_category
        error_folder.mkdir(parents=True, exist_ok=True)

        # Create filename following the existing pattern
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        bill_id_clean = error_record["bill_id"].replace(" ", "").replace("/", "_")
        filename = f"bill_{bill_id_clean}_{timestamp}.json"

        # Save the error record
        with open(error_folder / filename, "w", encoding="utf-8") as f:
            json.dump(error_record, f, indent=2, ensure_ascii=False)

        print(f"   📋 Saved error file: {error_folder / filename}")

    except Exception as e:
        print(f"   ❌ Error saving individual error file: {e}")


def save_failed_bills_report(output_folder: Path, state: str):
    """Save a comprehensive report of failed bills to the calling repo's data_not_processed folder."""
    global failed_bills_tracker

    if failed_bills_tracker["total_failed"] == 0:
        print("✅ No failed bills to report")
        return

    # Create data_not_processed folder structure
    data_not_processed = output_folder / "data_not_processed"
    text_extraction_errors = data_not_processed / "text_extraction_errors"
    summary_reports = text_extraction_errors / "summary_reports"
    summary_reports.mkdir(parents=True, exist_ok=True)

    # Generate timestamp for the report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save detailed error report
    report_file = summary_reports / f"failed_text_extraction_{state}_{timestamp}.json"

    report_data = {
        "state": state,
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_failed": failed_bills_tracker["total_failed"],
            "failed_downloads": len(failed_bills_tracker["failed_downloads"]),
            "failed_parsing": len(failed_bills_tracker["failed_parsing"]),
            "failed_saves": len(failed_bills_tracker["failed_saves"]),
        },
        "failed_downloads": failed_bills_tracker["failed_downloads"],
        "failed_parsing": failed_bills_tracker["failed_parsing"],
        "failed_saves": failed_bills_tracker["failed_saves"],
    }

    try:
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        print(f"📋 Failed bills report saved: {report_file}")
        print(f"   Total failed: {failed_bills_tracker['total_failed']}")
        print(f"   Download failures: {len(failed_bills_tracker['failed_downloads'])}")
        print(f"   Parsing failures: {len(failed_bills_tracker['failed_parsing'])}")
        print(f"   Save failures: {len(failed_bills_tracker['failed_saves'])}")

    except Exception as e:
        print(f"❌ Error saving failed bills report: {e}")

    # Also save a simple summary file for quick reference
    summary_file = summary_reports / f"failed_summary_{state}_{timestamp}.txt"
    try:
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(f"Text Extraction Failure Report - {state}\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            f.write(f"Total Failed Bills: {failed_bills_tracker['total_failed']}\n")
            f.write(
                f"Download Failures: {len(failed_bills_tracker['failed_downloads'])}\n"
            )
            f.write(
                f"Parsing Failures: {len(failed_bills_tracker['failed_parsing'])}\n"
            )
            f.write(f"Save Failures: {len(failed_bills_tracker['failed_saves'])}\n\n")

            if failed_bills_tracker["failed_downloads"]:
                f.write("DOWNLOAD FAILURES:\n")
                for error in failed_bills_tracker["failed_downloads"]:
                    f.write(f"  - {error['bill_id']}: {error['error_message']}\n")
                    if error["url"]:
                        f.write(f"    URL: {error['url']}\n")
                f.write("\n")

            if failed_bills_tracker["failed_parsing"]:
                f.write("PARSING FAILURES:\n")
                for error in failed_bills_tracker["failed_parsing"]:
                    f.write(f"  - {error['bill_id']}: {error['error_message']}\n")
                f.write("\n")

            if failed_bills_tracker["failed_saves"]:
                f.write("SAVE FAILURES:\n")
                for error in failed_bills_tracker["failed_saves"]:
                    f.write(f"  - {error['bill_id']}: {error['error_message']}\n")
                f.write("\n")

        print(f"📋 Summary report saved: {summary_file}")

    except Exception as e:
        print(f"❌ Error saving summary report: {e}")


def reset_error_tracking():
    """Reset the global error tracking for a new run."""
    global failed_bills_tracker
    failed_bills_tracker = {
        "failed_downloads": [],
        "failed_parsing": [],
        "failed_saves": [],
        "total_failed": 0,
    }


def download_with_retry(
    url: str, max_retries: int = 5, delay: float = 1.0
) -> Optional[requests.Response]:
    """Download with advanced retry logic and anti-blocking techniques."""
    is_congress_gov = "congress.gov" in url

    for attempt in range(max_retries):
        try:
            # Rotate session for load balancing
            session = rotate_session()

            # Add random delay to avoid rate limiting
            base_delay = delay + random.uniform(1.0, 3.0)
            if is_congress_gov:
                base_delay += random.uniform(2.0, 5.0)  # Extra delay for congress.gov
            time.sleep(base_delay)

            # Get specialized headers based on domain
            if is_congress_gov:
                headers = get_congress_gov_headers()
            else:
                headers = get_realistic_headers()

            # Make the request with additional options
            response = session.get(
                url,
                headers=headers,
                timeout=45,
                verify=False,  # Disable SSL verification for some sites
                allow_redirects=True,
            )

            # If we get a 403, try multiple fallback strategies
            if response.status_code == 403:
                print(
                    f"   ⚠️ Got 403 on attempt {attempt + 1}, trying fallback strategies..."
                )

                # Strategy 1: Try Googlebot user agent
                headers["User-Agent"] = (
                    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
                )
                response = session.get(url, headers=headers, timeout=45, verify=False)

                if response.status_code == 403:
                    # Strategy 2: Try different browser
                    headers["User-Agent"] = (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0"
                    )
                    headers["Accept"] = (
                        "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
                    )
                    response = session.get(
                        url, headers=headers, timeout=45, verify=False
                    )

                if response.status_code == 403:
                    # Strategy 3: Try mobile user agent
                    headers["User-Agent"] = (
                        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
                    )
                    response = session.get(
                        url, headers=headers, timeout=45, verify=False
                    )

                if response.status_code == 403:
                    # Strategy 4: Try with minimal headers
                    minimal_headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    }
                    response = session.get(
                        url, headers=minimal_headers, timeout=45, verify=False
                    )

            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as e:
            print(f"   ⚠️ Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                # Exponential backoff with jitter
                wait_time = delay * (2**attempt) + random.uniform(2, 8)
                if is_congress_gov:
                    wait_time += random.uniform(3, 10)  # Extra wait for congress.gov
                print(f"   ⏳ Waiting {wait_time:.1f}s before retry...")
                time.sleep(wait_time)
            else:
                print(f"   ❌ All {max_retries} attempts failed for {url}")
                return None

    return None


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
        response = download_with_retry(url, max_retries=3, delay=delay)
        if not response:
            return None

        content_type = response.headers.get("content-type", "").lower()
        content = response.text

        # More flexible content type checking
        if (
            "xml" in content_type
            or content.strip().startswith("<?xml")
            or "<bill>" in content[:1000]
        ):
            return content
        else:
            print(f"⚠️ Unexpected content type: {content_type} for {url}")
            print(f"   Content preview: {content[:200]}...")
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


def create_safe_filename(
    url: str, version_note: str = "", file_extension: str = "xml"
) -> str:
    """
    Create a safe filename from URL and version note.

    Args:
        url: The URL to extract filename from
        version_note: Version note to include in filename
        file_extension: File extension to use (xml, html, pdf, etc.)

    Returns:
        Safe filename
    """
    # Extract filename from URL
    filename = url.split("/")[-1]
    if not filename or "." not in filename:
        filename = f"bill_content.{file_extension}"

    # Clean up version note for filename
    safe_version = re.sub(r"[^\w\s-]", "", version_note).strip()
    safe_version = re.sub(r"[-\s]+", "_", safe_version)

    if safe_version:
        name, ext = filename.rsplit(".", 1)
        filename = f"{name}_{safe_version}.{ext}"

    return filename


def extract_bill_text_from_metadata(
    metadata_file: Path, files_dir: Path, output_folder: Path = None
) -> bool:
    """
    Extract bill text for a single bill from its metadata.json file.

    Args:
        metadata_file: Path to metadata.json file
        files_dir: Path to files/ directory for this bill
        output_folder: Path to calling repo root for error reporting (optional)

    Returns:
        True if successful, False otherwise
    """
    try:
        # Load metadata
        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        # Extract bill ID for error tracking
        bill_id = metadata.get("identifier", "unknown")
        if not bill_id or bill_id == "unknown":
            # Try to extract from file path as fallback
            bill_id = metadata_file.parent.name

        # Define media type preference order (best to worst)
        MEDIA_TYPE_PREFERENCE = [
            "text/xml",  # Best: Structured XML data
            "text/html",  # Good: HTML content
            "application/pdf",  # Acceptable: PDF files
            "text/plain",  # Basic: Plain text
        ]

        # Process versions first (primary bill text), then documents (supporting materials)
        arrays_to_process = []

        # Add versions array first (prioritized - contains actual bill text)
        versions = metadata.get("versions", [])
        if versions:
            arrays_to_process.append(("versions", versions))

        # Add documents array second (supporting documentation)
        documents = metadata.get("documents", [])
        if documents:
            arrays_to_process.append(("documents", documents))

        if not arrays_to_process:
            # This is normal - not all bills have full text available
            return True  # Don't count as error

        success_count = 0

        for array_name, items in arrays_to_process:
            priority = "🟢 PRIMARY" if array_name == "versions" else "🟡 SUPPORTING"
            print(f"   📋 Processing {array_name} array... ({priority})")

            for item in items:
                item_note = item.get("note", "")
                links = item.get("links", [])

                if not links:
                    continue  # Skip items without links

                # Find best available link based on preference order
                best_link = None
                best_media_type = None

                for link in links:
                    media_type = link.get("media_type", "")
                    url = link.get("url")

                    if not url:
                        continue

                    # Check if this media type is better than current best
                    for preferred_type in MEDIA_TYPE_PREFERENCE:
                        if preferred_type in media_type.lower():
                            if best_link is None or MEDIA_TYPE_PREFERENCE.index(
                                preferred_type
                            ) < MEDIA_TYPE_PREFERENCE.index(best_media_type):
                                best_link = link
                                best_media_type = preferred_type
                            break

                if not best_link:
                    continue  # Skip if no suitable link found

                url = best_link.get("url")
                media_type = best_link.get("media_type", "")

                print(f"   📥 Downloading: {url} (type: {media_type})")

                # Download content based on media type
                content = None
                strikethrough_info = None

                if "xml" in media_type.lower():
                    content = download_bill_text(url)
                elif "html" in media_type.lower():
                    content = download_html_content(url)
                elif "pdf" in media_type.lower():
                    # Try enhanced strikethrough detection first
                    strikethrough_result = extract_text_with_strikethroughs(url)
                    if strikethrough_result and strikethrough_result.get("raw_text"):
                        content = strikethrough_result["raw_text"]
                        strikethrough_info = {
                            "has_strikethroughs": strikethrough_result.get(
                                "has_strikethroughs", False
                            ),
                            "strikethrough_count": strikethrough_result.get(
                                "strikethrough_count", 0
                            ),
                        }
                        if strikethrough_info["has_strikethroughs"]:
                            print(
                                f"   🔍 Detected {strikethrough_info['strikethrough_count']} strikethrough sections"
                            )
                    else:
                        # Fallback to regular PDF extraction
                        content = download_pdf_content(url)
                else:
                    print(f"   ⚠️ Unsupported media type: {media_type}")
                    continue

                if not content:
                    print(f"   ❌ Failed to download: {url}")
                    record_failed_bill(
                        bill_id=bill_id,
                        error_type="download",
                        error_message=f"Failed to download content from {media_type}",
                        url=url,
                        metadata_file=str(metadata_file),
                        additional_info={
                            "media_type": media_type,
                            "item_note": item_note,
                        },
                        output_folder=output_folder,
                    )
                    continue

                print(f"   📄 Downloaded {len(content)} characters")

                # Extract text based on content type
                extracted_data = None
                if "xml" in media_type.lower():
                    extracted_data = extract_text_from_xml(content)
                elif "html" in media_type.lower():
                    extracted_data = extract_text_from_html(content)
                elif "pdf" in media_type.lower():
                    extracted_data = extract_text_from_pdf(content)
                else:
                    extracted_data = {
                        "raw_text": content,
                        "title": "",
                        "official_title": "",
                        "sections": [],
                    }

                if "error" in extracted_data:
                    print(f"   ❌ Failed to parse content: {extracted_data['error']}")
                    record_failed_bill(
                        bill_id=bill_id,
                        error_type="parsing",
                        error_message=extracted_data["error"],
                        url=url,
                        metadata_file=str(metadata_file),
                        additional_info={
                            "media_type": media_type,
                            "item_note": item_note,
                        },
                        output_folder=output_folder,
                    )
                    continue

                # Create filenames
                file_extension = (
                    "xml"
                    if "xml" in media_type.lower()
                    else "html" if "html" in media_type.lower() else "pdf"
                )
                filename = create_safe_filename(url, item_note, file_extension)
                text_filename = filename.replace(f".{file_extension}", "_extracted.txt")

                # Create appropriate directory structure
                if array_name == "documents":
                    # Put documents in a separate subfolder
                    target_dir = files_dir / "documents"
                    target_dir.mkdir(parents=True, exist_ok=True)
                    print(f"   📁 Created documents directory: {target_dir}")
                else:
                    # Put versions in the main files directory
                    target_dir = files_dir
                    target_dir.mkdir(parents=True, exist_ok=True)
                    print(f"   📁 Created directory: {target_dir}")

                # Save original content
                content_file = target_dir / filename
                print(f"   💾 Saving {file_extension.upper()} to: {content_file}")
                try:
                    with open(content_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"   ✅ {file_extension.upper()} saved successfully")
                except Exception as e:
                    print(f"   ❌ Error saving {file_extension.upper()}: {e}")
                    continue

                # Save extracted text
                text_file = target_dir / text_filename
                print(f"   💾 Saving text to: {text_file}")
                try:
                    with open(text_file, "w", encoding="utf-8") as f:
                        f.write(f"Title: {extracted_data.get('title', 'N/A')}\n")
                        f.write(
                            f"Official Title: {extracted_data.get('official_title', 'N/A')}\n"
                        )
                        f.write(
                            f"Number of Sections: {len(extracted_data.get('sections', []))}\n"
                        )
                        f.write(f"Source: {array_name} - {item_note}\n")
                        f.write(f"Media Type: {media_type}\n")
                        if strikethrough_info and strikethrough_info.get(
                            "has_strikethroughs"
                        ):
                            f.write(
                                f"Strikethrough Detection: {strikethrough_info['strikethrough_count']} sections found\n"
                            )
                        f.write("\n" + "=" * 80 + "\n\n")

                        for i, section in enumerate(
                            extracted_data.get("sections", []), 1
                        ):
                            f.write(f"Section {i}:\n{section}\n\n")

                        f.write("\n" + "=" * 80 + "\n\n")
                        f.write("Raw Text:\n")
                        f.write(extracted_data.get("raw_text", ""))
                    print(f"   ✅ Text saved successfully")
                except Exception as e:
                    print(f"   ❌ Error saving text: {e}")
                    record_failed_bill(
                        bill_id=bill_id,
                        error_type="save",
                        error_message=f"Failed to save extracted text: {e}",
                        url=url,
                        metadata_file=str(metadata_file),
                        additional_info={
                            "media_type": media_type,
                            "item_note": item_note,
                            "text_filename": text_filename,
                        },
                        output_folder=output_folder,
                    )
                    continue

                success_count += 1
                print(f"   ✅ Extracted text for {array_name}: {item_note}")

        return success_count > 0

    except Exception as e:
        print(f"   ❌ Error processing {metadata_file}: {e}")
        return False


def debug_pdf_structure(url: str) -> dict:
    """
    Debug function to analyze PDF structure and identify potential strikethrough text.

    This function provides detailed information about the PDF's character layout,
    fonts, colors, and other properties that might indicate strikethrough text.
    """
    try:
        response = download_with_retry(url, max_retries=3, delay=1.0)
        if not response:
            return {"error": "Failed to download PDF"}

        import pdfplumber
        import io

        pdf_file = io.BytesIO(response.content)
        with pdfplumber.open(pdf_file) as pdf:
            debug_info = {
                "pages": len(pdf.pages),
                "fonts": set(),
                "colors": set(),
                "character_count": 0,
                "potential_strikethroughs": [],
            }

            for page_num, page in enumerate(pdf.pages):
                chars = page.chars
                debug_info["character_count"] += len(chars)

                for char in chars:
                    # Collect font information
                    font_name = char.get("fontname", "")
                    debug_info["fonts"].add(font_name)

                    # Collect color information
                    if "non_stroking_color" in char:
                        color = char["non_stroking_color"]
                        debug_info["colors"].add(str(color))

                    # Check for potential strikethrough indicators
                    if is_likely_strikethrough(char, chars, chars.index(char)):
                        debug_info["potential_strikethroughs"].append(
                            {
                                "page": page_num + 1,
                                "text": char["text"],
                                "font": char.get("fontname", ""),
                                "color": char.get("non_stroking_color", ""),
                                "position": (char["x0"], char["top"]),
                            }
                        )

            return debug_info

    except Exception as e:
        return {"error": str(e)}


def process_bills_in_batch(
    processed_folder: Path,
    batch_size: int = 100,
    output_folder: Path = None,
    state: str = "unknown",
) -> Dict[str, int]:
    """
    Process bills in batches for text extraction.

    Args:
        processed_folder: Path to the processed data folder
        batch_size: Number of bills to process in each batch
        output_folder: Path to save error reports (optional)
        state: State identifier for error reports (optional)

    Returns:
        Dictionary with processing statistics
    """
    # Reset error tracking for this run
    reset_error_tracking()

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
                files_dir.mkdir(parents=True, exist_ok=True)

                # Extract text for this bill
                success = extract_bill_text_from_metadata(
                    metadata_file, files_dir, output_folder
                )

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

    # Save error report if output folder is provided
    if output_folder:
        save_failed_bills_report(output_folder, state)

    return {
        "total_bills": total_bills,
        "processed": processed_count,
        "successful": success_count,
        "errors": error_count,
    }


def download_congress_gov_content(url: str) -> str:
    """Download content from congress.gov with specialized anti-blocking techniques."""
    try:
        # For amendment URLs, try the /text endpoint first
        if "/amendment/" in url and not url.endswith("/text"):
            text_url = url + "/text"
            print(f"   🔄 Trying /text endpoint: {text_url}")

            # Try the /text endpoint first
            response = download_with_retry(text_url, max_retries=5, delay=2.0)
            if response:
                return response.text

            print(f"   ⚠️ /text endpoint failed, trying original URL: {url}")

        # Try the enhanced retry function on original URL
        response = download_with_retry(url, max_retries=5, delay=2.0)
        if response:
            return response.text

        # If that fails, try a different approach with session warming
        print(f"   🔄 Trying session warming approach for {url}")

        # Warm up the session by visiting the main page first
        session = rotate_session()
        warmup_headers = get_congress_gov_headers()

        try:
            # Visit main page to establish session
            session.get(
                "https://www.congress.gov/",
                headers=warmup_headers,
                timeout=30,
                verify=False,
            )
            time.sleep(random.uniform(2, 4))

            # For amendment URLs, try /text endpoint first
            target_url = url
            if "/amendment/" in url and not url.endswith("/text"):
                target_url = url + "/text"
                print(f"   🔄 Session warming: trying /text endpoint: {target_url}")

            # Now try the target URL
            response = session.get(
                target_url, headers=warmup_headers, timeout=45, verify=False
            )
            if response.status_code == 200:
                return response.text

            # If /text failed, try original URL
            if target_url != url:
                print(f"   🔄 Session warming: trying original URL: {url}")
                response = session.get(
                    url, headers=warmup_headers, timeout=45, verify=False
                )
                if response.status_code == 200:
                    return response.text
        except:
            pass

        # Final fallback: try with curl-like headers
        print(f"   🔄 Trying curl-like approach for {url}")
        curl_headers = {
            "User-Agent": "curl/7.68.0",
            "Accept": "*/*",
            "Connection": "keep-alive",
        }

        session = rotate_session()

        # For amendment URLs, try /text endpoint first
        target_url = url
        if "/amendment/" in url and not url.endswith("/text"):
            target_url = url + "/text"
            print(f"   🔄 Curl fallback: trying /text endpoint: {target_url}")

        response = session.get(
            target_url, headers=curl_headers, timeout=45, verify=False
        )
        if response.status_code == 200:
            return response.text

        # If /text failed, try original URL
        if target_url != url:
            print(f"   🔄 Curl fallback: trying original URL: {url}")
            response = session.get(url, headers=curl_headers, timeout=45, verify=False)
            if response.status_code == 200:
                return response.text

        return None

    except Exception as e:
        print(f"   ❌ Failed to download congress.gov content: {e}")
        return None


def download_html_content(url: str) -> str:
    """Download HTML content from URL with proper headers to avoid blocking."""
    try:
        # Use specialized function for congress.gov
        if "congress.gov" in url:
            return download_congress_gov_content(url)

        # Use standard retry for other sites
        response = download_with_retry(url, max_retries=3, delay=1.0)
        if not response:
            return None
        return response.text
    except Exception as e:
        print(f"   ❌ Failed to download HTML: {e}")
        return None


def download_pdf_content(url: str) -> str:
    """Download PDF content from URL and convert to text."""
    try:
        response = download_with_retry(url, max_retries=3, delay=1.0)
        if not response:
            return None

        # Try multiple PDF parsing libraries in order of preference
        pdf_content = None

        # Try pdfplumber first (best for complex layouts)
        try:
            import pdfplumber
            import io

            pdf_file = io.BytesIO(response.content)
            with pdfplumber.open(pdf_file) as pdf:
                text_parts = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                pdf_content = "\n\n".join(text_parts)
                if pdf_content:
                    print(f"   ✅ Successfully extracted PDF text using pdfplumber")
                    return pdf_content
        except ImportError:
            pass
        except Exception as e:
            print(f"   ⚠️ pdfplumber failed: {e}")

        # Try PyPDF2 as fallback
        try:
            import PyPDF2
            import io

            pdf_file = io.BytesIO(response.content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text_parts = []
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            pdf_content = "\n\n".join(text_parts)
            if pdf_content:
                print(f"   ✅ Successfully extracted PDF text using PyPDF2")
                return pdf_content
        except ImportError:
            pass
        except Exception as e:
            print(f"   ⚠️ PyPDF2 failed: {e}")

        # Try pymupdf (fitz) as another fallback
        try:
            import fitz  # PyMuPDF
            import io

            pdf_file = io.BytesIO(response.content)
            doc = fitz.open(stream=pdf_file, filetype="pdf")
            text_parts = []
            for page in doc:
                page_text = page.get_text()
                if page_text:
                    text_parts.append(page_text)
            doc.close()
            pdf_content = "\n\n".join(text_parts)
            if pdf_content:
                print(f"   ✅ Successfully extracted PDF text using PyMuPDF")
                return pdf_content
        except ImportError:
            pass
        except Exception as e:
            print(f"   ⚠️ PyMuPDF failed: {e}")

        # If all libraries fail, return a placeholder
        print(f"   ⚠️ No PDF parsing libraries available")
        return f"[PDF content from {url} - requires PDF parsing library (pdfplumber, PyPDF2, or PyMuPDF)]"

    except Exception as e:
        print(f"   ❌ Failed to download PDF: {e}")
        return None


def extract_text_from_html(html_content: str) -> dict:
    """Extract text from HTML content."""
    try:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html_content, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text
        text = soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = " ".join(chunk for chunk in chunks if chunk)

        return {
            "title": soup.title.string if soup.title else "",
            "official_title": "",
            "sections": [text],
            "raw_text": text,
        }
    except ImportError:
        return {"error": "BeautifulSoup not available for HTML parsing"}
    except Exception as e:
        return {"error": f"Failed to parse HTML: {e}"}


def extract_text_from_pdf(pdf_content: str) -> dict:
    """Extract text from PDF content."""
    # The pdf_content is already extracted text from the PDF
    # Clean up the text and structure it
    lines = pdf_content.split("\n")
    cleaned_lines = [line.strip() for line in lines if line.strip()]

    # Try to identify title and sections
    title = ""
    sections = []
    current_section = []

    for line in cleaned_lines:
        # Look for title patterns (usually at the top, all caps, or contains "AN ACT")
        if not title and (
            "AN ACT" in line.upper() or "BILL" in line.upper() or len(line) > 50
        ):
            title = line
        # Look for section headers (numbers, "SECTION", etc.)
        elif re.match(r"^(Section|§|\d+\.)", line, re.IGNORECASE):
            if current_section:
                sections.append("\n".join(current_section))
                current_section = []
            current_section.append(line)
        else:
            current_section.append(line)

    # Add the last section
    if current_section:
        sections.append("\n".join(current_section))

    # If no sections found, treat the whole content as one section
    if not sections:
        sections = [pdf_content]

    return {
        "title": title or "PDF Document",
        "official_title": title or "",
        "sections": sections,
        "raw_text": pdf_content,
    }


def extract_text_with_strikethroughs(url: str) -> dict:
    """
    Extract PDF text including strikethrough content using visual analysis.

    This function attempts to detect strikethrough text by analyzing
    the visual layout and character positioning in the PDF.
    """
    try:
        response = download_with_retry(url, max_retries=3, delay=1.0)
        if not response:
            return None

        # Try pdfplumber with enhanced strikethrough detection
        try:
            import pdfplumber
            import io

            pdf_file = io.BytesIO(response.content)
            with pdfplumber.open(pdf_file) as pdf:
                text_parts = []
                strikethrough_parts = []

                for page in pdf.pages:
                    # Extract regular text
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)

                    # Try to detect strikethrough text using character analysis
                    chars = page.chars
                    if chars:
                        strikethrough_text = detect_strikethrough_chars(chars)
                        if strikethrough_text:
                            strikethrough_parts.append(
                                f"[DELETED: {strikethrough_text}]"
                            )

                # Combine regular and strikethrough text
                full_text = "\n\n".join(text_parts)
                if strikethrough_parts:
                    full_text += "\n\n" + "\n".join(strikethrough_parts)

                if full_text:
                    print(
                        f"   ✅ Successfully extracted PDF text with strikethrough detection using pdfplumber"
                    )
                    return {
                        "raw_text": full_text,
                        "has_strikethroughs": len(strikethrough_parts) > 0,
                        "strikethrough_count": len(strikethrough_parts),
                    }

        except ImportError:
            pass
        except Exception as e:
            print(f"   ⚠️ pdfplumber strikethrough detection failed: {e}")

        # Fallback to regular extraction
        return None

    except Exception as e:
        print(f"   ❌ Failed to download PDF for strikethrough analysis: {e}")
        return None


def detect_strikethrough_chars(chars: list) -> str:
    """
    Detect strikethrough text by analyzing character positioning and formatting.

    Args:
        chars: List of character objects from pdfplumber

    Returns:
        String containing detected strikethrough text
    """
    strikethrough_text = []

    # Group characters by line
    lines = {}
    for char in chars:
        y_pos = round(char["top"], 2)  # Round to handle floating point precision
        if y_pos not in lines:
            lines[y_pos] = []
        lines[y_pos].append(char)

    # Analyze each line for strikethrough patterns
    for y_pos, line_chars in lines.items():
        # Sort characters by x position
        line_chars.sort(key=lambda x: x["x0"])

        # Look for patterns that might indicate strikethrough
        for i, char in enumerate(line_chars):
            # Check if character has strikethrough-like properties
            if is_likely_strikethrough(char, line_chars, i):
                strikethrough_text.append(char["text"])

    return "".join(strikethrough_text)


def is_likely_strikethrough(char: dict, line_chars: list, index: int) -> bool:
    """
    Determine if a character is likely part of strikethrough text.

    This is a heuristic approach that looks for visual indicators
    of strikethrough text in PDF character data.
    """
    # Check for strikethrough font properties
    font_name = char.get("fontname", "").lower()
    if any(
        strike_indicator in font_name
        for strike_indicator in ["strike", "delete", "removed"]
    ):
        return True

    # Check for unusual character spacing or positioning
    if index > 0 and index < len(line_chars) - 1:
        prev_char = line_chars[index - 1]
        next_char = line_chars[index + 1]

        # Look for gaps in text that might indicate strikethrough
        gap_before = char["x0"] - prev_char["x1"]
        gap_after = next_char["x0"] - char["x1"]

        if gap_before > 2 or gap_after > 2:  # Unusual spacing
            return True

    # Check for color differences (strikethrough text might be grayed out)
    if "non_stroking_color" in char:
        color = char["non_stroking_color"]
        if isinstance(color, list) and len(color) >= 3:
            # Check if text is grayed out (common for strikethrough)
            r, g, b = color[:3]
            if r == g == b and r < 0.8:  # Gray text
                return True

    return False


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
