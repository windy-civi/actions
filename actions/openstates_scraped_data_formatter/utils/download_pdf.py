from pathlib import Path
from urllib import request
from typing import Any


def download_bill_pdf(
    data: dict[str, Any], save_path: Path, bill_identifier: str
) -> None:
    versions = data.get("versions", [])
    if not versions:
        print("⚠️ No versions found for bill")
        return

    files_dir = save_path / "files"
    files_dir.mkdir(parents=True, exist_ok=True)

    for version in versions:
        for link in version.get("links", []):
            url = link.get("url")
            if url and url.endswith(".pdf"):
                try:
                    response = request.get(url, timeout=10)
                    if response.status_code == 200:
                        filename = f"{bill_identifier}.pdf"
                        file_path = files_dir / filename
                        with open(file_path, "wb") as f:
                            f.write(response.data)
                        print(f"📄 Downloaded PDF: {filename}")
                    else:
                        print(
                            f"⚠️ Failed to download PDF: {url} (status {response.status_code})"
                        )
                except Exception as e:
                    print(f"❌ Error downloading PDF: {url} ({e})")
