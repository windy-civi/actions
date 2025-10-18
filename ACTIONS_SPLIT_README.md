# Actions Split Documentation

## Overview

The monolithic `actions/scrape/action.yml` has been split into two separate actions for better debugging and data preservation:

1. **`actions/scrape/action.yml`** - Handles data scraping only
2. **`actions/format/action.yml`** - Handles data formatting only

## Benefits

### 🔍 **Better Debugging**

- **Before**: One massive job with 50,000+ lines of logs
- **After**: Two focused jobs with clear separation of concerns
- Easier to identify whether issues are in scraping or formatting

### 💾 **Data Preservation**

- **Before**: If formatting failed, you had to re-scrape everything
- **After**: Scraped data is saved as artifacts between jobs
- If formatting fails, you can re-run just the formatting job

### 🚀 **Performance**

- **Before**: Sequential processing in one job
- **After**: Can potentially parallelize scraping and formatting for different states
- Better resource utilization

## Usage

### For Caller Repos

#### Basic Pipeline (Scrape + Format)

Update your workflow to use two separate jobs. See `docs/example-caller-workflow.yml` for a complete example:

#### Independent Text Extraction

**Quick Start**: Copy `docs/example-caller-text-extraction.yml` to your state repo as `.github/workflows/extract-text.yml` and update the state code.

For a more advanced example with scheduling and state selection, see `docs/example-text-extraction-workflow.yml`.

```yaml
jobs:
  scrape:
    name: "🕷️ Scrape Data"
    runs-on: ubuntu-latest
    outputs:
      scrape-artifact-name: ${{ steps.scrape.outputs.scrape-artifact-name }}
    steps:
      - name: Checkout caller repo
        uses: actions/checkout@v4

      - name: Run scraper
        id: scrape
        uses: windy-civi/opencivicdata-blockchain-transformer/actions/scrape@main
        with:
          state: usa
          github-token: ${{ secrets.GITHUB_TOKEN }}

  format:
    name: "📝 Format Data"
    runs-on: ubuntu-latest
    needs: scrape
    steps:
      - name: Checkout caller repo
        uses: actions/checkout@v4

      - name: Download scrape artifact
        uses: actions/download-artifact@v4
        with:
          name: ${{ needs.scrape.outputs.scrape-artifact-name }}

      - name: Run formatter
        uses: windy-civi/opencivicdata-blockchain-transformer/actions/format@main
        with:
          state: usa
          github-token: ${{ secrets.GITHUB_TOKEN }}
          scrape-artifact-name: ${{ needs.scrape.outputs.scrape-artifact-name }}
```

### Action Parameters

#### Scrape Action

- `state`: State abbreviation (required)
- `github-token`: GitHub token (required)
- `use-scrape-cache`: Skip scraping and reuse nightly artifact (optional, default: "false")

#### Format Action

- `state`: State abbreviation (required)
- `github-token`: GitHub token (required)
- `scrape-artifact-name`: Name of scrape artifact to download (optional, default: "scrape-snapshot-nightly")
- `force-update`: Force push even if upstream changed (optional, default: "false")

#### Extract Text Action

- `state`: State abbreviation (required)
- `github-token`: GitHub token (required)
- `force-update`: Force push even if upstream changed (optional, default: "false")

**Features**:

- **Incremental Processing**: Automatically skips bills that have already been processed, checking the `text_extraction_latest_update` timestamp in metadata
- **Auto-Save Failsafe**: Commits and pushes progress every 30 minutes to prevent data loss if the job times out
- **Resume Capability**: If the job times out (6-hour GitHub limit), restart it and it will continue from where it left off

## Migration Guide

### Step 1: Update Caller Repo Workflow

Replace your current single job with two separate jobs as shown above.

### Step 2: Test the Split

1. Run the scrape job first
2. Verify the artifact is uploaded
3. Run the format job
4. Verify data flows correctly

### Step 3: Monitor and Optimize

- Check job logs are more manageable
- Verify data preservation works as expected
- Consider parallelizing for multiple states

## Troubleshooting

### Common Issues

1. **Artifact not found**: Ensure the scrape job completes successfully before running format
2. **Permission errors**: Make sure GitHub token has proper permissions
3. **Path issues**: Verify artifact names match between jobs

### Debugging Tips

- Check scrape job logs for scraping issues
- Check format job logs for formatting issues
- Use artifact browser to verify scraped data
- Check job dependencies are correct

## Files Changed

- `actions/scrape/action.yml` - New scrape-only action
- `actions/format/action.yml` - New format-only action
- `actions/extract/action.yml` - Text extraction action with incremental processing and auto-save
- `docs/example-caller-workflow.yml` - Example caller repo workflow (scrape + format)
- `docs/example-caller-text-extraction.yml` - Simple example for caller repos (recommended)
- `docs/example-text-extraction-workflow.yml` - Advanced text extraction workflow example
- `text_extraction/main.py` - Added incremental processing support
- `text_extraction/utils/text_extraction.py` - Added incremental processing logic
- `ACTIONS_SPLIT_README.md` - This documentation

## Backward Compatibility

The old monolithic action is still available but deprecated. New implementations should use the split actions.
