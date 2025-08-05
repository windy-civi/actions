import json
from pathlib import Path
from datetime import datetime
from typing import Any, Optional
from utils.file_utils import format_timestamp, record_error_file

LATEST_TIMESTAMP_PATH = (
    Path(__file__).resolve().parents[2] / "data_output/latest_timestamp_seen.txt"
)

latest_timestamps: dict[str, datetime] = {
    "bills": datetime(1900, 1, 1),
    "vote_events": datetime(1900, 1, 1),
    "events": datetime(1900, 1, 1),
}

def to_dt_obj(ts_str: str | datetime) -> Optional[datetime]:
    if isinstance(ts_str, datetime):
        return ts_str
    try:
        ts_str = ts_str.rstrip("Z")
        if "-" in ts_str:
            return datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S")
        else:
            return datetime.strptime(ts_str, "%Y%m%dT%H%M%S")
    except Exception as e:
        print(f"❌ Failed to parse timestamp: {ts_str} ({e})")
        return None

def read_all_latest_timestamps():
    global latest_timestamps
    try:
        with open(LATEST_TIMESTAMP_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)
            print(f"📂 Raw timestamp file contents: {json.dumps(raw, indent=2)}")
            latest_timestamps = {k: to_dt_obj(v) for k, v in raw.items() if v}
    except Exception:
        print("⚠️ No timestamp file found or invalid JSON. Using defaults.")
        latest_timestamps = {
            "bills": datetime(1900, 1, 1),
            "vote_events": datetime(1900, 1, 1),
            "events": datetime(1900, 1, 1),
        }

def update_latest_timestamp(
    category: str,
    current_dt: Optional[datetime],
    existing_dt: Optional[datetime],
) -> Optional[datetime]:
    if not current_dt:
        return existing_dt

    if not existing_dt or current_dt > existing_dt:
        latest_timestamps[category] = current_dt
        print(f"🕓 Updating {category} latest timestamp to {current_dt}")
        print(f"📄 File contents: {latest_timestamps}")
        return current_dt

    return existing_dt

def extract_timestamp(data: dict[str, Any], category: str) -> str | None:
    try:
        if category == "bills":
            actions = data.get("actions", [])
            if not actions:
                return "NO_ACTIONS_FOUND"
            dates = [a.get("date") for a in actions if a.get("date")]
            if not dates:
                return "NO_DATES_IN_ACTIONS"
            try:
                return format_timestamp(min(dates))
            except Exception:
                return "INVALID_BILL_DATE"

        elif category == "events":
            date = data.get("start_date")
            if date:
                return format_timestamp(date)
            return "MISSING_EVENT_DATE"

        elif category == "vote_events":
            date = data.get("start_date")
            if date:
                return format_timestamp(date)
            return "MISSING_VOTE_DATE"

        return "UNKNOWN_CATEGORY"

    except Exception as e:
        return f"ERROR_{category.upper()}_{str(e)}"

def is_newer_than_latest(
    data: dict[str, Any],
    latest_timestamp_dt: datetime,
    category: str,
    DATA_NOT_PROCESSED_FOLDER: Path,
) -> bool:
    raw_ts = extract_timestamp(data, category)

    if isinstance(raw_ts, str) and raw_ts in {
        "NO_ACTIONS_FOUND",
        "NO_DATES_IN_ACTIONS",
        "INVALID_BILL_DATE",
        "MISSING_EVENT_DATE",
        "MISSING_VOTE_DATE",
        "UNKNOWN_CATEGORY",
    }:
        print(f"⚠️ Skipping item in {category} — invalid timestamp: {raw_ts}")
        record_error_file(
            DATA_NOT_PROCESSED_FOLDER,
            f"from_is_newer_than_latest_{raw_ts.lower()}",
            filename="unknown.json",
            data=data,
        )
        return False

    try:
        current_dt = to_dt_obj(raw_ts)
        return current_dt > latest_timestamp_dt if current_dt else False
    except Exception as e:
        print(f"❌ Failed to parse timestamp '{raw_ts}' in {category}: {e}")
        record_error_file(
            DATA_NOT_PROCESSED_FOLDER,
            f"from_is_newer_than_latest_parse_error",
            filename="unknown.json",
            data=data,
            original_filename=raw_ts,
        )
        return False

def write_latest_timestamp_file():
    try:
        output = {}
        for k, dt in latest_timestamps.items():
            if isinstance(dt, datetime):
                output[k] = dt.strftime("%Y-%m-%dT%H:%M:%S")

        if not output:
            print("⚠️ No timestamps to write.")
            return

        LATEST_TIMESTAMP_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LATEST_TIMESTAMP_PATH, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)

        print(f"📝 Updated latest timestamp path: {LATEST_TIMESTAMP_PATH}")
        print("📄 File contents:")
        print(json.dumps(output, indent=2))

    except Exception as e:
        print(f"❌ Failed to write latest timestamp: {e}")
