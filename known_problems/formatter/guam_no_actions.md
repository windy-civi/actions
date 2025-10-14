# Guam (GU) - Bills Have No Actions Array

**Status:** 🟡 Partial Success (Scraper works, Formatter rejects)
**Date Reported:** October 14, 2025
**Category:** Formatter Issue (Our Code)
**Error Type:** `NO_ACTIONS_FOUND`

## Problem

Guam bills scrape successfully but are rejected by our formatter because they have empty `actions` arrays. Our formatter requires actions to determine bill timestamps, but Guam bills don't have this data.

## Error Details

```
⚠️ Skipping item in bills — invalid timestamp: NO_ACTIONS_FOUND
📄 Saved error file to: /home/runner/work/gu-data-pipeline/gu-data-pipeline/data_output/data_not_processed/from_is_newer_than_latest_no_actions_found/unknown.json
```

This error repeats **100 times** (once for each bill).

## Impact

**Scraper:**

- ✅ Successfully scrapes 100 bills
- ✅ Creates 102 JSON files (100 bills + 2 organization files)
- ✅ Uploads artifact successfully

**Formatter:**

- ❌ Rejects all 100 bills due to missing actions
- ❌ Final output: 0 bills processed
- ❌ All bills saved to `data_not_processed/`

## Bill Structure

Guam bills have valid data but no actions:

```json
{
  "identifier": "B 100-38",
  "title": "AN ACT TO...",
  "legislative_session": "38th",
  "actions": [],           ❌ Empty!
  "sponsorships": [...],   ✅ Has data
  "versions": [...],       ✅ Has PDF links!
  "scraped_at": "2025-10-14T00:45:05+00:00"  ✅ Has timestamp!
}
```

## Root Cause

**Our formatter logic:**

1. Checks `actions` array for timestamps
2. If empty → marks as `NO_ACTIONS_FOUND`
3. Rejects the bill (can't determine when it was updated)

**Why Guam has no actions:**

- Guam's legislature may not track actions the same way
- OpenStates scraper for Guam doesn't capture actions
- Actions might be recorded differently in Guam's system

## Potential Solutions

### Option 1: Use `scraped_at` as Fallback

Modify formatter to use `scraped_at` timestamp when actions array is empty.

**Pros:**

- ✅ All Guam bills would be processed
- ✅ Still have a valid timestamp
- ✅ Bills get saved to output

**Cons:**

- ⚠️ Less accurate timestamp (when scraped vs. when introduced)
- ⚠️ All bills would have same timestamp

### Option 2: Use Session Start Date

Use the legislative session's start date as the bill timestamp.

**Pros:**

- ✅ More accurate than scraped_at
- ✅ All bills in session share logical timestamp

**Cons:**

- ⚠️ Requires session metadata
- ⚠️ Still not as accurate as real action dates

### Option 3: Accept Bills Without Timestamps

Allow bills with no actions and use a default timestamp (1900-01-01).

**Pros:**

- ✅ Simplest solution
- ✅ Bills still get processed and saved

**Cons:**

- ❌ Later analysis may need timestamps
- ❌ Can't track bill progression

## Recommendation

**Use scraped_at as fallback** - This gives us real data to work with while maintaining some temporal information.

## Code Location

**File:** `scrape_and_format/main.py` or related handler
**Logic:** Action timestamp extraction
**Change Needed:** Add fallback to use `scraped_at` when `actions` is empty

---

**Last Updated:** October 14, 2025
