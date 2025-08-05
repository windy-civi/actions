import re
from datetime import datetime
import json
from pathlib import Path
from urllib import request
from typing import Any, TypedDict


class SessionInfo(TypedDict):
    name: str
    date_folder: str


def format_timestamp(date_str: str) -> str | None:
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%Y%m%dT%H%M%SZ")
    except Exception:
        return None


def extract_session_mapping(jurisdiction_data: dict) -> dict[str, SessionInfo]:
    session_mapping = {}
    for session in jurisdiction_data.get("legislative_sessions", []):
        identifier = session.get("identifier")
        name = session.get("name")
        start = session.get("start_date", "")[:4]
        end = session.get("end_date", "")[:4]
        if identifier and name and start and end:
            session_mapping[identifier] = {
                "name": name,
                "date_folder": f"{start}-{end}",
            }
    return session_mapping


def ensure_session_mapping(
    state_abbr: str, base_path: Path, input_folder: str | Path
) -> dict[str, SessionInfo]:
    """
    Ensures sessions/{state_abbr}.json exists.
    - If jurisdiction_*.json is found, extract and overwrite session cache.
    - If not found, fallback to OpenStates API only if cache doesn't already exist.
    Returns a dictionary like:
    {
        "119": {"name": "119th Congress", "date_folder": "2023-2024"},
        ...
    }
    """
    session_cache_path = base_path / "sessions" / f"{state_abbr}.json"
    sessions_folder = base_path / "sessions"
    sessions_folder.mkdir(parents=True, exist_ok=True)

    # 1. Look for jurisdiction file
    jurisdiction_files = list(Path(input_folder).glob("jurisdiction_*.json"))
    if jurisdiction_files:
        print(f"🔍 Found jurisdiction file — updating sessions/{state_abbr}.json")
        with open(jurisdiction_files[0], "r", encoding="utf-8") as f:
            jurisdiction_data = json.load(f)
        session_mapping = extract_session_mapping(jurisdiction_data)
        if session_mapping:
            with open(session_cache_path, "w", encoding="utf-8") as f:
                json.dump(session_mapping, f, indent=2)
            print(f"📅 Wrote extracted session mapping to sessions/{state_abbr}.json")
            return session_mapping

    # 2. If no jurisdiction file, use existing session cache if it exists
    if session_cache_path.exists():
        print(f"✔️ Using existing sessions/{state_abbr}.json")
        with open(session_cache_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # 3. Fallback: fetch from OpenStates API
    print(f"🌐 Fetching session list from OpenStates API")
    url = f"https://v3.openstates.org/jurisdictions/{state_abbr}/sessions"
    try:
        response = request.get(url, timeout=10)
        if response.status_code == 200:
            sessions = response.json()
            session_mapping = {}
            for s in sessions:
                identifier = s.get("identifier")
                name = s.get("name")
                start = s.get("start_date", "")[:4]
                end = s.get("end_date", "")[:4]
                if identifier and name and start and end:
                    session_mapping[identifier] = {
                        "name": name,
                        "date_folder": f"{start}-{end}",
                    }
            with open(session_cache_path, "w", encoding="utf-8") as f:
                json.dump(session_mapping, f, indent=2)
            print(f"✅ Wrote session mapping to sessions/{state_abbr}.json")
            return session_mapping
        else:
            print(f"⚠️ Failed to fetch sessions (status {response.status_code})")
    except Exception as e:
        print(f"❌ Error fetching sessions: {e}")

    return {}


def record_error_file(
    error_folder: str | Path,
    category: str,
    filename: str,
    data: dict[str, Any],
    original_filename: str | None = None,
) -> None:
    folder = Path(error_folder) / category
    folder.mkdir(parents=True, exist_ok=True)

    # 🔍 Step 1: Get existing names in that folder
    existing_names = set()
    for f in folder.glob("*.json"):
        try:
            with open(f, "r", encoding="utf-8") as existing_file:
                existing_data = json.load(existing_file)
                name = existing_data.get("name")
                if name:
                    existing_names.add(name)
        except Exception:
            continue

    # 🛑 Step 2: Skip if this "name" already exists
    if data.get("name") in existing_names:
        print(f"⚠️ Skipping duplicate org: {data['name']}")
        return

    if original_filename:
        data["_original_filename"] = original_filename

    with open(folder / filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"📄 Saved error file to: {folder / filename}")


def slugify(text: str, max_length=100):
    """
    Converts a string to a safe, lowercase, underscore-separated slug.
    Strips punctuation and truncates long filenames.
    """
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)  # remove punctuation
    text = re.sub(r"\s+", "_", text)  # convert spaces to underscores
    text = text.strip("_")
    return text[:max_length]


def write_action_logs(
    actions: list[dict[str, Any]], bill_identifier: str, log_folder: str | Path
) -> None:
    """
    Writes one JSON file per action for a bill.

    Each file is named: YYYYMMDDT000000Z_<slugified_description>.json
    File contents: { "action": {action}, "bill_id": <bill_identifier> }
    """
    for action in actions:
        date = action.get("date")
        desc = action.get("description", "no_description")
        timestamp = format_timestamp(date) if date else "unknown"
        slug = slugify(desc)

        filename = f"{timestamp}_{slug}.json"
        output_file = Path(log_folder) / filename

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({"action": action, "bill_id": bill_identifier}, f, indent=2)


def write_vote_event_log(vote_event: dict[str, Any], log_folder: str | Path) -> None:
    """
    Saves a single vote_event file as a timestamped log with result-based suffix.

    Filename: YYYYMMDDT000000Z_vote_event_<result>.json
    """
    date = vote_event.get("start_date")
    timestamp = format_timestamp(date) if date else "unknown"
    result = vote_event.get("result", "unknown")
    filename = f"{timestamp}_vote_event_{slugify(result)}.json"

    output_file = Path(log_folder) / filename
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(vote_event, f, indent=2)


def list_json_files(folder: Path) -> list[Path]:
    """
    Returns all .json files in the given folder.

    Args:
        folder (Path): Directory to search.

    Returns:
        list[Path]: List of JSON file paths.
    """
    if not folder.exists() or not folder.is_dir():
        return []

    return sorted(folder.glob("*.json"))
