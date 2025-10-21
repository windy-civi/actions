#!/bin/bash

# Quick test script for incremental processing
# Tests the formatter with a single bill

set -e

echo "🧪 Testing Incremental Processing - Phase 1"
echo "=========================================="
echo ""

# Setup
TEST_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$TEST_DIR/../.." && pwd)"  # Go up 2 levels: incremental/ -> testing/ -> project root
INPUT_DIR="$TEST_DIR/test_input"
OUTPUT_DIR="$TEST_DIR/test_output"

echo "📁 Test directories:"
echo "   Input:  $INPUT_DIR"
echo "   Output: $OUTPUT_DIR"
echo ""

# Check if we have input files
BILL_COUNT=$(find "$INPUT_DIR" -name "bill_*.json" 2>/dev/null | wc -l | tr -d ' ')
echo "📊 Found $BILL_COUNT bill(s) to process"
echo ""

if [ "$BILL_COUNT" -eq 0 ]; then
    echo "❌ No bill files found in $INPUT_DIR"
    echo "   Please add bill_*.json files to test with"
    exit 1
fi

# Run the formatter
echo "🚀 Running formatter..."
cd "$PROJECT_ROOT"

pipenv run python scrape_and_format/main.py \
    --state usa \
    --openstates-data-folder "$INPUT_DIR" \
    --git-repo-folder "$OUTPUT_DIR"

echo ""
echo "✅ Test complete!"
echo ""
echo "📂 Check results in: $OUTPUT_DIR/data_output/data_processed/"


