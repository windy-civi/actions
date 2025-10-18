from pathlib import Path
import json
import re
from typing import Any
from utils.file_utils import format_timestamp, validate_required_field
from utils.timestamp_tracker import (
    update_latest_timestamp,
    to_dt_obj,
    LatestTimestamps,
)
from utils.path_utils import build_data_path


def clean_event_name(name: str) -> str:
    return re.sub(r"[^\w]+", "_", name.lower()).strip("_")[:40]


def handle_event(
    STATE_ABBR: str,
    data: dict[str, any],
    DATA_PROCESSED_FOLDER: Path,
    DATA_NOT_PROCESSED_FOLDER: Path,
    filename: str,
    latest_timestamps: LatestTimestamps,
) -> bool:
    """
    Saves event JSON to the correct session folder under events,
    using a consistent timestamped format to match bill action logs.
    """
    event_id = data.get("_id") or filename.replace(".json", "")
    
    start_date = validate_required_field(
        data,
        "start_date",
        filename,
        DATA_NOT_PROCESSED_FOLDER,
        "from_handle_event_missing_start_date",
        f"Event {event_id} missing start_date",
    )
    if not start_date:
        return False

    referenced_bill_id = validate_required_field(
        data,
        "bill_identifier",
        filename,
        DATA_NOT_PROCESSED_FOLDER,
        "from_handle_event_missing_bill_identifier",
        "Event missing bill_identifier",
    )
    if not referenced_bill_id:
        return False

    timestamp = format_timestamp(start_date)
    if timestamp == "unknown":
        print(f"⚠️ Event {event_id} has unrecognized timestamp format: {start_date}")
    else:
        current_dt = to_dt_obj(timestamp)
        latest_timestamps["events"] = update_latest_timestamp(
            "events", current_dt, latest_timestamps["events"], latest_timestamps
        )

    event_name = data.get("name", "event")
    short_name = clean_event_name(event_name)
    session_id = data.get("legislative_session", "unknown-session")

    # Use centralized path builder for events folder (not individual event)
    base_path = build_data_path(
        DATA_PROCESSED_FOLDER, STATE_ABBR, "events", session_id, ""
    ).parent  # Go up one level since build_data_path adds identifier

    base_path.mkdir(parents=True, exist_ok=True)

    output_file = base_path / f"{timestamp}_{short_name}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return True
