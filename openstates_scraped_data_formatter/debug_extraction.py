#!/usr/bin/env python3
"""
Debug script to check what's happening with text extraction
"""
import json
from pathlib import Path


def debug_metadata_file(metadata_path):
    """Debug a single metadata file"""
    try:
        with open(metadata_path, "r") as f:
            data = json.load(f)

        bill_id = data.get("identifier", "unknown")
        versions = data.get("versions", [])

        print(f"Bill: {bill_id}")
        print(f"  Versions: {len(versions)}")

        for i, version in enumerate(versions):
            url = version.get("url", "")
            note = version.get("note", "")
            print(f"    Version {i+1}: {note}")
            print(f"      URL: {url}")

        return len(versions) > 0

    except Exception as e:
        print(f"Error reading {metadata_path}: {e}")
        return False


def main():
    processed_folder = Path("data_output/data_processed")

    if not processed_folder.exists():
        print(f"❌ Processed folder not found: {processed_folder}")
        return

    print(f"📁 Looking in: {processed_folder.absolute()}")

    # Find all metadata files
    metadata_files = list(processed_folder.rglob("metadata.json"))
    print(f"📊 Found {len(metadata_files)} metadata files")

    # Check first few files
    bills_with_versions = 0
    total_versions = 0

    for i, metadata_file in enumerate(metadata_files[:10]):  # Check first 10
        print(f"\n--- File {i+1}: {metadata_file} ---")
        has_versions = debug_metadata_file(metadata_file)
        if has_versions:
            bills_with_versions += 1

    # Check if any files have versions
    print(f"\n🔍 Checking for bills with versions...")
    for metadata_file in metadata_files:
        try:
            with open(metadata_file, "r") as f:
                data = json.load(f)
            versions = data.get("versions", [])
            if versions:
                bills_with_versions += 1
                total_versions += len(versions)
        except:
            pass

    print(f"\n📊 Summary:")
    print(f"  Total bills: {len(metadata_files)}")
    print(f"  Bills with versions: {bills_with_versions}")
    print(f"  Total versions: {total_versions}")

    # Check if any text files were created
    print(f"\n🔍 Looking for extracted text files...")
    text_files = list(processed_folder.rglob("*_extracted.txt"))
    xml_files = list(processed_folder.rglob("*.xml"))

    print(f"  Text files found: {len(text_files)}")
    print(f"  XML files found: {len(xml_files)}")

    if text_files:
        print(f"  Sample text files:")
        for f in text_files[:5]:
            print(f"    {f}")


if __name__ == "__main__":
    main()
