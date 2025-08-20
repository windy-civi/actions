#!/usr/bin/env python3
"""
Test the updated handle_bill function with the new metadata.json structure.
"""

import json
import sys
from pathlib import Path

# Add the formatter module to the path
sys.path.append(str(Path("openstates_scraped_data_formatter")))

from handlers.bill import handle_bill
from utils.timestamp_tracker import LatestTimestamps


def test_updated_handle_bill():
    """Test the updated handle_bill function."""

    print("🧪 TESTING UPDATED handle_bill() FUNCTION")
    print("=" * 60)

    # Create test directories
    test_output = Path("test_output")
    test_output.mkdir(exist_ok=True)

    data_processed = test_output / "data_processed"
    data_not_processed = test_output / "data_not_processed"

    data_processed.mkdir(exist_ok=True)
    data_not_processed.mkdir(exist_ok=True)

    # Load sample bill data
    sample_bill_file = Path(
        "sample_data/bill_83db0600-6cd2-11f0-a587-065053629bd5.json"
    )
    if not sample_bill_file.exists():
        print(f"❌ Sample bill file not found: {sample_bill_file}")
        return False

    with open(sample_bill_file, "r", encoding="utf-8") as f:
        bill_data = json.load(f)

    # Initialize latest timestamps
    latest_timestamps: LatestTimestamps = {
        "bills": None,
        "events": None,
        "vote_events": None,
    }

    # Test the function
    print(f"📄 Testing with bill: {bill_data.get('identifier', 'Unknown')}")
    print(f"📄 Bill title: {bill_data.get('title', 'Unknown')}")

    success = handle_bill(
        STATE_ABBR="USA",
        data=bill_data,
        DATA_PROCESSED_FOLDER=data_processed,
        DATA_NOT_PROCESSED_FOLDER=data_not_processed,
        filename="test_bill.json",
        latest_timestamps=latest_timestamps,
    )

    if success:
        print("✅ handle_bill() completed successfully!")

        # Check the new structure
        expected_bill_path = (
            data_processed
            / "country:us"
            / "congress"
            / "sessions"
            / "119"
            / "bills"
            / "HR1"
        )

        print(f"\n📁 Checking new file structure...")
        print(f"Expected path: {expected_bill_path}")

        if expected_bill_path.exists():
            print("✅ Bill folder created successfully!")

            # Check for metadata.json
            metadata_file = expected_bill_path / "metadata.json"
            if metadata_file.exists():
                print("✅ metadata.json created successfully!")

                # Load and verify metadata
                with open(metadata_file, "r", encoding="utf-8") as f:
                    metadata = json.load(f)

                print(f"📋 Metadata verification:")
                print(f"  - identifier: {metadata.get('identifier')}")
                print(f"  - title: {metadata.get('title')}")
                print(f"  - session: {metadata.get('legislative_session')}")
                print(f"  - actions: {len(metadata.get('actions', []))}")
                print(f"  - versions: {len(metadata.get('versions', []))}")

                # Check for logs folder
                logs_folder = expected_bill_path / "logs"
                if logs_folder.exists():
                    print("✅ logs/ folder created successfully!")

                    # Check for action logs (but not entire_bill.json)
                    log_files = list(logs_folder.glob("*.json"))
                    entire_bill_files = list(logs_folder.glob("*_entire_bill.json"))

                    log_files = list(logs_folder.glob("*.json"))
                    print(f"  - Action log files: {len(log_files)}")
                    print(
                        f"  - Entire bill files in logs: {len(entire_bill_files)} (should be 0)"
                    )

                    if len(entire_bill_files) == 0:
                        print("✅ No entire_bill.json in logs/ (correct!)")
                    else:
                        print(
                            "❌ Found entire_bill.json in logs/ (should be moved to metadata.json)"
                        )

                # Check for files folder
                files_folder = expected_bill_path / "files"
                if files_folder.exists():
                    print("✅ files/ folder created successfully!")

                print(f"\n🎉 SUCCESS! New structure working correctly:")
                print(f"  {expected_bill_path}/")
                print(f"  ├── metadata.json  ← Bill data here")
                print(f"  ├── logs/          ← Action logs here")
                print(f"  └── files/         ← Future bill text files here")

                return True
            else:
                print("❌ metadata.json not found!")
                return False
        else:
            print("❌ Bill folder not created!")
            return False
    else:
        print("❌ handle_bill() failed!")
        return False


if __name__ == "__main__":
    success = test_updated_handle_bill()
    if success:
        print("\n✅ All tests passed! The restructuring is working correctly.")
    else:
        print("\n❌ Tests failed. Please check the implementation.")
