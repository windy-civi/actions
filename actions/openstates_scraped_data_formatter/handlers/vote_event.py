import json
from pathlib import Path
from utils.file_utils import format_timestamp, record_error_file, write_vote_event_log
from utils.timestamp_tracker import (
    update_latest_timestamp,
    latest_timestamps,
    to_dt_obj,
)

VOTE_LATEST_TIMESTAMP = latest_timestamps["vote_events"]
print(f"💬 (Vote_event handler) Current latest timestamp: {VOTE_LATEST_TIMESTAMP}")


def handle_vote_event(
    STATE_ABBR: str,
    data: dict[str, any],
    session_name: str,
    date_folder: str,
    DATA_PROCESSED_FOLDER: Path,
    DATA_NOT_PROCESSED_FOLDER: Path,
    filename: str,
) -> bool:
    """
    Handles a vote_event JSON file by:

    1. Creating the associated bill folder (and placeholder if missing)
    2. Saving the full vote_event as a timestamped log file using result info
       Format: YYYYMMDDT000000Z_vote_event_<result>.json

    Skips and logs errors if bill_identifier is missing.

    Args:
        data (dict): Parsed JSON vote event.
        session_name (str): Folder name for the legislative session.
        DATA_PROCESSED_FOLDER (Path): Base path for processed output.
        DATA_NOT_PROCESSED_FOLDER (Path): Base path for logging unprocessable files.
        filename (str): Original filename (used in logs).
    """
    global VOTE_LATEST_TIMESTAMP
    referenced_bill_id = data.get("bill_identifier")
    if not referenced_bill_id:
        print("⚠️ Warning: Vote missing bill_identifier")
        record_error_file(
            DATA_NOT_PROCESSED_FOLDER,
            "from_handle_vote_event_missing_bill_identifier",
            filename,
            data,
            original_filename=filename,
        )
        return False

    date = data.get("start_date")
    timestamp = format_timestamp(date)
    if timestamp == "unknown":
        print(
            f"⚠️ Vote Event {referenced_bill_id} has unrecognized timestamp format: {date}"
        )
    if timestamp and timestamp != "unknown":
        current_dt = to_dt_obj(timestamp)
        VOTE_LATEST_TIMESTAMP = update_latest_timestamp(
            "vote_events", current_dt, VOTE_LATEST_TIMESTAMP
        )

    save_path = Path(DATA_PROCESSED_FOLDER).joinpath(
        f"country:us",
        f"state:{STATE_ABBR}",
        "sessions",
        "ocd-session",
        f"country:us",
        f"state:{STATE_ABBR}",
        date_folder,
        session_name,
        "bills",
        referenced_bill_id,
    )
    (save_path / "logs").mkdir(parents=True, exist_ok=True)
    (save_path / "files").mkdir(parents=True, exist_ok=True)

    # Add placeholder if bill doesn't exist
    placeholder_file = save_path / "placeholder.json"
    if not placeholder_file.exists():
        placeholder_data = {"identifier": referenced_bill_id, "placeholder": True}
        with open(placeholder_file, "w", encoding="utf-8") as f:
            json.dump(placeholder_data, f, indent=2)
        print(f"📝 Created placeholder for missing bill {referenced_bill_id}")

    # Save the full vote_event log
    write_vote_event_log(data, save_path / "logs")
    return True
