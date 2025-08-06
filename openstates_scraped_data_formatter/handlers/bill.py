from pathlib import Path
import json
from typing import Any
from utils.file_utils import format_timestamp, record_error_file, write_action_logs
from utils.download_pdf import download_bill_pdf
from utils.timestamp_tracker import (
    update_latest_timestamp,
    latest_timestamps,
    to_dt_obj,
)

BILL_LATEST_TIMESTAMP = latest_timestamps["bills"]
print(f"💬 (Bill handler) Current latest timestamp: {BILL_LATEST_TIMESTAMP}")


def handle_bill(
    STATE_ABBR: str,
    data: dict[str, Any],
    DATA_PROCESSED_FOLDER: Path,
    DATA_NOT_PROCESSED_FOLDER: Path,
    filename: str,
) -> bool:
    """
    Handles a bill JSON file by saving:

    1. A full snapshot of the bill in logs/ using the earliest action date
    2. One separate JSON file per action in logs/, each timestamped and slugified
    3. A files/ directory, with any linked PDFs downloaded (optional)

    Skips and logs errors if required fields (e.g. identifier) are missing.

    Returns:
        bool: True if saved successfully, False if skipped due to missing identifier.
    """
    DOWNLOAD_PDFS = False
    global BILL_LATEST_TIMESTAMP

    bill_identifier = data.get("identifier")
    if not bill_identifier:
        print("⚠️ Warning: Bill missing identifier")
        record_error_file(
            DATA_NOT_PROCESSED_FOLDER,
            "from_handle_bill_missing_identifier",
            filename,
            data,
            original_filename=filename,
        )
        return False

    is_usa = STATE_ABBR.lower() == "usa"
    session_id = data.get("legislative_session", "unknown-session")
    bill_id = bill_identifier.replace(" ", "")

    if is_usa:
        save_path = Path(DATA_PROCESSED_FOLDER).joinpath(
            "country:us",
            "congress",
            "sessions",
            session_id,
            "bills",
            bill_id,
        )
    else:
        save_path = Path(DATA_PROCESSED_FOLDER).joinpath(
            "country:us",
            f"state:{STATE_ABBR.lower()}",
            "sessions",
            session_id,
            "bills",
            bill_id,
        )

    (save_path / "logs").mkdir(parents=True, exist_ok=True)
    (save_path / "files").mkdir(parents=True, exist_ok=True)

    actions = data.get("actions", [])
    if actions:
        dates = [a.get("date") for a in actions if a.get("date")]
        timestamp = format_timestamp(sorted(dates)[0]) if dates else None
        if timestamp and timestamp != "unknown":
            current_dt = to_dt_obj(timestamp)
            BILL_LATEST_TIMESTAMP = update_latest_timestamp(
                "bills", current_dt, BILL_LATEST_TIMESTAMP
            )
    else:
        timestamp = None

    if not timestamp:
        print(f"⚠️ Warning: Bill {bill_identifier} missing action dates")
        timestamp = "unknown"

    # Save entire bill
    full_filename = f"{timestamp}_entire_bill.json"
    output_file = save_path.joinpath("logs", full_filename)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # Save each action as a separate file
    if actions:
        write_action_logs(actions, bill_identifier, save_path / "logs")

    if DOWNLOAD_PDFS:
        download_bill_pdf(data, save_path, bill_identifier)

    return True
