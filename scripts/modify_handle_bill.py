#!/usr/bin/env python3
"""
Show the exact changes needed to modify handle_bill function for restructuring.
"""


def show_current_code():
    """Show the current handle_bill function code."""

    print("🔍 CURRENT handle_bill() FUNCTION")
    print("=" * 60)
    print(
        """
def handle_bill(
    STATE_ABBR: str,
    data: dict[str, Any],
    DATA_PROCESSED_FOLDER: Path,
    DATA_NOT_PROCESSED_FOLDER: Path,
    filename: str,
    latest_timestamps: LatestTimestamps,
) -> bool:
    # ... existing code ...

    # Save entire bill
    full_filename = f"{timestamp}_entire_bill.json"
    output_file = save_path.joinpath("logs", full_filename)  # ← CURRENT: saves to logs/
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # Save each action as a separate file
    if actions:
        write_action_logs(actions, bill_identifier, save_path / "logs")
"""
    )


def show_modified_code():
    """Show the modified handle_bill function code."""

    print("\n🔧 MODIFIED handle_bill() FUNCTION")
    print("=" * 60)
    print(
        """
def handle_bill(
    STATE_ABBR: str,
    data: dict[str, Any],
    DATA_PROCESSED_FOLDER: Path,
    DATA_NOT_PROCESSED_FOLDER: Path,
    filename: str,
    latest_timestamps: LatestTimestamps,
) -> bool:
    # ... existing code ...

    # Save bill metadata (moved from logs/)
    metadata_file = save_path / "metadata.json"  # ← NEW: saves to metadata.json
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # Save each action as a separate file (unchanged)
    if actions:
        write_action_logs(actions, bill_identifier, save_path / "logs")
"""
    )


def show_migration_script():
    """Show a migration script to update existing data."""

    print("\n🔄 MIGRATION SCRIPT")
    print("=" * 60)
    print(
        """
import json
from pathlib import Path

def migrate_existing_bills(data_processed_folder: Path):
    \"\"\"
    Migrate existing bill data from logs/entire_bill.json to metadata.json
    \"\"\"
    print("🔄 Migrating existing bill data...")

    # Find all bill folders
    bill_folders = list(data_processed_folder.glob("**/bills/*"))

    migrated_count = 0
    for bill_folder in bill_folders:
        if not bill_folder.is_dir():
            continue

        # Look for entire_bill.json in logs
        logs_folder = bill_folder / "logs"
        if not logs_folder.exists():
            continue

        entire_bill_files = list(logs_folder.glob("*_entire_bill.json"))
        if not entire_bill_files:
            continue

        # Use the first one found
        entire_bill_file = entire_bill_files[0]

        # Check if metadata.json already exists
        metadata_file = bill_folder / "metadata.json"
        if metadata_file.exists():
            print(f"  ⚠️ {bill_folder.name}: metadata.json already exists")
            continue

        # Load and migrate
        try:
            with open(entire_bill_file, 'r', encoding='utf-8') as f:
                bill_data = json.load(f)

            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(bill_data, f, indent=2)

            print(f"  ✅ {bill_folder.name}: migrated to metadata.json")
            migrated_count += 1

        except Exception as e:
            print(f"  ❌ {bill_folder.name}: error - {e}")

    print(f"\\n✅ Migration complete: {migrated_count} bills migrated")
"""
    )


def show_updated_file_structure():
    """Show the updated file structure."""

    print("\n📁 UPDATED FILE STRUCTURE")
    print("=" * 60)
    print(
        """
BEFORE (Current):
data_output/data_processed/country:us/congress/sessions/119/bills/HR1/
├── logs/
│   ├── 20250520T040000Z_entire_bill.json  ← Bill data here
│   ├── 20250520T040000Z.classification.referral-committee.lower.json
│   └── 20250520T040000Z_passage.json
└── files/
    └── (future bill text files)

AFTER (New):
data_output/data_processed/country:us/congress/sessions/119/bills/HR1/
├── metadata.json  ← Bill data moved here
├── logs/
│   ├── 20250520T040000Z.classification.referral-committee.lower.json
│   └── 20250520T040000Z_passage.json
└── files/
    ├── bill_text_enrolled.xml
    ├── bill_text_enrolled.txt
    ├── bill_text_engrossed.xml
    └── bill_text_engrossed.txt
"""
    )


def show_benefits():
    """Show the benefits of this restructuring."""

    print("\n✅ BENEFITS OF RESTRUCTURING")
    print("=" * 60)
    print(
        """
1. CLEANER ORGANIZATION:
   ✅ Bill metadata is separate from action logs
   ✅ Clear separation of concerns
   ✅ Easier to understand folder structure

2. SIMPLER TEXT EXTRACTION:
   ✅ Direct access to bill metadata: bill_folder/metadata.json
   ✅ No need to search through logs folder
   ✅ Easier to find version URLs for downloading

3. BETTER PROCESSING:
   ✅ Metadata.json is the single source of truth for bill data
   ✅ Action logs remain in logs/ for historical tracking
   ✅ Files/ folder ready for bill text storage

4. IMPROVED ACCESSIBILITY:
   ✅ One-click access to bill metadata
   ✅ Clearer API for downstream processing
   ✅ Better organization for AI analysis

5. FUTURE-PROOF:
   ✅ Ready for bill text storage in files/
   ✅ Scalable structure for multiple versions
   ✅ Maintains blockchain-style immutability
"""
    )


if __name__ == "__main__":
    show_current_code()
    show_modified_code()
    show_migration_script()
    show_updated_file_structure()
    show_benefits()
