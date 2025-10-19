# 🏛️ Windy Civi: OpenCivicData Blockchain Transformer

A GitHub Actions-powered pipeline that scrapes, formats, and extracts text from state and federal legislative data, organizing it into blockchain-style, versioned data structures. But more than that, it’s part of a larger mission to make civic data transparent, permanent, and accessible to everyone.

## 💡 Why This Matters

Democracy relies on accessible information. Legislative data in the U.S. is often fragmented, inconsistently formatted, and easily lost when administrations change or sites go offline. **Windy Civi** is designed to solve that problem by creating a _decentralized, verifiable record_ of bills, votes, and actions—structured like a blockchain for traceability and accountability.

This project is inspired by open data movements and maintained by contributors who believe civic infrastructure should be public, durable, and transparent.

## 🧠 On AI and Collaboration

This project was developed with the help of AI tools like **ChatGPT** and **Cursor**, which I used as active collaborators rather than shortcuts. They were especially helpful when exploring architecture decisions, discussing different ways to structure functions, design data flows, and think through tradeoffs that are usually hard to reason about alone.

In many ways, AI became a kind of mentor. It helped me clarify my reasoning, consider alternative approaches, and better understand the 'why' behind every choice. But it also forced me to slow down. I learned to pause, ask questions, and make sure I truly understood what was being built rather than just moving fast.

Most unexpectedly, this process dramatically improved my debugging skills. By breaking problems into smaller conversations and exploring edge cases in real time, I became much more methodical and confident when tracking down issues. In short, coding with AI has been less about automation—and more about becoming a sharper, more reflective engineer.

## 🏗️ Repository Structure

```
├── actions/
│   ├── scrape/              # Scraping & Formatting Action
│   │   └── action.yml       # Docker-based scraping + formatting
│   └── extract/             # Text Extraction Action
│       └── action.yml       # Extract text from PDFs/XMLs
├── scrape_and_format/       # Scraping & formatting logic
├── text_extraction/         # Text extraction modules
│   └── utils/               # Shared utilities for parsing
├── Pipfile                  # Python dependencies
└── README.md
```

## 🚀 Composite Actions

This pipeline uses **modular GitHub Actions** that can be run independently or chained together.

### Action 1: Scrape Data

Scrapes legislative data from **OpenStates** using Docker.

**Features:**

- Docker-based scraping using OpenStates scrapers
- Artifact creation for passing data between jobs
- Nightly releases (rolling + immutable archives)

### Action 2: Format Data

Formats scraped data into blockchain-style directories.

**Features:**

- Incremental processing (only processes new/updated bills)
- Automatic session detection via API
- Concurrent job support (git pull before commit)

### Action 3: Extract Text

Extracts readable bill text from XML, HTML, or PDF versions.

**Features:**

- Incremental processing (skips already-extracted bills)
- Auto-save every 30 minutes (prevents timeout data loss)
- Multi-format extraction (XML > HTML > PDF)
- Resumable after GitHub's 6-hour timeout

**Example Usage:**

See [example workflows](docs/) for complete setup:

- `example-caller-workflow.yml` - Scrape + Format pipeline
- `example-caller-text-extraction.yml` - Text extraction (independent)

## 📊 Output Example

```
data_output/data_processed/
└── country:us/
    └── congress/                    # or state:tn/ for state data
        └── sessions/119/
            ├── bills/
            │   └── HR1234/
            │       ├── metadata.json           # Bill data + _processing timestamps
            │       ├── logs/                   # Action logs + vote events
            │       └── files/                  # Bill text (XML, PDF, extracted)
            └── events/                         # Hearing/committee events
                └── 20250325_hearing.json
```

Each bill includes structured metadata with incremental processing timestamps, versioned text files, and action logs—creating a traceable digital record of legislative change.

## ⚙️ Setup

**Requirements:**

- Python 3.12+
- pipenv
- Docker (for scraping)

```bash
pipenv install
pipenv run python scrape_and_format/main.py --state tn
```

## 🌍 Project Vision

Windy Civi’s long-term goal is to create a **permanent, blockchain-style public archive** for all legislative data—linking together OpenStates scrapers, GitHub repositories, and decentralized storage. Think of it as a civic data backbone for researchers, journalists, and citizens.

## 🤝 Contributing

This project is part of the broader **Windy Civi** ecosystem—a civic tech initiative based in Chicago focused on open data and transparency. We welcome collaborators, contributors, and curious minds.

- 🐙 [Open an Issue](https://github.com/windy-civi)
- 📬 Submit a PR
- 🌱 Help design future civic pipelines

**Built with care, code, and curiosity.** 🏛️✨
