# Florida (FL) - House Search Selector Broken

**Status:** 🔴 Failing
**Date Reported:** October 23, 2025
**Category:** Scraper Issue (Upstream)
**Error Type:** `Selector Error: could not find bill in House Search`
**Scraper Version:** `openstates/scrapers:latest` (as of Oct 2025)

---

## 🔴 Problem

The Florida scraper fails to extract any bills due to broken selectors on the House of Representatives website (`flhouse.gov`). The scraper runs for the full 6-hour GitHub Actions timeout but saves **zero bills**.

---

## 🔍 Error Details

**Repeated error in logs:**

```
ERROR fl.bills.HouseSearchPage: Selector Error at source
https://flhouse.gov/Sections/Bills/bills.aspx?Chamber=B&SessionId=105&BillNumber=XXX,
could not find bill in House Search
```

**This error repeats for every single bill:**

- HB 667, HB 668, HB 669, HB 670, HB 671... (all House bills)
- Continues for 6 hours
- **Zero "save bill" success messages**

---

## 💥 Impact

### On Scraping:

- ❌ Scraper runs for full 6 hours
- ❌ Processes all bills in the session (600+ bills)
- ❌ **Saves 0 bills** (complete failure)
- ❌ Times out at 6-hour GitHub limit
- ❌ Wastes all compute time

### On Output:

- ❌ No JSON files created (bill count = 0)
- ❌ No usable data for formatter
- ❌ Cannot build Florida data pipeline

---

## 🔬 Scraper Behavior

### What Works:

```
✅ Fetches bill list from flsenate.gov
✅ Gets Senate bill pages (flsenate.gov/Session/Bill/...)
✅ Extracts some metadata (sees bills exist)
✅ Attempts to get House companion information
```

### What Fails:

```
❌ House search page (flhouse.gov/Sections/Bills/bills.aspx)
❌ Selector cannot find bills on search page
❌ Every bill lookup fails → no data extracted
❌ Logs error and continues to next bill (infinite loop of failures)
```

---

## 📊 Log Comparison

### Working Scraper (New Mexico):

```
INFO openstates: save bill SB1 in 2025S1 as bill_xxx.json  ✅
INFO openstates: save bill HB1 in 2025S1 as bill_xxx.json  ✅
INFO openstates: save bill SB2 in 2025S1 as bill_xxx.json  ✅
(Successful saves every few seconds)
```

### Broken Scraper (Florida):

```
INFO fl.bills.BillDetail: fetching https://flsenate.gov/Session/Bill/2025/667/ByCategory
WARNING fl.bills.BillDetail: No chapter law table for HB 667
INFO fl.bills.HouseSearchPage: fetching https://flhouse.gov/Sections/Bills/bills.aspx?...
ERROR fl.bills.HouseSearchPage: Selector Error... could not find bill in House Search  ❌
WARNING fl.bills.BillDetail: No vote table for HB 667
(Repeats for every bill - NO "save bill" messages)
```

**Key indicator:** Absence of `INFO openstates: save bill` messages = scraper is broken.

---

## 🔎 Root Cause

The Florida House of Representatives website (`flhouse.gov`) **changed their HTML structure**, breaking the OpenStates scraper's CSS/XPath selectors for finding bills on the search page.

**Technical details:**

- **Component:** `HouseSearchPage` class in `scrapers/fl/bills.py`
- **Issue:** Selector expecting old HTML structure that no longer exists
- **Similar to:** Illinois scraper issue (HTML structure changes are common)

**Why it runs for 6 hours:**
The scraper doesn't **crash** - it catches the error, logs a warning, and moves to the next bill. It processes all 600+ bills (logging errors for each) but never successfully extracts any data.

---

## ⚠️ Historical Context

**Previous run (3 months ago):**

```
22:55:42 WARNING fl.bills.BillDetail: No chapter law table for HB 667
22:55:46 ERROR fl.bills.HouseSearchPage: Selector Error...
(Same errors, ran for 6 hours, timeout)
```

**Conclusion:** This has been broken for **at least 3 months** (likely since House website update).

---

## 🛠️ Workaround

**Short-term:**

- ⚠️ Skip Florida - scraper is unusable
- Wait for OpenStates to update the scraper
- Monitor OpenStates repository for fixes

**Long-term:**

- Consider opening an issue on OpenStates repo if not already reported
- Check OpenStates [issue tracker](https://github.com/openstates/openstates-scrapers/issues) for FL updates
- Alternative: Write custom scraper or use Florida's official API if available

---

## 📋 Upstream Information

- **Repository:** https://github.com/openstates/openstates-scrapers
- **Scraper File:** `scrapers/fl/bills.py`
- **Component:** `HouseSearchPage` class
- **Issue:** Broken selector for House bill search page
- **Related Issues:** Check https://github.com/openstates/openstates-scrapers/issues

---

## 🎯 Detection Tips

**How to identify this issue:**

1. Run scraper and watch logs
2. Look for `INFO openstates: save bill` messages
3. If **absent** after 5-10 minutes → scraper is broken
4. Don't wait 6 hours - cancel early if no saves

**Red flags:**

- Only WARNING and ERROR messages (no INFO saves)
- Same error repeating for different bill numbers
- Log shows "fetching" but never "save bill"

---

**Last Updated:** October 23, 2025
