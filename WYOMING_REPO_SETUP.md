# 🏛️ Wyoming Repository Setup Guide

This guide shows how to set up the Wyoming repository (`windy-civi-pipelines/wy-data-pipeline-with-text`) to use the composite actions from the main repository.

## 📁 Repository Structure

Create this structure in your Wyoming repository:

```
.github/
├── actions/
│   ├── action1/
│   │   └── update-data.yml
│   └── action2/
│       └── llm-analysis.yml
```

## 🔧 Action 1: Data Pipeline

Create `.github/actions/action1/update-data.yml`:

```yaml
name: Update Data

on:
  schedule:
    - cron: "0 1 * * *" # every day at 1am UTC
  workflow_dispatch:
    inputs:
      use-scrape-cache:
        type: boolean
        description: "Use open states scraper cache"
      force-update:
        type: boolean
        description: "Force push changes even if there are upstream changes (use with caution)"

jobs:
  update-data:
    name: Update Data
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Use Data Pipeline Action
        uses: windy-civi/opencivicdata-blockchain-transformer@bill-text-extraction
        with:
          state: wy
          github-token: ${{ secrets.GITHUB_TOKEN }}
          use-scrape-cache: ${{ inputs.use-scrape-cache }}
          force-update: ${{ inputs.force-update }}

      - name: Summary
        run: |
          echo "✅ Data pipeline complete!"
          echo "📊 Check the data_output/ directory for results"
          echo "🕒 Run completed at: $(date)"
```

## 🤖 Action 2: LLM Analysis

Create `.github/actions/action2/llm-analysis.yml`:

```yaml
name: LLM Bill Analysis

on:
  schedule:
    - cron: "0 2 * * *" # every day at 2am UTC (after data update)
  workflow_dispatch:
    inputs:
      state:
        type: choice
        description: "State to analyze"
        options:
          - wy
          - all
        default: "wy"
      analyze-versions:
        type: boolean
        description: "Analyze bill versions and track changes"
        default: true
      generate-reports:
        type: boolean
        description: "Generate human-readable reports"
        default: true

jobs:
  llm-bill-analysis:
    name: LLM Bill Analysis
    runs-on: ubuntu-latest
    permissions:
      contents: read
      actions: read

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Use LLM Analysis Action
        uses: windy-civi/opencivicdata-blockchain-transformer@llm-bill-tracker
        with:
          state: ${{ inputs.state }}
          analyze-versions: ${{ inputs.analyze-versions }}
          generate-reports: ${{ inputs.generate-reports }}

      - name: Summary
        run: |
          echo "🤖 LLM analysis complete!"
          echo "📊 State analyzed: ${{ inputs.state }}"
          echo "📄 Reports generated: ${{ inputs.generate-reports }}"
          echo "🕒 Run completed at: $(date)"
          echo ""
          echo "💡 Download artifacts to view detailed reports"
```

## 🔑 Setup Requirements

### 1. Add OpenAI API Key to Secrets

In your Wyoming repository:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `OPENAI_API_KEY`
4. Value: Your OpenAI API key
5. Click **Add secret**

### 2. Enable GitHub Actions

Make sure GitHub Actions are enabled in your repository:

1. Go to **Settings** → **Actions** → **General**
2. Ensure "Allow all actions and reusable workflows" is selected

## 🚀 How It Works

### Action 1 (Data Pipeline):

- **Pulls from**: `windy-civi/opencivicdata-blockchain-transformer@bill-text-extraction`
- **Function**: Scrapes and formats Wyoming legislative data
- **Schedule**: Daily at 1am UTC
- **Output**: Formatted data in `data_output/` directory

### Action 2 (LLM Analysis):

- **Pulls from**: `windy-civi/opencivicdata-blockchain-transformer@llm-bill-tracker`
- **Function**: Analyzes bills using LLM for summaries and changes
- **Schedule**: Daily at 2am UTC (after data update)
- **Output**: Analysis reports and artifacts

## 📊 Benefits

1. **Clean Separation**: Data pipeline and LLM analysis are separate
2. **Independent Versioning**: Each action can be updated independently
3. **Easy Maintenance**: Clear structure and organization
4. **Scalable**: Easy to add more states or features

## 🎯 Next Steps

1. **Create the file structure** in your Wyoming repository
2. **Add the workflow files** as shown above
3. **Add your OpenAI API key** to secrets
4. **Test the workflows** by triggering them manually
5. **Monitor the results** in the Actions tab

## 💰 Cost Tracking

- **Data Pipeline**: Free (no external API calls)
- **LLM Analysis**: ~$0.004 per bill
- **Daily Wyoming Analysis**: ~$0.032 (8 versions)

---

**Ready to analyze Wyoming legislation!** 🏛️📊
