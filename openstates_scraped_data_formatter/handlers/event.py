from pathlib import Path
import json
import re
from typing import Any
from utils.file_utils import record_error_file, format_timestamp
from utils.timestamp_tracker import (
    update_latest_timestamp,
    latest_timestamps,
    to_dt_obj,
)

EVENT_LATEST_TIMESTAMP = latest_timestamps["events"]
print(f"💬 (Event handler) Current latest timestamp: {EVENT_LATEST_TIMESTAMP}")


def clean_event_name(name: str) -> str:
    return re.sub(r"[^\w]+", "_", name.lower()).strip("_")[:40]


def handle_event(
    STATE_ABBR: str,
    data: dict[str, any],
    session_name: str,
    date_folder: str,
    DATA_PROCESSED_FOLDER: Path,
    DATA_NOT_PROCESSED_FOLDER: Path,
    filename: str,
    referenced_bill_id: str | None,
) -> bool:
    """
    Saves event JSON to the correct session folder under events,
    using a consistent timestamped format to match bill action logs.
    """
    global EVENT_LATEST_TIMESTAMP
    event_id = data.get("_id") or filename.replace(".json", "")
    start_date = data.get("start_date")
    if not start_date:
        print(f"⚠️ Event {event_id} missing start_date")
        record_error_file(
            DATA_NOT_PROCESSED_FOLDER,
            "from_handle_event_missing_start_date",
            filename,
            data,
            original_filename=filename,
        )
        return False

    if not referenced_bill_id:
        referenced_bill_id = data.get("bill_identifier")
        if not referenced_bill_id:
            print("⚠️ Warning: Event missing bill_identifier")
            record_error_file(
                DATA_NOT_PROCESSED_FOLDER,
                "from_handle_event_missing_bill_identifier",
                filename,
                data,
                original_filename=filename,
            )
            return False

    timestamp = format_timestamp(start_date)
    if timestamp == "unknown":
        print(f"⚠️ Event {event_id} has unrecognized timestamp format: {timestamp}")
    if timestamp and timestamp != "unknown":
        current_dt = to_dt_obj(timestamp)
        EVENT_LATEST_TIMESTAMP = update_latest_timestamp(
            "events", current_dt, EVENT_LATEST_TIMESTAMP
        )

    event_name = data.get("name", "event")
    short_name = clean_event_name(event_name)

    base_path = Path(DATA_PROCESSED_FOLDER).joinpath(
        f"country:us",
        f"state:{STATE_ABBR}",
        "sessions",
        "ocd-session",
        f"country:us",
        f"state:{STATE_ABBR}",
        date_folder,
        session_name,
        "events",
    )
    base_path.mkdir(parents=True, exist_ok=True)

    output_file = base_path / f"{timestamp}_{short_name}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return True
