import click
from pathlib import Path
from tempfile import mkdtemp

from utils.timestamp_tracker import (
    read_all_latest_timestamps,
    latest_timestamps,
)

read_all_latest_timestamps()
print(f"💬 Latest timestamps: {latest_timestamps}")

from utils.io_utils import load_json_files
from utils.file_utils import ensure_session_mapping
from utils.process_utils import process_and_save
from postprocessors.event_bill_linker import link_events_to_bills_pipeline

BASE_FOLDER = Path(__file__).parent.parent
SESSION_MAPPING = {}


@click.command()
@click.option(
    "--state",
    required=True,
    help="Jurisdiction code to process.",
)
@click.option(
    "--input-folder",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    required=True,
    help="Path to the input folder containing JSON files.",
)
@click.option(
    "--allow-session-fix/--no-allow-session-fix",
    default=True,
    help="Allow interactive session fixes when session names are missing.",
)
def main(
    state: str,
    input_folder: Path,
    allow_session_fix: bool,
):
    STATE_ABBR = state.lower()
    DATA_OUTPUT = BASE_FOLDER / "data_output"
    DATA_PROCESSED_FOLDER = DATA_OUTPUT / "data_processed"
    DATA_NOT_PROCESSED_FOLDER = DATA_OUTPUT / "data_not_processed"
    EVENT_ARCHIVE_FOLDER = DATA_OUTPUT / "event_archive"
    # Created to map bills with no session metadata
    BILL_TO_SESSION_FILE = BASE_FOLDER / "bill_session_mapping" / f"{STATE_ABBR}.json"
    # Maps dates to session names and folders
    # e.g. "113": {"name": "113th Congress", "date_folder": "2013-2015"}
    SESSION_MAPPING_FILE = BASE_FOLDER / "sessions" / f"{STATE_ABBR}.json"
    SESSION_LOG_PATH = DATA_OUTPUT / "new_sessions_added.txt"

    # 1. Ensure output folders exist
    DATA_PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)
    DATA_NOT_PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)
    EVENT_ARCHIVE_FOLDER.mkdir(parents=True, exist_ok=True)
    (BILL_TO_SESSION_FILE.parent).mkdir(parents=True, exist_ok=True)
    (SESSION_MAPPING_FILE.parent).mkdir(parents=True, exist_ok=True)

    # 2. Ensure state specific session mapping is available
    SESSION_MAPPING.update(
        ensure_session_mapping(STATE_ABBR, BASE_FOLDER, input_folder)
    )

    # 3. Load and parse all input JSON files
    all_json_files = load_json_files(
        input_folder,
        EVENT_ARCHIVE_FOLDER,
        DATA_NOT_PROCESSED_FOLDER,
    )

    # 4. Route and process by handler (returns counts)
    counts = process_and_save(
        STATE_ABBR,
        all_json_files,
        DATA_NOT_PROCESSED_FOLDER,
        SESSION_MAPPING,
        SESSION_LOG_PATH,
        DATA_PROCESSED_FOLDER,
    )

    # 5. Link archived event logs to state sessions and save
    if EVENT_ARCHIVE_FOLDER.exists():
        print("Linking event references to related bills...")
        link_events_to_bills_pipeline(
            STATE_ABBR,
            EVENT_ARCHIVE_FOLDER,
            DATA_PROCESSED_FOLDER,
            DATA_NOT_PROCESSED_FOLDER,
            BILL_TO_SESSION_FILE,
            SESSION_MAPPING_FILE,
        )
    else:
        print(
            f"⚠️ Event archive folder {EVENT_ARCHIVE_FOLDER} does not exist. Skipping event linking.\n🚀 Processing complete."
        )
    print("Processing summary:")
    print(f"Bills saved: {counts.get('bills', 0)}")
    print(f"Vote events saved: {counts.get('votes', 0)}")


if __name__ == "__main__":
    main(auto_envvar_prefix="OSDF")
