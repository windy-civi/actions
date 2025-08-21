# 🔑 LLM Bill Tracker Setup Guide

Quick setup guide for using the LLM bill tracker with GitHub Actions.

## 🚀 Option 1: GitHub Secrets (Recommended)

### 1. Add OpenAI API Key to Repository Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `OPENAI_API_KEY`
5. Value: Your OpenAI API key
6. Click **Add secret**

### 2. Run the Workflow

The workflow will automatically use the secret. You can trigger it:

- **Manually**: Go to **Actions** → **LLM Bill Analysis** → **Run workflow**
- **Automatically**: Runs daily at 2am UTC (after main data update)

## 🚀 Option 2: Manual API Key Input

### 1. Run Workflow Manually

1. Go to **Actions** → **LLM Bill Analysis**
2. Click **Run workflow**
3. Fill in the inputs:
   - **State**: `wy` (or `all`)
   - **API Key**: Paste your OpenAI API key
   - **Analyze versions**: ✅ (checked)
   - **Generate reports**: ✅ (checked)
4. Click **Run workflow**

## 🚀 Option 3: Local Development

### 1. Set Environment Variable

```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 2. Run Locally

```bash
# Activate virtual environment
source venv/bin/activate

# Run analysis
python openstates_scraped_data_formatter/cli_bill_tracker.py analyze --show-summary
```

## 📊 What You'll Get

### GitHub Actions Output:
- **Artifacts**: Downloadable JSON reports
- **Logs**: Detailed analysis progress
- **Summary**: Overview of what was analyzed

### Report Contents:
- Bill summaries and key provisions
- Version change tracking
- Human-readable change summaries
- Bill evolution analysis

## 💰 Cost Tracking

- **Per bill**: ~$0.004
- **100 bills**: ~$0.40
- **1,000 bills**: ~$4.00

Monitor your OpenAI usage at: https://platform.openai.com/usage

## 🔧 Troubleshooting

### No API Key Provided
- System runs in "mock mode"
- Shows structure but no real LLM analysis
- Good for testing the workflow

### Missing Dependencies
- Workflow automatically installs required packages
- Check logs for any installation errors

### No Sample Data
- Ensure `sample_data/wy_sample/` exists
- Add your bill data to the repository

## 🎯 Next Steps

1. **Test with Wyoming data** (already included)
2. **Add more states** by extending the workflow
3. **Customize analysis** by modifying the LLM prompts
4. **Scale up** to process more bills

---

**Ready to analyze some bills!** 🏛️📊
