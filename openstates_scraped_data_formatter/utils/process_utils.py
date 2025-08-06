import click
from typing import Optional
from pathlib import Path
from collections.abc import Callable
from handlers import bill, vote_event, event
from utils.file_utils import record_error_file
from utils.interactive import prompt_for_session_fix
from utils.timestamp_tracker import write_latest_timestamp_file


def count_successful_saves(
    files: list[Path], handler_function: Callable[[Path], bool]
) -> int:

    count = 0
    for file_path in files:
        success = handler_function(file_path)
        if success:
            count += 1
    return count


def route_handler(
    STATE_ABBR: str,
    filename: str,
    data: dict,
    DATA_NOT_PROCESSED_FOLDER: Path,
    DATA_PROCESSED_FOLDER: Path,
) -> Optional[str]:

    if "bill_" in filename:
        success = bill.handle_bill(
            STATE_ABBR,
            data,
            DATA_PROCESSED_FOLDER,
            DATA_NOT_PROCESSED_FOLDER,
            filename,
        )
        return "bill" if success else None

    elif "vote_event_" in filename:
        success = vote_event.handle_vote_event(
            STATE_ABBR,
            data,
            DATA_PROCESSED_FOLDER,
            DATA_NOT_PROCESSED_FOLDER,
            filename,
        )
        return "vote_event" if success else None

    elif "event_" in filename:
        success = event.handle_event(
            STATE_ABBR,
            data,
            DATA_PROCESSED_FOLDER,
            DATA_NOT_PROCESSED_FOLDER,
            filename,
        )
        return "event" if success else None

    else:
        print(f"❓ Unrecognized file type: {filename}")
        return None


def process_and_save(
    STATE_ABBR: str,
    data: list[tuple[str, dict]],
    DATA_NOT_PROCESSED_FOLDER: Path,
    SESSION_MAPPING: dict[str, dict[str, str]],
    SESSION_LOG_PATH: Path,
    DATA_PROCESSED_FOLDER: Path,
) -> dict[str, int]:
    bill_count = 0
    event_count = 0
    vote_event_count = 0

    for filename, data in data:
        session = data.get("legislative_session")
        if not session:
            print(f"⚠️ Skipping {filename}, missing legislative_session")
            record_error_file(
                DATA_NOT_PROCESSED_FOLDER, "missing_session", filename, data
            )
            continue

        session_metadata = SESSION_MAPPING.get(session)

        # Prompt user to fix if session is unknown: by default is toggled off
        if (
            not session_metadata
            and click.get_current_context().params["allow_session_fix"]
        ):
            new_session = prompt_for_session_fix(
                filename, session, log_path=SESSION_LOG_PATH
            )
            if new_session:
                SESSION_MAPPING[session] = new_session
                session_metadata = new_session

        if not session_metadata:
            record_error_file(
                DATA_NOT_PROCESSED_FOLDER, "unknown_session", filename, data
            )
            continue

        result = route_handler(
            STATE_ABBR,
            filename,
            data,
            DATA_NOT_PROCESSED_FOLDER,
            DATA_PROCESSED_FOLDER,
        )
        if result not in ("bill", "event", "vote_event"):
            print(f"⚠️ Unrecognized result from handler for {filename}: {result}")
            continue

        if result == "bill":
            bill_count += 1
        elif result == "event":
            event_count += 1
        elif result == "vote_event":
            vote_event_count += 1
    write_latest_timestamp_file()
    print("\n✅ File processing complete.")
    return {
        "bills": bill_count,
        "events": event_count,
        "votes": vote_event_count,
    }
