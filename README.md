# OpenCivicData Blockchain Transformer

A GitHub Actions-powered pipeline that scrapes, cleans, and formats state legislative data from OpenStates into blockchain-style, versioned data structures.

## 🏗️ Repository Structure

This repository provides **two composite actions** that can be used by state-specific repositories:

```
├── action1/                    # Data Pipeline Action
│   └── action.yml             # Scrapes and formats legislative data
├── action2/                    # LLM Analysis Action
│   └── action.yml             # Analyzes bills using LLM
├── openstates_scraped_data_formatter/  # Core formatter code
│   ├── main.py                # Main entry point
│   ├── handlers/              # Data handlers
│   ├── postprocessors/        # Post-processing logic
│   └── utils/                 # Utility functions
├── Pipfile                    # Python dependencies
└── requirements.txt           # Alternative dependency management
```

## 🚀 Composite Actions

### Action 1: Data Pipeline

- **Purpose**: Scrapes, cleans, and formats state legislative data
- **Branch**: `bill-text-extraction`
- **Functionality**:
  - Scrapes data from OpenStates
  - Formats into blockchain-style structure
  - Commits formatted data to repository

### Action 2: LLM Analysis

- **Purpose**: Analyzes legislative bills using LLM
- **Branch**: `llm-bill-tracker`
- **Functionality**:
  - Summarizes bill content
  - Tracks version changes
  - Generates human-readable reports
  - Cost: ~$0.004 per bill

## 📋 Usage

### For State Repositories

State repositories can use these actions by creating workflows that call the composite actions:

```yaml
# Example: .github/actions/action1/update-data.yml
name: Update Data
on:
  schedule:
    - cron: "0 1 * * *"
  workflow_dispatch:

jobs:
  update-data:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: windy-civi/opencivicdata-blockchain-transformer@bill-text-extraction
        with:
          state: wy
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

```yaml
# Example: .github/actions/action2/llm-analysis.yml
name: LLM Bill Analysis
on:
  schedule:
    - cron: "0 2 * * *"
  workflow_dispatch:

jobs:
  llm-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: windy-civi/opencivicdata-blockchain-transformer@llm-bill-tracker
        with:
          state: wy
          analyze-versions: true
          generate-reports: true
```

## 🔧 Setup

### Prerequisites

- Python 3.11+
- pipenv (for dependency management)
- OpenAI API key (for LLM analysis)

### Installation

```bash
# Install dependencies
pipenv install

# Set up environment variables
export OPENAI_API_KEY="your-api-key-here"
```

## 📊 Output Format

### Data Pipeline Output

Formatted data is saved to `data_output/data_processed/`, organized by session and bill:

- `logs/`: Timestamped JSONs for bill actions, events, and votes
- `files/`: Source documents (if enabled)
- `metadata.json`: Bill metadata at the root of each bill folder

### LLM Analysis Output

- **Bill summaries** with key provisions
- **Version change tracking** between bill versions
- **Human-readable reports** of legislative changes
- **Downloadable artifacts** with full analysis

## 💰 Cost Analysis

- **Data Pipeline**: Free (no external API calls)
- **LLM Analysis**: ~$0.004 per bill
- **100 bills**: ~$0.40
- **1,000 bills**: ~$4.00

## 🎯 Branches

- **`main`**: Stable releases
- **`bill-text-extraction`**: Data pipeline functionality
- **`llm-bill-tracker`**: LLM analysis functionality

## 📚 Documentation

- [LLM Setup Guide](LLM_SETUP_GUIDE.md) - How to use LLM analysis
- [Wyoming Repository Setup](WYOMING_REPO_SETUP.md) - Complete setup guide for state repositories
- [Project Rules](PROJECT_RULES.md) - Data handling rules and standards

## 🤝 Contributing

This is part of the Windy Civi project. For questions, improvements, or help:

- Open an issue
- Join our Slack
- Check the documentation

---

**Ready to transform legislative data!** 🏛️📊
