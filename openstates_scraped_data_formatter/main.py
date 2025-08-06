import click
from pathlib import Path
from tempfile import mkdtemp

from utils.timestamp_tracker import (
    read_latest_timestamps,
    LatestTimestamps,
)

from utils.io_utils import load_json_files
from utils.file_utils import ensure_session_mapping
from utils.process_utils import process_and_save
from postprocessors.event_bill_linker import link_events_to_bills_pipeline
from utils.file_utils import verify_folder_exists

SESSION_MAPPING = {}


@click.command()
@click.option(
    "--state",
    required=True,
    help="Jurisdiction code to process.",
)
@click.option(
    "--openstates-data-folder",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    required=True,
    help="Path to the input folder containing JSON files.",
)
@click.option(
    "--git-repo-folder",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    required=True,
    help="Path to the output folder where processed files will be saved.",
)
def main(
    state: str,
    openstates_data_folder: Path,
    git_repo_folder: Path,
):
    STATE_ABBR = state.lower()
    DATA_OUTPUT = git_repo_folder / "data_output"
    DATA_PROCESSED_FOLDER = DATA_OUTPUT / "data_processed"
    DATA_NOT_PROCESSED_FOLDER = DATA_OUTPUT / "data_not_processed"
    EVENT_ARCHIVE_FOLDER = DATA_OUTPUT / "event_archive"
    # Created to map bills with no session metadata
    BILL_TO_SESSION_FILE = git_repo_folder / "bill_session_mapping" / f"{STATE_ABBR}.json"
    # Maps dates to session names and folders
    # e.g. "113": {"name": "113th Congress", "date_folder": "2013-2015"}
    SESSION_MAPPING_FILE = git_repo_folder / "sessions" / f"{STATE_ABBR}.json"
    SESSION_LOG_PATH = DATA_OUTPUT / "new_sessions_added.txt"

    # Ensure output folders exist
    DATA_PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)
    DATA_NOT_PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)
    EVENT_ARCHIVE_FOLDER.mkdir(parents=True, exist_ok=True)
    (BILL_TO_SESSION_FILE.parent).mkdir(parents=True, exist_ok=True)
    (SESSION_MAPPING_FILE.parent).mkdir(parents=True, exist_ok=True)

    # Read latest timestamps using the output folder
    latest_timestamps: LatestTimestamps = read_latest_timestamps(git_repo_folder)
    print(f"💬 Latest timestamps: {latest_timestamps}")

    # 1. Verify input_folder exists
    verify_folder_exists(openstates_data_folder)
    # 2. Ensure state specific session mapping is available
    SESSION_MAPPING.update(
        ensure_session_mapping(STATE_ABBR, git_repo_folder, openstates_data_folder)
    )

    # 3. Load and parse all input JSON files
    all_json_files = load_json_files(
        openstates_data_folder,
        EVENT_ARCHIVE_FOLDER,
        DATA_NOT_PROCESSED_FOLDER,
        latest_timestamps,
    )

    # 4. Route and process by handler (returns counts)
    counts = process_and_save(
        STATE_ABBR,
        all_json_files,
        DATA_NOT_PROCESSED_FOLDER,
        SESSION_MAPPING,
        SESSION_LOG_PATH,
        DATA_PROCESSED_FOLDER,
        latest_timestamps,
        git_repo_folder,
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
