import json
from pathlib import Path
from postprocessors.helpers import (
    load_bill_to_session_mapping,
    extract_bill_ids_from_event,
    run_handle_event,
)
from utils.file_utils import list_json_files
from utils.session_utils import load_session_mapping


def link_events_to_bills_pipeline(
    STATE_ABBR: str,
    EVENT_ARCHIVE_FOLDER: Path,
    DATA_PROCESSED_FOLDER: Path,
    DATA_NOT_PROCESSED_FOLDER: Path,
    BILL_TO_SESSION_FILE: Path,
    SESSION_MAPPING_FILE: Path,
) -> None:
    """
    Main pipeline for linking events to bills and saving them in the correct folder.
    """
    print("\n📦 Starting event-to-bill linking pipeline")

    session_mapping = load_session_mapping(SESSION_MAPPING_FILE)
    bill_to_session = load_bill_to_session_mapping(
        BILL_TO_SESSION_FILE,
        DATA_PROCESSED_FOLDER,
        session_mapping=session_mapping,
        force_rebuild=True,
    )

    print(f"📂 Loaded {len(bill_to_session)} bill-session mappings")

    skipped = []
    for event_file in list_json_files(EVENT_ARCHIVE_FOLDER):
        with open(event_file) as f:
            data = json.load(f)

        bill_ids = extract_bill_ids_from_event(data)
        if not bill_ids:
            continue

        for bill_id in bill_ids:
            session_meta = bill_to_session.get(bill_id)
            if session_meta:
                run_handle_event(
                    STATE_ABBR,
                    data,
                    session_meta["name"],
                    session_meta["date_folder"],
                    DATA_PROCESSED_FOLDER,
                    DATA_NOT_PROCESSED_FOLDER,
                    bill_id,
                    filename=event_file.name,
                )
                event_file.unlink()
                missing_path = (
                    DATA_NOT_PROCESSED_FOLDER / "missing_session" / event_file.name
                )
                if missing_path.exists():
                    missing_path.unlink()
                break
        else:
            skipped.append((event_file, bill_ids))

    if skipped:
        bill_to_session = load_bill_to_session_mapping(
            BILL_TO_SESSION_FILE,
            DATA_PROCESSED_FOLDER,
            session_mapping=session_mapping,
            force_rebuild=True,
        )

        for event_file, bill_ids in skipped:
            for bill_id in bill_ids:
                session_meta = bill_to_session.get(bill_id)
                if session_meta:
                    with open(event_file) as f:
                        data = json.load(f)
                    run_handle_event(
                        STATE_ABBR,
                        data,
                        session_meta["name"],
                        session_meta["date_folder"],
                        DATA_PROCESSED_FOLDER,
                        DATA_NOT_PROCESSED_FOLDER,
                        referenced_bill_id=bill_id,
                        filename=event_file.name,
                    )
                    event_file.unlink()
                    missing_path = (
                        DATA_NOT_PROCESSED_FOLDER / "missing_session" / event_file.name
                    )
                    if missing_path.exists():
                        missing_path.unlink()
                    break

    print("\n✅ Event-to-bill linking complete")
