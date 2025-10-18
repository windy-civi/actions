# 📊 Bill Processing Flow Chart

## Current Bill Processing Pipeline

```
📁 Scraped Data (OpenStates)
    ↓
🔍 main.py
    ↓
📖 read_latest_timestamps() → Load repository-level timestamps
    ↓
📂 load_json_files()
    ↓
🔍 For each bill_*.json file:
    ↓
⚠️  is_newer_than_latest(data, bills_ts, "bills")
    ↓ (if TRUE)
📋 process_and_save()
    ↓
🔀 route_handler() → bill.handle_bill()
    ↓
📝 handle_bill():
    ├── Validate bill identifier
    ├── Create bill folder structure
    ├── Process actions:
    │   ├── Extract dates from actions
    │   ├── Update latest_timestamps["bills"]
    │   └── write_action_logs() → Create individual action JSON files
    ├── Save metadata.json (complete bill data)
    └── Return success/failure
    ↓
📊 Update counts and write_latest_timestamp_file()
```

## 🚨 Critical Points Where Repository-Level Timestamps Cause Issues

### **1. Filtering Stage (`load_json_files`)**

```python
# Current problematic logic:
if filename.startswith("bill"):
    if not is_newer_than_latest(data, bills_ts, "bills", DATA_NOT_PROCESSED_FOLDER):
        continue  # ❌ BILL GETS SKIPPED FOREVER
```

**Problem**: If a bill has actions older than `bills_ts`, the entire bill gets filtered out.

### **2. Timestamp Update (`handle_bill`)**

```python
# Current logic updates repository-level timestamp:
dates = [a.get("date") for a in actions if a.get("date")]
timestamp = format_timestamp(sorted(dates)[0])  # Oldest action date
latest_timestamps["bills"] = update_latest_timestamp(
    "bills", current_dt, latest_timestamps["bills"], latest_timestamps
)
```

**Problem**: Updates repository timestamp to oldest action, not newest.

### **3. Action Processing (`write_action_logs`)**

```python
# Current logic processes ALL actions every time:
write_action_logs(actions, bill_identifier, save_path / "logs")
```

**Problem**: Recreates all action log files, even if they already exist.

---

## 🎯 Where to Implement Action-Level Tracking

### **Stage 1: Replace Repository-Level Filtering**

**Location**: `load_json_files()` in `io_utils.py`
**Current**: Filter entire bill based on repository timestamp
**New**: Load all bills, let bill handler decide what to process

### **Stage 2: Add Action-Level Comparison**

**Location**: `handle_bill()` in `bill.py`
**Current**: Process all actions every time
**New**: Compare incoming actions with existing metadata, process only new actions

### **Stage 3: Preserve Processing Timestamps**

**Location**: `write_action_logs()` in `file_utils.py`
**Current**: Create new action files every time
**New**: Only create files for new actions, preserve existing ones

### **Stage 4: Update Metadata with Processing Info**

**Location**: `handle_bill()` in `bill.py`
**Current**: Save raw metadata.json
**New**: Add `_processing` fields to actions before saving

---

## 🔄 New Processing Flow (Hybrid Approach)

```
📁 Scraped Data (OpenStates)
    ↓
🔍 main.py
    ↓
📖 read_latest_timestamps() → Load repository-level timestamps (for migration)
    ↓
📂 load_json_files_hybrid() [SMART FILTERING]:
    ├── For each bill_*.json file:
    ├── Load existing metadata.json (if exists)
    ├── Compare action counts:
    │   ├── Same count → Skip bill (likely no changes)
    │   ├── Higher count → Process bill (new actions)
    │   └── Lower count → Process bill (handle deletions)
    └── Only pass bills with changes to processing
    ↓
📋 process_and_save()
    ↓
🔀 route_handler() → bill.handle_bill()
    ↓
📝 handle_bill_hybrid() [ACTION-LEVEL PROCESSING]:
    ├── Load existing metadata.json (if exists)
    ├── Find new actions (count difference):
    │   ├── new_actions_count = incoming_count - existing_count
    │   ├── new_actions = incoming_actions[-new_actions_count:]
    │   └── Only process new actions
    ├── write_action_logs() → Create files only for new actions
    ├── Add _processing fields to new actions:
    │   ├── "log_file_created": timestamp
    │   └── "text_extracted": null (for text extraction)
    ├── Merge metadata:
    │   ├── Keep existing actions with _processing fields
    │   ├── Add new actions with new _processing fields
    │   └── Save updated metadata.json
    └── Return success/failure
    ↓
📊 Update counts (no timestamp file updates needed)
```

## 🛠️ Implementation Strategy

### **Phase 1: Modify `load_json_files()`**

- Remove repository-level timestamp filtering for bills
- Load all bill files regardless of timestamp

### **Phase 2: Update `handle_bill()`**

- Load existing metadata.json if it exists
- Implement action comparison logic
- Only process new actions
- Preserve existing `_processing` fields

### **Phase 3: Update `write_action_logs()`**

- Check if action log file already exists
- Only create files for new actions
- Preserve existing action log files

### **Phase 4: Add `_processing` Fields**

- Add `_processing` field to new actions
- Include `log_file_created` and `text_extracted` timestamps
- Merge with existing metadata before saving

---

## 📊 Benefits of New Approach

✅ **No more skipped bills** - All bills get processed
✅ **No unnecessary reprocessing** - Only new actions get processed
✅ **Preserve processing history** - Never lose timestamp information
✅ **Faster processing** - Skip existing actions
✅ **Reliable incremental updates** - Handle any timestamp scenario

---

## 🔗 Text Extraction Integration

### **Current Text Extraction Flow:**

```
📁 Processed Bills (with metadata.json)
    ↓
🔍 text_extraction/main.py
    ↓
📂 Scan all bills for text extraction
    ↓
📄 For each bill:
    ├── Download PDFs/XMLs from action URLs
    ├── Extract text using pdfplumber/PyPDF2
    ├── Save extracted text files
    └── Update metadata with text extraction timestamps
```

### **New Text Extraction Flow (Incremental):**

```
📁 Processed Bills (with _processing fields)
    ↓
🔍 text_extraction/main.py
    ↓
📂 Scan bills for actions needing text extraction
    ↓
📄 For each bill:
    ├── Load existing metadata.json
    ├── Find actions where text_extracted is null
    ├── Download PDFs/XMLs for new actions only
    ├── Extract text using pdfplumber/PyPDF2
    ├── Save extracted text files
    ├── Update action _processing.text_extracted timestamp
    └── Save updated metadata.json
```

### **Text Extraction Integration Points:**

#### **1. Two-Level Text Extraction Tracking**

```json
{
  "_processing": {
    "logs_latest_update": "2025-10-14T01:30:00Z",
    "extraction_latest_update": "2025-10-14T02:15:00Z" // ← Bill-level timestamp
  },
  "actions": [
    {
      "description": "Became Public Law No: 119-21.",
      "date": "2025-07-04T04:00:00+00:00",
      "_processing": {
        "log_file_created": "2025-10-14T01:30:00Z",
        "text_extracted": "2025-10-14T02:15:00Z" // ← Action-level timestamp
      }
    }
  ]
}
```

**Bill-Level `_processing`:**

- `logs_latest_update` - When logs were last created for this bill
- `extraction_latest_update` - When text was last extracted for this bill
- **Purpose**: Fast filtering to skip bills that don't need processing

**Action-Level `_processing`:**

- `log_file_created` - When the log file was created for this action
- `text_extracted` - When text was extracted for this action
- **Purpose**: Granular tracking of which actions have been processed

#### **2. Text Extraction Logic (with Fast Filtering)**

```python
def process_bill_text_extraction(bill_path):
    metadata = load_metadata(bill_path / "metadata.json")

    # Quick filter: skip if extracted recently (within last 24 hours)
    extraction_updated = metadata.get("_processing", {}).get("extraction_latest_update")
    if extraction_updated and is_recent(extraction_updated, hours=24):
        return  # Skip this entire bill

    needs_update = False

    for action in metadata.get("actions", []):
        # Check if text extraction is needed
        processing = action.get("_processing", {})
        if not processing.get("text_extracted"):
            # Extract text for this action
            try:
                extract_action_text(action)
                # Update action-level timestamp
                processing["text_extracted"] = datetime.now().isoformat() + "Z"
                needs_update = True
            except Exception as e:
                log_error(f"Failed to extract text: {e}")
                # Don't add timestamp - will retry next night

    # Update bill-level timestamp if we processed any actions
    if needs_update:
        if "_processing" not in metadata:
            metadata["_processing"] = {}
        metadata["_processing"]["extraction_latest_update"] = datetime.now().isoformat() + "Z"

        # Save updated metadata
        save_metadata(metadata)
```

#### **3. Benefits for Text Extraction:**

- ✅ **Fast filtering** - Bill-level timestamp skips entire bills that don't need processing
- ✅ **Only extract text for new actions** - Skip existing ones
- ✅ **Preserve extraction history** - Never lose text extraction timestamps
- ✅ **Faster text extraction** - Skip actions already processed
- ✅ **Reliable incremental updates** - Handle any text extraction scenario
- ✅ **Error recovery** - Failed extractions automatically retry next night
- ✅ **Independent workflows** - Each workflow tracks its own progress

---

**Last Updated**: October 16, 2025
**Branch**: `incremental-processing`
