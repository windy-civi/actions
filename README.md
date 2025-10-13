# OpenCivicData Blockchain Transformer

A GitHub Actions-powered pipeline that scrapes, formats, and extracts text from state and federal legislative data, organizing it into blockchain-style, versioned data structures.

## 🏗️ Repository Structure

This repository provides **two composite actions** for processing legislative data:

```
├── actions/
│   ├── scrape/              # Scraping & Formatting Action
│   │   └── action.yml       # Docker-based scraping + formatting
│   └── extract/             # Text Extraction Action
│       └── action.yml       # Extract text from PDFs/XMLs
├── scrape_and_format/       # Scraping & formatting code
│   ├── main.py              # Main entry point
│   ├── handlers/            # Data handlers
│   ├── postprocessors/      # Post-processing logic
│   └── utils/               # Utility functions
├── text_extraction/         # Text extraction code
│   ├── main.py              # Extraction entry point
│   └── utils/               # Extraction utilities
│       ├── common.py        # Shared download & error tracking
│       ├── xml_extractor.py # XML text extraction
│       ├── html_extractor.py # HTML text extraction
│       └── pdf_extractor.py # PDF text extraction
├── Pipfile                  # Python dependencies
└── README.md
```

## 🚀 Composite Actions

### Action 1: Scrape & Format Data

**Purpose**: Scrapes legislative data from OpenStates and formats it into blockchain-style structure

**Features**:

- Docker-based scraping using OpenStates scrapers
- Nightly artifact creation (rolling + immutable archives)
- Automatic data formatting and organization
- Commits formatted data to calling repository

**Usage**:

```yaml
- uses: windy-civi/opencivicdata-blockchain-transformer/actions/scrape@main
  with:
    state: tn # State abbreviation (or 'usa' for federal)
    github-token: ${{ secrets.GITHUB_TOKEN }}
    use-scrape-cache: false # Optional: reuse cached data
    force-update: false # Optional: force push changes
```

### Action 2: Extract Text

**Purpose**: Extracts text from bill PDFs, XMLs, and HTMLs for analysis

**Features**:

- Extracts text from XML (structured bill text)
- Extracts text from HTML (web pages)
- Extracts text from PDF (with strikethrough detection)
- Saves both original files and extracted text
- Only processes bill versions (skips amendments to avoid blocking)

**Usage**:

```yaml
- uses: windy-civi/opencivicdata-blockchain-transformer/actions/extract@main
  with:
    state: tn # State abbreviation
    github-token: ${{ secrets.GITHUB_TOKEN }}
    force-update: false # Optional: force push changes
```

## 📋 Complete Workflow Example

```yaml
name: Legislative Data Pipeline
on:
  schedule:
    - cron: "0 1 * * *" # Daily at 1 AM UTC
  workflow_dispatch:

jobs:
  scrape-and-format:
    name: Scrape & Format Data
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: windy-civi/opencivicdata-blockchain-transformer/actions/scrape@main
        with:
          state: tn
          github-token: ${{ secrets.GITHUB_TOKEN }}

  extract-text:
    name: Extract Bill Text
    runs-on: ubuntu-latest
    needs: scrape-and-format
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4

      - uses: windy-civi/opencivicdata-blockchain-transformer/actions/extract@main
        with:
          state: tn
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

## 🔧 Setup

### Prerequisites

- Python 3.12+
- pipenv (for dependency management)
- Docker (for scraping action)

### Local Development

```bash
# Install dependencies
pipenv install

# Run scraping locally
pipenv run python scrape_and_format/main.py \
  --state tn \
  --openstates-data-folder ./data \
  --git-repo-folder ./output

# Run text extraction locally
pipenv run python text_extraction/main.py \
  --state tn \
  --data-folder ./data_output/data_processed \
  --output-folder ./output
```

## 📊 Output Format

### Scraping Output

Data is saved to `data_output/data_processed/`, organized by jurisdiction and session:

```
data_output/data_processed/
└── country:us/
    └── state:tn/
        └── sessions/
            └── 113/
                └── bills/
                    └── HB1234/
                        ├── metadata.json    # Bill metadata
                        ├── logs/            # Actions, events, votes
                        └── files/           # Extracted text (if text extraction run)
```

### Text Extraction Output

For each bill version, creates:

- **Original file**: `BILLS-119hr1enr.xml` (or .html, .pdf)
- **Extracted text**: `BILLS-119hr1enr_extracted.txt`

Extracted text files include:

- Title and official title
- Number of sections
- Source information
- Full extracted text

### Error Tracking

Failed extractions are saved to `data_not_processed/text_extraction_errors/`:

- Individual error files per failed bill
- Summary reports with statistics
- Categorized by error type (download/parsing/save)

## 🎯 Branches

- **`main`**: Stable production code
- **`refactor-text-extraction`**: Text extraction improvements
- **`backup-anti-blocking-code`**: Preserved complex anti-blocking code

## 📚 Key Features

### Modular Text Extraction

- Separate extractors for XML, HTML, and PDF
- Shared download and error tracking utilities
- PDF strikethrough detection for legislative amendments
- Clean, maintainable code structure

### Smart Processing

- Only processes bill versions (actual text)
- Skips amendment documents (to avoid blocking)
- Prioritizes XML > HTML > PDF for best quality
- Handles multiple versions per bill

### Error Handling

- Comprehensive error tracking
- Individual error files for debugging
- Summary reports with statistics
- Continues processing on failures

## 💰 Cost

- **Scraping**: Free (uses OpenStates Docker image)
- **Text Extraction**: Free (no external APIs)
- **GitHub Actions**: Free for public repos, included minutes for private repos

## 🤝 Contributing

This is part of the Windy Civi project. For questions or improvements:

- Open an issue
- Submit a pull request
- Check the documentation in `project_docs/`

---

**Transform legislative data into actionable insights!** 🏛️📊
