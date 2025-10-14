# New Mexico (NM) - 2025 1st Special Session Not Configured

**Status:** 🔴 Failing
**Date Reported:** October 14, 2025
**Category:** Scraper Issue (Upstream)
**Error Type:** `CommandError: Session not found`

## Problem

New Mexico called a "2025 1st Special" legislative session, but the OpenStates scraper configuration hasn't been updated to recognize it yet.

## Error Details

```
openstates.exceptions.CommandError:
Session(s) 2025 1st Special were reported by NewMexico.get_session_list()
but were not found in NewMexico.legislative_sessions or NewMexico.ignored_scraped_sessions.
```

## Impact

- ❌ All New Mexico scraping fails before any bills are scraped
- ❌ Gets 0 JSON files
- ❌ No fallback artifact available
- ❌ Cannot collect any New Mexico legislative data

## Root Cause

**Timing Issue:**

- New Mexico started a special legislative session in January 2025
- OpenStates scraper detected it via `get_session_list()`
- But "2025 1st Special" not yet added to scraper configuration
- There's always a lag when states start new sessions

## Workaround

- Wait for OpenStates to update configuration (usually 1-2 weeks)
- Skip New Mexico until fixed
- Monitor OpenStates repository for updates

## Upstream Information

- **Repository:** https://github.com/openstates/openstates-scrapers
- **File:** `scrapers/nm/__init__.py`
- **Fix Needed:** Add "2025 1st Special" to the `legislative_sessions` list

## Timeline Note

This is part of a **January 2025 pattern** where multiple states are starting new sessions faster than OpenStates can update their configurations. Similar issues affecting Texas and potentially other states.

---

**Last Updated:** October 14, 2025
