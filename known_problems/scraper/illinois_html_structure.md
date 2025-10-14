# Illinois (IL) - HTML Structure Changed

**Status:** 🔴 Failing
**Date Reported:** October 14, 2025
**Category:** Scraper Issue (Upstream)
**Error Type:** `IndexError: list index out of range`

## Problem

The Illinois General Assembly website changed their HTML structure, breaking the OpenStates scraper's XPath selector for extracting bill titles.

## Error Details

```
Traceback (most recent call last):
  File "/opt/openstates/openstates/scrapers/il/bills.py", line 495, in scrape_bill
    title = doc.xpath('//div[@id="content"]/div[1]/div/h5/text()')[0].strip()
IndexError: list index out of range
```

**What it's looking for:** `<h5>` tag at path `//div[@id="content"]/div[1]/div/h5/text()`
**What's happening:** Element not found (HTML structure changed on Illinois website)

## Impact

- ❌ Scraper crashes immediately when trying to scrape first bill (HB1)
- ❌ Gets 0 usable bills (only jurisdiction/organization metadata)
- ❌ Cannot process any Illinois legislative data

## Scraper Behavior

```
✅ save jurisdiction Illinois as jurisdiction_ocd-jurisdiction-country:us-state:il-government.json
✅ save organization Illinois General Assembly as organization_[id].json
✅ save organization Senate as organization_[id].json
✅ save organization House as organization_[id].json
⚠️ WARNING openstates: no session provided, using active sessions: {'104th'}
✅ GET - 'https://ilga.gov/Legislation/RegularSession/HB?SessionId=114'
✅ GET - 'https://ilga.gov/Legislation/BillStatus?DocNum=1&GAID=18&DocTypeID=HB&LegId=156928&SessionID=114'
❌ CRASH - IndexError: list index out of range
```

## Root Cause

Illinois legislature updated their website HTML structure, and the OpenStates scraper's XPath selector is now outdated.

## Workaround

- Use cached/nightly artifact: `use-scrape-cache: true`
- Skip Illinois until OpenStates updates the scraper
- Wait for upstream fix

## Upstream Information

- **Repository:** https://github.com/openstates/openstates-scrapers
- **File:** `scrapers/il/bills.py`
- **Line:** 495
- **Fix Needed:** Update XPath selector to match new HTML structure

## Notes

The scraper does manage to save 4 JSON files (jurisdiction + 3 organizations), but these are not useful without the actual bill data.

---

**Last Updated:** October 14, 2025
