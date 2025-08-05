# Windy Civi Dta Pipeline template: no saved scraped data

## A GitHub Actions-powered pipeline that scrapes, cleans, and versions state legislative data from Open States.

This repository provides a self-contained GitHub Actions workflow to:

1. 🧹 **Scrape** data for a single U.S. state from the OpenStates project
2. 🧼 **Sanitize** it (removing `_id` and `scraped_at` fields for deterministic output)
3. 🧠 **Format** it into a blockchain-style, versioned data structure
4. 📂 **Commit** the formatted output to this repo nightly (or manually)

---

## 🔧 Setup Instructions

1. **Create a new repo** using this one as a template (via GitHub's "Use this template" button).
2. **Rename your repo** using the convention: `STATE-data-pipeline`, replacing `STATE` with the 2-letter abbreviation (e.g. `il`, `tx`, `wi`).
3. In `.github/workflows/update-data.yml`:

- Replace `STATE` under `env:` with the lowercase 2-letter state abbreviation (e.g. `il`, `tx`, `wi`)
- Make sure it matches the folder name used in the [Open States scrapers](https://github.com/openstates/openstates-scrapers/tree/main/scrapers)
- (Optional) Uncomment the schedule block if you want this pipeline to run automatically

```yaml
# schedule:
#   - cron: "0 1 * * *"
```

To enable it, remove the # at the beginning of both lines:

4. Enable GitHub Actions in your repo.

Once set up, the pipeline will run:

- ♻️ **Every night at 1am UTC** (by default — you can change the time by editing the [cron expression](https://crontab.guru/) in `.github/workflows/update-data.yml`)
  , and
- 🧑‍💻 **Any time you manually trigger it from the GitHub UI**

---

## 📁 Folder Structure

```markdown
STATE-windy-civi-data-pipeline/
├── .github/workflows/ # GitHub Actions automation
├── \_data/ # Data downloaded from Open States scrapers (optional; see below to enable/disable)
├── bill_session_mapping/ # Internal mapping of bill IDs to legislative sessions
├── data_output/ # Formatter output files
│ ├── data_processed/ # Clean structured output by session and bill
│ ├── data_not_processed/ # Items that could not be parsed or routed
│ └── event_archive/ # Raw extracted events saved for post-processing
├── openstates_scraped_data_formatter/ # Formatter for blockchain-style output
├── sessions/ # Generated session metadata JSON
├── Pipfile, Pipfile.lock # Formatter dependencies
└── README.md # Project setup and usage info
```

---

## 📦 Output Format

Formatted data is saved to `data_output/data_processed/`, organized by session and bill. Each folder includes:

- `logs/`: timestamped JSONs for bill actions, events, and votes
- `files/`: placeholder for source documents (if enabled)

Additional folders:

- `data_not_processed/`: Items that could not be fully parsed or matched (e.g. missing session info)
- `event_archive/`: Extracted events temporarily stored for linking to bill actions

---

## 🔁 Notes on Workflow Behavior

- The `data_output/`, `bill_session_mapping/`, and `sessions/` folders persist in the repo after each run
- GitHub Actions writes directly to those folders using `rsync`
- No folders are auto-deleted; only overwritten if files change
- Session mappings and new session logs are automatically updated

---

### Optional: Include `_data` in Your Repository

By default, this pipeline will save a copy of the scraped data to a `_data/` folder in your repo. This can be helpful for debugging or reviewing raw input files. However, it will significantly increase your repo size over time, so you may wish to disable it.

We provide templates with `_data` **enabled** and **disabled**. You can switch between them anytime. Here's how:

---

### ✅ To Enable `_data` Saving:

1. **In your GitHub Actions workflow (`.github/workflows/update-data.yml`)**, make sure this step is **uncommented**:

   ```yaml
   - name: Copy Scraped Data to Repo
     run: |
       mkdir -p "$GITHUB_WORKSPACE/_data/$STATE"
       cp -r "${RUNNER_TEMP}/_working/_data/$STATE"/* "$GITHUB_WORKSPACE/_data/$STATE/"
   ```

2. **In the commit step**, make sure `_data` is included:

   ```bash
   git add _data data_output bill_session_mapping sessions
   ```

---

### 🚫 To Disable `_data` Saving:

1. **Comment out the `Copy Scraped Data` step** in `.github/workflows/update-data.yml`:

   ```yaml
   # - name: Copy Scraped Data to Repo
   #   run: |
   #     mkdir -p "$GITHUB_WORKSPACE/_data/$STATE"
   #     cp -r "${RUNNER_TEMP}/_working/_data/$STATE"/* "$GITHUB_WORKSPACE/_data/$STATE/"
   ```

2. **Remove `_data` from the `git add` command**:

   ```bash
   git add data_output bill_session_mapping sessions
   ```

---

## 💬 Questions or Contributions?

This is part of the [Windy Civi](https://github.com/windy-civi) project. If you're working on a new state, want to suggest improvements, or need help, feel free to open an issue or join our Slack!

📝 _Note: You can always copy from the template workflows we provide (`.github/workflows/update-data-with-data.yml` vs `.github/workflows/update-data.yml`) and modify as needed. We recommend disabling `_data` once your setup is stable to keep the repo lightweight._
