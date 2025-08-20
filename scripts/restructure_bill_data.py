#!/usr/bin/env python3
"""
Demonstrate restructuring bill data from logs/ to metadata.json.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional


def find_entire_bill_file(bill_folder: Path) -> Optional[Path]:
    """Find the entire_bill.json file in the logs folder."""
    logs_folder = bill_folder / "logs"
    if not logs_folder.exists():
        return None

    for file in logs_folder.glob("*_entire_bill.json"):
        return file

    return None


def restructure_bill_data(bill_folder: Path) -> bool:
    """
    Restructure bill data by moving entire_bill.json to metadata.json.

    Args:
        bill_folder: Path to the bill folder (e.g., .../bills/HR1/)

    Returns:
        bool: True if restructured successfully, False otherwise
    """
    print(f"📁 Processing: {bill_folder}")

    # Find the entire_bill.json file
    entire_bill_file = find_entire_bill_file(bill_folder)
    if not entire_bill_file:
        print(f"  ❌ No entire_bill.json found in {bill_folder}/logs/")
        return False

    # Check if metadata.json already exists
    metadata_file = bill_folder / "metadata.json"
    if metadata_file.exists():
        print(f"  ⚠️ metadata.json already exists, skipping")
        return False

    # Load the entire bill data
    try:
        with open(entire_bill_file, "r", encoding="utf-8") as f:
            bill_data = json.load(f)
    except Exception as e:
        print(f"  ❌ Error loading {entire_bill_file}: {e}")
        return False

    # Save as metadata.json
    try:
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(bill_data, f, indent=2)
        print(f"  ✅ Created metadata.json ({len(bill_data)} fields)")

        # Show what's in the metadata
        print(f"  📋 Metadata includes:")
        print(f"     - identifier: {bill_data.get('identifier', 'N/A')}")
        print(f"     - title: {bill_data.get('title', 'N/A')}")
        print(
            f"     - legislative_session: {bill_data.get('legislative_session', 'N/A')}"
        )
        print(f"     - actions: {len(bill_data.get('actions', []))} actions")
        print(f"     - versions: {len(bill_data.get('versions', []))} versions")
        print(f"     - sponsorships: {len(bill_data.get('sponsorships', []))} sponsors")

        return True

    except Exception as e:
        print(f"  ❌ Error saving metadata.json: {e}")
        return False


def demonstrate_restructure():
    """Demonstrate the restructuring with sample data."""

    print("🔄 BILL DATA RESTRUCTURING DEMONSTRATION")
    print("=" * 60)

    # Create a sample structure to demonstrate
    sample_dir = Path("sample_data/restructure_demo")
    sample_dir.mkdir(exist_ok=True)

    # Create sample bill folder structure
    bill_folder = (
        sample_dir / "country:us" / "congress" / "sessions" / "119" / "bills" / "HR1"
    )
    bill_folder.mkdir(parents=True, exist_ok=True)

    # Create logs folder
    logs_folder = bill_folder / "logs"
    logs_folder.mkdir(exist_ok=True)

    # Copy sample bill data to logs
    sample_bill_file = Path(
        "sample_data/bill_83db0600-6cd2-11f0-a587-065053629bd5.json"
    )
    if sample_bill_file.exists():
        with open(sample_bill_file, "r", encoding="utf-8") as f:
            bill_data = json.load(f)

        # Save as entire_bill.json in logs
        entire_bill_file = logs_folder / "20250520T040000Z_entire_bill.json"
        with open(entire_bill_file, "w", encoding="utf-8") as f:
            json.dump(bill_data, f, indent=2)

        print(f"📄 Created sample structure:")
        print(f"  {entire_bill_file}")

        # Demonstrate restructuring
        print(f"\n🔄 Restructuring...")
        success = restructure_bill_data(bill_folder)

        if success:
            print(f"\n✅ Restructuring complete!")
            print(f"📁 New structure:")
            print(f"  {bill_folder}/")
            print(f"  ├── metadata.json  ← Bill data moved here")
            print(f"  └── logs/")
            print(
                f"      └── 20250520T040000Z_entire_bill.json  ← Original (can be removed)"
            )

            # Show the new metadata file
            metadata_file = bill_folder / "metadata.json"
            if metadata_file.exists():
                print(f"\n📋 New metadata.json contains:")
                with open(metadata_file, "r", encoding="utf-8") as f:
                    metadata = json.load(f)

                print(f"  - identifier: {metadata.get('identifier')}")
                print(f"  - title: {metadata.get('title')}")
                print(f"  - session: {metadata.get('legislative_session')}")
                print(f"  - actions: {len(metadata.get('actions', []))}")
                print(f"  - versions: {len(metadata.get('versions', []))}")

                # Show version URLs for text extraction
                versions = metadata.get("versions", [])
                if versions:
                    print(f"\n🔗 Version URLs for text extraction:")
                    for i, version in enumerate(versions[:3]):  # Show first 3
                        note = version.get("note", "Unknown")
                        links = version.get("links", [])
                        xml_url = next(
                            (
                                link["url"]
                                for link in links
                                if link.get("media_type") == "text/xml"
                            ),
                            None,
                        )
                        if xml_url:
                            print(f"  {i+1}. {note}: {xml_url}")

    else:
        print(f"❌ Sample bill file not found: {sample_bill_file}")


def show_implementation_plan():
    """Show how to implement this in the main codebase."""

    print("\n" + "=" * 60)
    print("🔧 IMPLEMENTATION PLAN")
    print("=" * 60)

    print(
        """
1. MODIFY handle_bill() FUNCTION:
   - Change from saving to logs/entire_bill.json
   - Save to metadata.json instead
   - Keep action logs in logs/ folder

2. UPDATE FILE STRUCTURE:
   Current:
     bills/HR1/
     ├── logs/
     │   ├── 20250520T040000Z_entire_bill.json
     │   └── action_logs.json
     └── files/

   New:
     bills/HR1/
     ├── metadata.json
     ├── logs/
     │   └── action_logs.json
     └── files/

3. BENEFITS:
   ✅ Cleaner separation of concerns
   ✅ Easier access to bill metadata
   ✅ Better organization for text extraction
   ✅ Simpler processing logic

4. MIGRATION:
   - Process existing data to new structure
   - Update any code that reads entire_bill.json
   - Update documentation
"""
    )


if __name__ == "__main__":
    demonstrate_restructure()
    show_implementation_plan()
