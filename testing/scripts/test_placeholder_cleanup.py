#!/usr/bin/env python3
"""
Test script for placeholder cleanup functionality.

Creates a test scenario with:
1. Bill with metadata.json + placeholder.json (should delete placeholder)
2. Bill with only placeholder.json + votes (orphan - should keep and report)
3. Bill with only placeholder.json + events (orphan - should keep and report)
"""

import json
import sys
from pathlib import Path
from tempfile import mkdtemp
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scrape_and_format"))

from postprocessors.cleanup_placeholders import cleanup_placeholders


def create_test_scenario():
    """Create a test data structure with various placeholder scenarios."""
    test_dir = Path(mkdtemp(prefix="placeholder_test_"))
    data_processed = test_dir / "data_processed"

    # Country/state/session structure
    bills_folder = (
        data_processed / "country:us" / "congress" / "sessions" / "119" / "bills"
    )
    bills_folder.mkdir(parents=True, exist_ok=True)

    print(f"📁 Created test directory: {test_dir}")

    # Scenario 1: Bill with both metadata and placeholder (should delete placeholder)
    bill1_folder = bills_folder / "HR1"
    bill1_folder.mkdir(parents=True, exist_ok=True)

    # Real bill metadata
    with open(bill1_folder / "metadata.json", "w") as f:
        json.dump(
            {
                "identifier": "HR 1",
                "title": "Test Bill 1",
                "_processing": {"logs_latest_update": "2025-01-01T00:00:00Z"},
            },
            f,
            indent=2,
        )

    # Placeholder (should be deleted)
    with open(bill1_folder / "placeholder.json", "w") as f:
        json.dump({"identifier": "HR1", "placeholder": True}, f, indent=2)

    print("   ✓ Scenario 1: HR1 with metadata + placeholder")

    # Scenario 2: Orphan with votes (no metadata, should keep and report)
    bill2_folder = bills_folder / "HR999"
    bill2_folder.mkdir(parents=True, exist_ok=True)
    (bill2_folder / "logs").mkdir(parents=True, exist_ok=True)

    # Only placeholder
    with open(bill2_folder / "placeholder.json", "w") as f:
        json.dump({"identifier": "HR999", "placeholder": True}, f, indent=2)

    # Some vote events
    with open(
        bill2_folder / "logs" / "20250101T120000Z_vote_event_passed.json", "w"
    ) as f:
        json.dump({"vote": "data"}, f, indent=2)

    with open(
        bill2_folder / "logs" / "20250102T120000Z_vote_event_failed.json", "w"
    ) as f:
        json.dump({"vote": "data2"}, f, indent=2)

    print("   ✓ Scenario 2: HR999 with only placeholder + 2 votes (orphan)")

    # Scenario 3: Orphan with events (no metadata, should keep and report)
    bill3_folder = bills_folder / "S500"
    bill3_folder.mkdir(parents=True, exist_ok=True)
    (bill3_folder / "logs").mkdir(parents=True, exist_ok=True)

    # Only placeholder
    with open(bill3_folder / "placeholder.json", "w") as f:
        json.dump({"identifier": "S500", "placeholder": True}, f, indent=2)

    # Some events
    with open(bill3_folder / "logs" / "20250101T120000Z_event_hearing.json", "w") as f:
        json.dump({"event": "data"}, f, indent=2)

    print("   ✓ Scenario 3: S500 with only placeholder + 1 event (orphan)")

    # Scenario 4: Normal bill with metadata, no placeholder (control)
    bill4_folder = bills_folder / "HR2"
    bill4_folder.mkdir(parents=True, exist_ok=True)

    with open(bill4_folder / "metadata.json", "w") as f:
        json.dump(
            {
                "identifier": "HR 2",
                "title": "Test Bill 2",
                "_processing": {"logs_latest_update": "2025-01-01T00:00:00Z"},
            },
            f,
            indent=2,
        )

    print("   ✓ Scenario 4: HR2 with only metadata (control)")

    return data_processed


def verify_results(data_processed: Path):
    """Verify the cleanup worked correctly."""
    print("\n🔍 Verifying results:")

    bills_folder = (
        data_processed / "country:us" / "congress" / "sessions" / "119" / "bills"
    )

    # Check Scenario 1: HR1 - placeholder should be deleted
    hr1_folder = bills_folder / "HR1"
    hr1_metadata = hr1_folder / "metadata.json"
    hr1_placeholder = hr1_folder / "placeholder.json"

    assert hr1_metadata.exists(), "HR1 metadata should exist"
    assert not hr1_placeholder.exists(), "HR1 placeholder should be deleted"
    print("   ✓ HR1: Placeholder deleted (bill exists)")

    # Check Scenario 2: HR999 - placeholder should remain
    hr999_folder = bills_folder / "HR999"
    hr999_placeholder = hr999_folder / "placeholder.json"
    hr999_metadata = hr999_folder / "metadata.json"

    assert hr999_placeholder.exists(), "HR999 placeholder should remain (orphan)"
    assert not hr999_metadata.exists(), "HR999 should have no metadata"
    print("   ✓ HR999: Placeholder kept (orphan with votes)")

    # Check Scenario 3: S500 - placeholder should remain
    s500_folder = bills_folder / "S500"
    s500_placeholder = s500_folder / "placeholder.json"
    s500_metadata = s500_folder / "metadata.json"

    assert s500_placeholder.exists(), "S500 placeholder should remain (orphan)"
    assert not s500_metadata.exists(), "S500 should have no metadata"
    print("   ✓ S500: Placeholder kept (orphan with events)")

    # Check tracking file exists
    tracking_file = data_processed / "orphaned_placeholders_tracking.json"
    assert tracking_file.exists(), "Tracking file should be generated"

    with open(tracking_file) as f:
        tracking = json.load(f)

    assert len(tracking) == 2, "Should have 2 orphans in tracking"

    # Verify HR999 and S500 are tracked
    assert "HR999" in tracking, "HR999 should be in tracking"
    assert "S500" in tracking, "S500 should be in tracking"

    # Check counts
    assert tracking["HR999"]["vote_count"] == 2, "HR999 should have 2 votes"
    assert tracking["S500"]["event_count"] == 1, "S500 should have 1 event"
    assert tracking["HR999"]["occurrence_count"] == 1, "HR999 should have occurred once"
    assert tracking["S500"]["occurrence_count"] == 1, "S500 should have occurred once"

    print("   ✓ Tracking file correct (2 orphans: HR999, S500)")

    print("\n✅ All verifications passed!")


def test_persistent_tracking(data_processed: Path):
    """Test that orphan tracking persists across runs."""
    print("\n🔄 Testing persistent tracking (simulating multiple runs)...")

    # Note: First run already happened in main(), so tracking file exists
    # Check current state (after first run in main())
    tracking_file = data_processed / "orphaned_placeholders_tracking.json"
    with open(tracking_file) as f:
        tracking = json.load(f)

    initial_count_hr999 = tracking["HR999"]["occurrence_count"]
    initial_count_s500 = tracking["S500"]["occurrence_count"]

    print(f"   Initial state: HR999={initial_count_hr999}, S500={initial_count_s500}")

    # Run #2 (simulate running again - should increment counts)
    print("\n🔄 Run #2 (incrementing counts)...")
    stats2 = cleanup_placeholders(data_processed)

    assert stats2["new_orphans"] == 0, "No new orphans on second run"
    assert stats2["orphans_found"] == 2, "Still 2 orphans total"
    assert stats2["resolved_orphans"] == 0, "No resolved orphans yet"

    with open(tracking_file) as f:
        tracking = json.load(f)

    assert (
        tracking["HR999"]["occurrence_count"] == initial_count_hr999 + 1
    ), "HR999 count should increment"
    assert (
        tracking["S500"]["occurrence_count"] == initial_count_s500 + 1
    ), "S500 count should increment"

    print(
        f"   ✓ Run #2: Counts incremented (HR999={tracking['HR999']['occurrence_count']}, S500={tracking['S500']['occurrence_count']})"
    )

    # Run #3 - now add metadata for HR999 (resolve it)
    print("\n🔄 Run #3 (resolving HR999)...")
    bills_folder = (
        data_processed / "country:us" / "congress" / "sessions" / "119" / "bills"
    )
    hr999_folder = bills_folder / "HR999"

    with open(hr999_folder / "metadata.json", "w") as f:
        json.dump(
            {
                "identifier": "HR 999",
                "title": "Now exists!",
                "_processing": {"logs_latest_update": "2025-01-01T00:00:00Z"},
            },
            f,
            indent=2,
        )

    stats3 = cleanup_placeholders(data_processed)

    assert stats3["resolved_orphans"] == 1, "HR999 should be resolved"
    assert stats3["orphans_found"] == 1, "Only 1 orphan left (S500)"

    with open(tracking_file) as f:
        tracking = json.load(f)

    assert "HR999" not in tracking, "HR999 should be removed from tracking"
    assert "S500" in tracking, "S500 should still be tracked"
    expected_s500_count = initial_count_s500 + 2  # +1 from run #2, +1 from run #3
    assert (
        tracking["S500"]["occurrence_count"] == expected_s500_count
    ), f"S500 should have count {expected_s500_count}"

    print(f"   ✓ Run #3: HR999 resolved and removed from tracking")
    print(f"   ✓ S500 still tracked with count {tracking['S500']['occurrence_count']}")
    print("\n✅ Persistent tracking test passed!")


def main():
    """Run the placeholder cleanup test."""
    print("🧪 Testing placeholder cleanup functionality\n")

    # Create test scenario
    data_processed = create_test_scenario()

    # Run cleanup
    print("\n🧹 Running cleanup...")
    stats = cleanup_placeholders(data_processed)

    # Verify results
    verify_results(data_processed)

    # Print final stats
    print("\n📊 Cleanup stats:")
    print(f"   Placeholders found: {stats['placeholders_found']}")
    print(f"   Placeholders deleted: {stats['placeholders_deleted']}")
    print(f"   Orphans found: {stats['orphans_found']}")
    print(f"   New orphans: {stats['new_orphans']}")

    # Test persistent tracking
    test_persistent_tracking(data_processed)

    # Cleanup test directory
    test_dir = data_processed.parent
    print(f"\n🗑️  Cleaning up test directory: {test_dir}")
    shutil.rmtree(test_dir)

    print("\n🎉 All tests completed successfully!")


if __name__ == "__main__":
    main()
