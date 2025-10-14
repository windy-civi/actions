# Guam (GU) - Scraper Not Extracting Dates or Actions

**Status:** 🔴 Failing  
**Date Reported:** October 14, 2025  
**Category:** Scraper Issue (Upstream)  
**Error Type:** Missing data extraction  
**Website:** https://guamlegislature.gov/bills-page1/

## Problem

The Guam scraper successfully retrieves bills but **fails to extract** introduction dates and legislative actions, even though this data is clearly available on the Guam legislature website.

## What the Website Has

From [Guam Legislature Bills Page](https://guamlegislature.gov/bills-page1/):

```
Bill No. 100-38 (COR)
Sponsor: Sabina Flores Perez (Introduced: 4/2/25)  ← Date is here!

Actions:
- Referral (PDF link)
- Fiscal Note Request (PDF link)  ← Actions are here!
- Fiscal Note (PDF link)
- Committee Report (PDF link)
- Transmittal (PDF link)
```

## What the Scraper Extracts

```json
{
  "identifier": "B 100-38",
  "title": "AN ACT TO...",
  "legislative_session": "38th",
  "actions": [],           ❌ Empty! (Should have Referral, Fiscal Note, etc.)
  "sponsorships": [...],   ✅ Correctly extracted
  "versions": [{
    "date": "",            ❌ Empty! (Should be "4/2/25")
  }],
  "scraped_at": "2025-10-14T00:45:05+00:00"
}
```

## Impact

**On Scraping:**

- ✅ Scraper runs successfully
- ✅ Gets 100 bills
- ✅ Extracts titles, sponsors, version PDF links
- ❌ Misses introduction dates
- ❌ Misses all legislative actions

**On Formatting:**

- ❌ Our formatter rejects all 100 bills
- ❌ Reason: No actions array → can't determine timestamp
- ❌ All bills saved to `data_not_processed/`
- ❌ Final output: 0 bills

## Downstream Effect

```
⚠️ Skipping item in bills — invalid timestamp: NO_ACTIONS_FOUND
```

This error repeats 100 times because our formatter requires actions to determine when a bill was updated. Without actions, it can't process the bills.

## Root Cause

The OpenStates Guam scraper is incomplete. It extracts basic bill information but doesn't parse:

1. The "Introduced: X/X/XX" dates from the sponsor line
2. The action links table (Referral, Fiscal Note Request, etc.)

## Potential Solutions

### Option A: Fix OpenStates Scraper (Recommended)

Update the Guam scraper to extract:

- Introduction dates from "Introduced: X/X/XX" text
- Action links and dates from the Actions table

**Upstream Fix Needed:**

- Repository: https://github.com/openstates/openstates-scrapers
- File: `scrapers/gu/bills.py`
- Changes: Add date and action parsing

### Option B: Fix Our Formatter (Workaround)

Modify our formatter to use `scraped_at` timestamp as fallback when `actions` is empty.

**Our Code:**

- File: `scrape_and_format/main.py` (or related handler)
- Change: Add fallback logic for missing actions

**Pros:**

- ✅ Guam bills would be processed
- ✅ Quick fix on our end

**Cons:**

- ⚠️ Less accurate timestamps
- ⚠️ Missing action history

## Recommendation

1. **Short-term:** Fix our formatter to handle missing actions (use `scraped_at`)
2. **Long-term:** Report to OpenStates to improve Guam scraper

This way Guam bills get processed now, and when OpenStates fixes their scraper, we'll automatically get the better data.

---

**Last Updated:** October 14, 2025
**Website Reference:** https://guamlegislature.gov/bills-page1/
