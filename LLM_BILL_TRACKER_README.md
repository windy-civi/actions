# 🤖 Wyoming Bill Tracker with LLM Analysis

A simple system to track Wyoming bills through their legislative journey using LLM analysis. This tool summarizes the original bill and tracks changes between versions in a human-readable way.

## 🎯 What It Does

1. **📋 Summarizes the Original Bill**: Creates a comprehensive summary of what the bill does
2. **🔄 Tracks Version Changes**: Compares each version to the previous one
3. **📊 Creates Human-Readable Reports**: Generates easy-to-understand summaries
4. **📈 Shows Bill Evolution**: Tracks how the bill changed over time

## 💰 Cost Analysis

**For Wyoming Dataset (8 versions per bill):**

- **Per bill**: ~$0.004 (very affordable!)
- **100 bills**: ~$0.40
- **1,000 bills**: ~$4.00

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Install required packages
pip install pdfplumber click requests
```

### 2. Set Up API Key (Optional)

```bash
# Set your OpenAI API key for real LLM analysis
export OPENAI_API_KEY="your-api-key-here"
```

### 3. Run the Analysis

```bash
# Basic analysis
python openstates_scraped_data_formatter/cli_bill_tracker.py analyze

# With human-readable summary
python openstates_scraped_data_formatter/cli_bill_tracker.py analyze --show-summary

# With verbose output
python openstates_scraped_data_formatter/cli_bill_tracker.py analyze --show-summary --verbose
```

### 4. View Reports

```bash
# View a saved report
python openstates_scraped_data_formatter/cli_bill_tracker.py show-report bill_tracker_report.json
```

## 📁 File Structure

```
openstates_scraped_data_formatter/
├── utils/
│   └── simple_llm_agent.py          # LLM agent for analysis
├── wyoming_bill_tracker.py          # Main tracking system
├── cli_bill_tracker.py              # Command-line interface
└── test_wyoming_llm_analysis.py     # Test script

sample_data/wy_sample/
├── metadata_wy_SAMPLE.json          # Bill metadata
├── HB0011_v1.pdf                    # Version 1 (Introduced)
├── HB0011_v2.pdf                    # Version 2 (Amendment)
├── HB0011_v3.pdf                    # Version 3 (Amendment)
└── ...                              # More versions
```

## 🔧 CLI Options

### Analyze Command

```bash
python cli_bill_tracker.py analyze [OPTIONS]

Options:
  -m, --metadata TEXT    Path to bill metadata JSON file
  -p, --pdf-dir TEXT     Directory containing PDF versions
  -o, --output TEXT      Output file for the report
  -k, --api-key TEXT     OpenAI API key
  -s, --show-summary     Show human-readable summary in terminal
  -v, --verbose          Show detailed progress information
```

### Show Report Command

```bash
python cli_bill_tracker.py show-report [REPORT_FILE]
```

## 📊 Output Format

The system generates a comprehensive JSON report with:

### Bill Tracker Info

- Bill identifier and session
- Total number of versions
- Analysis timestamp
- LLM model used

### Original Summary

- Bill title and sponsors
- Executive summary
- Key provisions
- Quality assessment

### Version Changes

- Changes between each version
- Human-readable summaries
- LLM analysis results
- Impact assessment

### Bill Evolution

- Overall evolution summary
- Key changes over time
- Legislative significance

## 🧠 LLM Features

### Current Capabilities

- **Content Analysis**: Understands bill content and structure
- **Version Comparison**: Identifies changes between versions
- **Strikethrough Detection**: Finds deleted or modified text
- **Impact Assessment**: Evaluates significance of changes

### Future Enhancements

- **Duplicate Detection**: Find similar content across versions
- **Amendment Classification**: Categorize types of changes
- **Quality Filtering**: Only keep high-quality extractions
- **Stakeholder Analysis**: Identify affected parties

## 💡 Example Usage

### Basic Analysis

```bash
# Run analysis on Wyoming sample data
python cli_bill_tracker.py analyze --show-summary
```

### Custom Data

```bash
# Use your own bill data
python cli_bill_tracker.py analyze \
  --metadata path/to/your/metadata.json \
  --pdf-dir path/to/your/pdfs \
  --output my_bill_report.json \
  --show-summary
```

### View Results

```bash
# View the generated report
python cli_bill_tracker.py show-report my_bill_report.json
```

## 🔍 Sample Output

```
📋 BILL TRACKER SUMMARY
============================================================
📄 Bill: HB0011
📝 Title: Manufacturing sales and use tax exemption-amendments.
🏛️ Session: 2025
👥 Sponsors: Minerals, Business and Economic Development

📋 Executive Summary:
   This bill addresses taxation, manufacturing, and exemptions

🔑 Key Provisions:
   • taxation
   • manufacturing
   • exemptions

🔄 Version Changes (7 total):
   • v1_to_v2: Amendment HB0011H2001 (2nd reading) - Representative Styvar (Failed)
   • v2_to_v3: Amendment HB0011H3001 (3rd reading) - Representative Davis (Failed)
   • v3_to_v4: Version 4
   • v4_to_v5: Version 5
   • v5_to_v6: Version 6
   • v6_to_v7: Version 7
   • v7_to_v8: Version 8
```

## 🛠️ Development

### Adding New Features

1. **Extend the LLM Agent**: Add new analysis methods to `simple_llm_agent.py`
2. **Enhance the Tracker**: Add new tracking capabilities to `wyoming_bill_tracker.py`
3. **Update the CLI**: Add new commands to `cli_bill_tracker.py`

### Testing

```bash
# Test the LLM agent
python openstates_scraped_data_formatter/utils/simple_llm_agent.py

# Test with Wyoming data
python openstates_scraped_data_formatter/test_wyoming_llm_analysis.py
```

## 🤝 Contributing

This is a starting point for LLM-powered legislative analysis. Feel free to:

1. **Add new analysis features**
2. **Improve the prompts**
3. **Support more states**
4. **Enhance the reporting**

## 📞 Support

If you have questions or want to extend this system:

- The code is well-documented and easy to understand
- Start with the simple examples
- Build up complexity gradually
- Test with real API keys for best results

---

**Happy Bill Tracking!** 🏛️📊
