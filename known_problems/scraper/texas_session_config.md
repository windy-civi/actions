# Texas (TX) - 89(2) 2025 Session Not Configured

**Status:** 🔴 Failing
**Date Reported:** October 14, 2025
**Category:** Scraper Issue (Upstream)
**Error Type:** `CommandError: Session not found`

## Problem

Texas started the "89th Legislature, 2nd Called Session (2025)", but the OpenStates scraper configuration hasn't been updated to recognize it yet.

## Error Details

```
openstates.exceptions.CommandError:
Session(s) 89(2) - 2025 were reported by Texas.get_session_list()
but were not found in Texas.legislative_sessions or Texas.ignored_scraped_sessions.
```

## Impact

- ❌ All Texas scraping fails before any bills are scraped
- ❌ Gets 0 JSON files
- ❌ No fallback artifact available
- ❌ Cannot collect any Texas legislative data

## Root Cause

**Timing Issue:**

- Texas called a second special session for their 89th Legislature in 2025
- OpenStates scraper detected it via `get_session_list()`
- But "89(2) - 2025" not yet added to scraper configuration
- There's always a lag when states start new sessions

## Workaround

- Wait for OpenStates to update configuration (usually 1-2 weeks)
- Skip Texas until fixed
- Focus on states with 2024 sessions
- Monitor OpenStates repository for updates

## Upstream Information

- **Repository:** https://github.com/openstates/openstates-scrapers
- **File:** `scrapers/tx/__init__.py`
- **Fix Needed:** Add "89(2) - 2025" to the `legislative_sessions` list

## Timeline Note

This is part of a **January 2025 pattern** where multiple states are starting new sessions faster than OpenStates can update their configurations. Similar issues affecting New Mexico and potentially other states.

Texas is a particularly active state with multiple special sessions, so this type of configuration lag may happen more frequently.

---

**Last Updated:** October 14, 2025
