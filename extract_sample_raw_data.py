#!/usr/bin/env python3
"""
Extract raw scraped bills matching the sample dataset.

Usage:
    python extract_sample_raw_data.py <raw_data_folder> <output_folder>
"""

import json
import sys
from pathlib import Path
from shutil import copy2


def get_sample_bill_identifiers(sample_processed_folder: Path) -> set:
    """Get list of bill identifiers from the sample processed dataset."""
    bills_folder = (
        sample_processed_folder
        / "data_output/data_processed/country:us/congress/sessions/119/bills"
    )

    if not bills_folder.exists():
        print(f"❌ Sample bills folder not found: {bills_folder}")
        return set()

    bill_ids = set()
    for bill_dir in bills_folder.iterdir():
        if bill_dir.is_dir() and not bill_dir.name.endswith("copy"):
            # Add with space (e.g., "HR 1") and without (e.g., "HR1")
            bill_name = bill_dir.name
            # Try to split at first digit
            import re

            match = re.match(r"([A-Z]+)(\d+)", bill_name)
            if match:
                prefix, number = match.groups()
                bill_ids.add(f"{prefix} {number}")  # With space
                bill_ids.add(f"{prefix}{number}")  # Without space
            else:
                bill_ids.add(bill_name)

    print(f"📊 Found {len(bill_ids)} bill variations in sample dataset")
    return bill_ids


def extract_matching_bills(
    raw_data_folder: Path, output_folder: Path, target_bills: set
):
    """Extract bill files that match the target bill identifiers."""
    output_folder.mkdir(parents=True, exist_ok=True)

    matched = 0
    skipped = 0
    errors = 0

    print(f"\n🔍 Scanning raw data in: {raw_data_folder}")

    for json_file in raw_data_folder.glob("bill_*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            identifier = data.get("identifier", "")

            if identifier in target_bills:
                # Copy the file
                dest_file = output_folder / json_file.name
                copy2(json_file, dest_file)
                matched += 1
                print(f"✅ Matched: {identifier} → {json_file.name}")
            else:
                skipped += 1

        except json.JSONDecodeError:
            errors += 1
            print(f"⚠️  Error reading: {json_file.name}")
        except Exception as e:
            errors += 1
            print(f"⚠️  Error processing {json_file.name}: {e}")

    print(f"\n📈 Results:")
    print(f"   ✅ Matched: {matched}")
    print(f"   ⏭️  Skipped: {skipped}")
    print(f"   ⚠️  Errors: {errors}")

    return matched


def main():
    if len(sys.argv) < 3:
        print(
            "Usage: python extract_sample_raw_data.py <raw_data_folder> <output_folder>"
        )
        print("\nExample:")
        print("  python extract_sample_raw_data.py /path/to/raw/bills test_input_large")
        sys.exit(1)

    raw_data_folder = Path(sys.argv[1])
    output_folder = Path(sys.argv[2])

    if not raw_data_folder.exists():
        print(f"❌ Raw data folder not found: {raw_data_folder}")
        sys.exit(1)

    # Get target bills from sample
    sample_folder = Path(__file__).parent / "sample_data/usa-data-pipeline-SAMPLE copy"
    target_bills = get_sample_bill_identifiers(sample_folder)

    if not target_bills:
        print("❌ No sample bills found!")
        sys.exit(1)

    # Extract matching bills
    matched_count = extract_matching_bills(raw_data_folder, output_folder, target_bills)

    print(f"\n✅ Done! Extracted {matched_count} bills to: {output_folder}")


if __name__ == "__main__":
    main()
