# 📋 Incremental Processing Implementation Plan

## 🎯 Project Goal

Replace the current repository-level timestamp tracking with bill-level and action-level tracking to enable true incremental processing. This will prevent reprocessing existing data and preserve processing timestamps.

---

## 🚨 Current Problems

### **Main Problem: Actions Skipped Due to Repository-Level Timestamps**

**Core Issue**: New actions get filtered out and never processed if they have timestamps older than the repository's "latest" timestamp.

**Example Scenario:**

```
Night 1: Repository has actions with newest timestamp: 2025-10-10
Night 2: New action comes in with timestamp: 2025-10-09 (older than 2025-10-10)
Result: New action gets filtered out and NEVER gets processed
```

### **Current Timestamp System:**

```json
{
  "bills": "2025-10-10T04:00:00",
  "vote_events": "2025-10-09T16:25:00",
  "events": "1900-01-01T00:00:00"
}
```

### **Why This Happens:**

- **Repository-level timestamps** track the **newest** action across the entire repository
- **New actions with older timestamps** get filtered out by `is_newer_than_latest()`
- **Government websites** sometimes backdate actions or have data corrections
- **Session overlaps** can cause timestamp ordering issues

### **Secondary Issues:**

- **Flaw 2**: Any new bill triggers reprocessing of ALL bills in repository
- **Flaw 3**: Single timestamp per data type covers entire repository

---

## 💡 Solution: Hybrid Approach

To solve the problems above while maintaining efficiency, we're implementing a **hybrid filtering and processing approach**:

### **Stage 1: Smart Filtering (Early Filter)**

In `load_json_files()`, we perform a quick count-based comparison:

1. **Load existing metadata** for each incoming bill
2. **Compare action counts**:
   - If counts are **equal** → Skip (likely no changes)
   - If counts are **different** → Pass to processing (has changes)
3. **Filter out 90%+ of unchanged bills** early in the pipeline

### **Stage 2: Action-Level Processing (Granular Processing)**

In `handle_bill()`, we process only new actions:

1. **Compare actions** using "description + date" identifier
2. **Identify new actions** that don't exist in existing metadata
3. **Process only new actions** (write logs, add `_processing` timestamps)
4. **Preserve existing actions** with their `_processing` timestamps
5. **Merge and save** complete metadata

### **Benefits:**

- ✅ **Efficient filtering**: Most unchanged bills are filtered early
- ✅ **No data loss**: Bills with new actions always get through
- ✅ **Granular processing**: Only new actions are processed
- ✅ **Preserve history**: Existing timestamps are never modified
- ✅ **Handles edge cases**: Backdated actions, corrections, session overlaps

---

## 📊 New Data Structure

### **Metadata Structure with Processing Timestamps:**

```json
{
  "legislative_session": "119",
  "identifier": "HR 1",
  "_processing": {
    "logs_latest_update": "2025-10-14T01:30:00Z",
    "extraction_latest_update": "2025-10-14T02:15:00Z"
  },
  "actions": [
    {
      "description": "Became Public Law No: 119-21.",
      "date": "2025-07-04T04:00:00+00:00",
      "organization_id": "~{\"classification\": \"executive\"}",
      "classification": ["became-law"],
      "related_entities": [],
      "_processing": {
        "log_file_created": "2025-10-14T01:30:00Z",
        "text_extracted": "2025-10-14T02:15:00Z"
      }
    }
  ]
}
```

### **Two-Level Timestamp Tracking:**

**Bill-Level `_processing`:**

- `logs_latest_update` - When this bill's logs were last processed/created
- `extraction_latest_update` - When this bill's text was last extracted

**Action-Level `_processing`:**

- `log_file_created` - When the log file was created for this specific action
- `text_extracted` - When text was extracted for this specific action

**Why Both Levels?**

- **Bill-level timestamps** = Fast filtering (skip entire bills that don't need processing)
- **Action-level timestamps** = Granular processing (only process new actions within a bill)

### **Action Comparison Logic:**

```python
def create_action_identifier(action):
    return f"{action['description']}|{action['date']}"

def find_new_actions(existing_actions, incoming_actions):
    existing_ids = {create_action_identifier(action) for action in existing_actions}
    incoming_ids = {create_action_identifier(action) for action in incoming_actions}
    new_ids = incoming_ids - existing_ids
    return [action for action in incoming_actions
            if create_action_identifier(action) in new_ids]
```

---

## 🔄 New Processing Flow (Hybrid Approach)

### **Step 1: Load and Filter (`load_json_files_hybrid()`)**

```python
def load_json_files_hybrid(openstates_folder, data_processed_folder, ...):
    for file in openstates_folder:
        if file.startswith("bill"):
            data = load_json(file)
            bill_id = extract_bill_identifier(data)

            # Load existing metadata if it exists
            existing_metadata = load_existing_metadata(data_processed_folder, bill_id)

            if existing_metadata:
                # Compare action counts
                incoming_count = len(data.get("actions", []))
                existing_count = len(existing_metadata.get("actions", []))

                if incoming_count == existing_count:
                    # No changes, skip this bill
                    continue

            # Either new bill OR has different action count → process it
            all_json_files.append(data)
```

**Key Points:**

- ✅ Early filtering based on action count
- ✅ Most bills (90%+) with no changes are filtered here
- ✅ Bills with new/removed actions pass through
- ✅ New bills always pass through

---

### **Step 2: Process Actions (`handle_bill_hybrid()`)**

```python
def handle_bill_hybrid(data, save_path, ...):
    # Load existing metadata
    metadata_file = save_path / "metadata.json"
    existing_metadata = load_json(metadata_file) if metadata_file.exists() else None

    if existing_metadata:
        # Compare actions to find new ones
        existing_actions = existing_metadata.get("actions", [])
        incoming_actions = data.get("actions", [])

        new_actions = find_new_actions(existing_actions, incoming_actions)

        # Only process new actions
        if new_actions:
            write_action_logs(new_actions, bill_identifier, save_path / "logs")
            add_processing_timestamps(new_actions, "log_file_created")

            # Update bill-level timestamp
            data["_processing"]["logs_latest_update"] = get_current_timestamp()

        # Merge: preserve existing actions with their _processing fields
        merged_actions = merge_actions(existing_actions, incoming_actions)
        data["actions"] = merged_actions

        # Preserve existing bill-level timestamps
        if "_processing" in existing_metadata:
            data["_processing"] = {**existing_metadata["_processing"], **data.get("_processing", {})}
    else:
        # New bill: process all actions
        write_action_logs(data["actions"], bill_identifier, save_path / "logs")
        add_processing_timestamps(data["actions"], "log_file_created")

        # Set initial bill-level timestamp
        data["_processing"] = {"logs_latest_update": get_current_timestamp()}

    # Save complete metadata
    save_json(metadata_file, data)
```

**Key Points:**

- ✅ Only new actions are processed (logs written)
- ✅ Existing actions keep their `_processing` timestamps
- ✅ New actions get `log_file_created` timestamp
- ✅ Bill-level `logs_latest_update` timestamp is set/updated
- ✅ Existing bill-level timestamps are preserved
- ✅ Complete metadata (all actions) is saved

---

### **Step 3: Text Extraction (`extract_text_hybrid()`)**

```python
def extract_text_hybrid(data_processed_folder, ...):
    for bill_folder in data_processed_folder:
        metadata = load_json(bill_folder / "metadata.json")

        # Quick filter: skip if extracted recently (within last 24 hours)
        extraction_updated = metadata.get("_processing", {}).get("extraction_latest_update")
        if extraction_updated and is_recent(extraction_updated, hours=24):
            continue  # Skip this entire bill

        needs_update = False

        for action in metadata.get("actions", []):
            # Only process actions that need text extraction
            if "_processing" not in action:
                continue  # Not processed yet (no log file)

            if "text_extracted" in action["_processing"]:
                continue  # Already extracted

            # Extract text for this action
            try:
                extract_text_for_action(action, bill_folder)
                action["_processing"]["text_extracted"] = get_current_timestamp()
                needs_update = True
            except Exception as e:
                log_error(f"Failed to extract text: {e}")
                # Don't add timestamp - will retry next night

        # Update bill-level timestamp if we processed any actions
        if needs_update:
            if "_processing" not in metadata:
                metadata["_processing"] = {}
            metadata["_processing"]["extraction_latest_update"] = get_current_timestamp()

            # Save updated metadata
            save_json(bill_folder / "metadata.json", metadata)
```

**Key Points:**

- ✅ Fast filtering using bill-level `extraction_latest_update` timestamp
- ✅ Only actions with `log_file_created` (but not `text_extracted`) are processed
- ✅ Existing text extraction timestamps are preserved
- ✅ New actions get `text_extracted` timestamp
- ✅ Bill-level `extraction_latest_update` timestamp is set/updated
- ✅ Error handling: failed extractions will retry next night
- ✅ Metadata is updated incrementally

---

## 🚀 Implementation Phases

### **Phase 1: Implement Hybrid Filtering System**

- [ ] **1.1** Modify `load_json_files()` to use smart filtering
- [ ] **1.2** Add function to load existing metadata for comparison
- [ ] **1.3** Implement action count comparison logic
- [ ] **1.4** Add `_processing` fields to metadata structure

**Files to modify:**

- `scrape_and_format/utils/io_utils.py`
- `scrape_and_format/utils/file_utils.py`

**Key Changes:**

- Replace repository-level timestamp filtering with count-based filtering
- Load existing metadata to compare action counts
- Skip bills with same action count (likely no changes)
- Process bills with different action counts (has changes)

---

### **Phase 2: Action-Level Processing**

- [ ] **2.1** Create action comparison utility functions
- [ ] **2.2** Implement "description + date" action identification
- [ ] **2.3** Update action processing to only handle new actions
- [ ] **2.4** Preserve existing action `_processing` timestamps

**Files to modify:**

- `scrape_and_format/handlers/bill.py`
- Create new utility: `scrape_and_format/utils/action_utils.py`

**Key Changes:**

- Add action comparison logic
- Only process new actions (not existing ones)
- Preserve existing `_processing` timestamps

---

### **Phase 3: Metadata Processing Updates**

- [ ] **3.1** Update `bill.py` handler to use hybrid processing
- [ ] **3.2** Modify metadata writing to preserve `_processing` fields
- [ ] **3.3** Update bill processing to merge existing and new actions
- [ ] **3.4** Add migration logic for existing bills

**Files to modify:**

- `scrape_and_format/handlers/bill.py`
- `scrape_and_format/utils/file_utils.py`

**Key Changes:**

- Update `handle_bill()` to use hybrid processing approach
- Merge existing metadata with new data
- Preserve all `_processing` fields

---

### **Phase 4: Text Extraction Integration**

- [ ] **4.1** Update text extraction to use action-level timestamps
- [ ] **4.2** Add `text_extracted` timestamp to action `_processing`
- [ ] **4.3** Update text extraction to only process new actions
- [ ] **4.4** Preserve existing text extraction timestamps

**Files to modify:**

- `text_extraction/main.py` (or equivalent)
- Text extraction utilities

**Key Changes:**

- Check action-level text extraction timestamps
- Only extract text for actions without `text_extracted` timestamp
- Preserve existing text extraction timestamps

---

### **Phase 5: Testing & Validation**

- [ ] **5.1** Test with sample data (HR1, HR1912)
- [ ] **5.2** Verify timestamp preservation
- [ ] **5.3** Test incremental processing scenarios
- [ ] **5.4** Validate error handling and recovery

**Test Scenarios:**

1. **New bill processing** - Should add `_processing` fields
2. **Existing bill with new actions** - Should only process new actions
3. **Existing bill with no changes** - Should skip processing entirely
4. **Text extraction** - Should only extract text for new actions

---

### **Phase 6: Documentation & Cleanup**

- [ ] **6.1** Update README with new processing logic
- [ ] **6.2** Document migration process
- [ ] **6.3** Update error handling documentation
- [ ] **6.4** Clean up old timestamp files

**Files to update:**

- `README.md`
- `project_docs/`
- Remove old `latest_timestamps.json` files

---

## 🔧 Implementation Details

### **Key Functions to Implement:**

1. **`load_existing_metadata(data_processed_folder, bill_id)`**

   - Load existing metadata.json for a bill (if it exists)
   - Return None if bill is new

2. **`create_action_identifier(action)`**

   - Create unique identifier: `description|date`
   - Used for comparing actions

3. **`find_new_actions(existing_actions, incoming_actions)`**

   - Compare action lists using identifiers
   - Return only actions that don't exist in existing metadata

4. **`merge_actions(existing_actions, incoming_actions)`**

   - Preserve `_processing` fields from existing actions
   - Add new actions to the list
   - Return merged list

5. **`add_processing_timestamps(actions, field_name)`**
   - Add timestamp to action's `_processing` field
   - Used for both `log_file_created` and `text_extracted`

### **Error Handling:**

- **Process twice rather than skip** - If action fails, retry on next run
- **Use existing error system** - Log failures in `data_not_processed/`
- **Continue processing** - Don't let one failed action stop the entire bill

### **Migration Strategy:**

- **Existing bills** - Add `_processing` fields on first processing
- **New bills** - Start with `_processing` fields from the beginning
- **Backward compatibility** - Handle bills without `_processing` fields gracefully

---

## 📈 Success Metrics

### **Efficiency Gains:**

- ✅ **Only process new data** - No unnecessary reprocessing
- ✅ **Preserve processing history** - Never lose timestamp information
- ✅ **Faster processing** - Skip existing bills/actions
- ✅ **Reliable incremental updates** - Handle any timestamp scenario

### **Data Integrity:**

- ✅ **Immutable processing logs** - Once written, never modified
- ✅ **Complete audit trail** - Track when each action was processed
- ✅ **Error recovery** - Retry failed actions without losing progress

---

## 🎯 Next Steps

1. **Start with Phase 1** - Implement hybrid filtering system
2. **Create GitHub issues** for each phase/task
3. **Test incrementally** - Validate each phase with sample data before moving to next
4. **Document changes** - Update docs as we implement

### **Recommended Implementation Order:**

1. **Phase 1** - Hybrid filtering (most impact, reduces unnecessary processing)
2. **Phase 2** - Action-level processing (core logic)
3. **Phase 3** - Metadata processing updates (complete the flow)
4. **Phase 4** - Text extraction integration (extend to text extraction)
5. **Phase 5** - Testing & validation (ensure everything works)
6. **Phase 6** - Documentation & cleanup (finalize)

---

## 📝 Notes

- **Branch**: `incremental-processing`
- **Sample Data**: 188 bills in `sample_data/USA_sample_data/usa-data-pipeline/`
- **Test Bills**: HR1, HR1912, HJRES24 (good examples for testing)
- **Missing Bills**: S, SJRES bills not in new dataset (will retry scraping tonight)

---

**Last Updated**: October 16, 2025
**Branch**: `incremental-processing`
**Status**: Planning complete, ready to begin Phase 1 implementation
