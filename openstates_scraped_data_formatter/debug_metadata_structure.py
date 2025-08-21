#!/usr/bin/env python3
"""
Debug script to examine metadata file structure
"""
import json
from pathlib import Path


def main():
    processed_folder = Path("data_output/data_processed")

    if not processed_folder.exists():
        print(f"❌ Processed folder not found: {processed_folder}")
        return

    # Find first few metadata files
    metadata_files = list(processed_folder.rglob("metadata.json"))[:5]

    for i, metadata_file in enumerate(metadata_files):
        print(f"\n--- Metadata File {i+1}: {metadata_file} ---")

        try:
            with open(metadata_file, "r") as f:
                data = json.load(f)

            bill_id = data.get("identifier", "unknown")
            print(f"Bill ID: {bill_id}")

            # Check if versions exist
            versions = data.get("versions", [])
            print(f"Versions count: {len(versions)}")

            if versions:
                print("First version structure:")
                first_version = versions[0]
                print(f"  Keys: {list(first_version.keys())}")

                # Check for links vs url
                if "links" in first_version:
                    links = first_version["links"]
                    print(f"  Links count: {len(links)}")
                    if links:
                        print(f"  First link: {links[0]}")

                if "url" in first_version:
                    url = first_version["url"]
                    print(f"  Direct URL: {url}")

                # Check for note
                note = first_version.get("note", "")
                print(f"  Note: {note}")

            # Check if there are any URL-like fields anywhere
            print("Searching for URL patterns...")
            data_str = json.dumps(data, indent=2)
            if "govinfo.gov" in data_str:
                print("  ✅ Found govinfo.gov URLs in data")
            else:
                print("  ❌ No govinfo.gov URLs found")

        except Exception as e:
            print(f"Error reading {metadata_file}: {e}")


if __name__ == "__main__":
    main()
