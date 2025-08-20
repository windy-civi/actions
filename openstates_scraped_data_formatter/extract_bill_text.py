import click
from pathlib import Path
from utils.text_extraction import process_bills_in_batch


@click.command()
@click.option(
    "--processed-folder",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    required=True,
    help="Path to the processed data folder containing bill metadata.json files.",
)
@click.option(
    "--batch-size",
    type=int,
    default=100,
    help="Number of bills to process in each batch (default: 100).",
)
def main(processed_folder: Path, batch_size: int):
    """
    Extract bill text from URLs found in metadata.json files.

    This script processes bills in batches to extract text from XML URLs
    found in the versions array of each bill's metadata.json file.

    The extracted text is saved in the files/ directory of each bill.
    """
    print("🚀 Starting bill text extraction...")
    print(f"📁 Processing folder: {processed_folder}")
    print(f"📦 Batch size: {batch_size}")

    stats = process_bills_in_batch(processed_folder, batch_size)

    print(f"\n📊 Extraction Complete!")
    print(f"Total bills: {stats['total_bills']}")
    print(f"Processed: {stats['processed']}")
    print(f"Successful: {stats['successful']}")
    print(f"Errors: {stats['errors']}")


if __name__ == "__main__":
    main()
