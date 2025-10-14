# State/Territory Scraper Status

Comprehensive tracking of OpenStates scraper status for all 50 states, DC, and territories.

**Last Updated:** October 14, 2025
**OpenStates Scrapers:** https://github.com/openstates/openstates-scrapers/tree/main/scrapers

---

## Legend

- ✅ **Working** - Scraper runs successfully, bills processed
- 🔴 **Failing** - Scraper crashes or returns no usable data
- 🟡 **Partial** - Scraper runs but has issues
- ❓ **Unknown** - Not yet tested
- 🚫 **Not Available** - No scraper exists

---

## ✅ Working States (1)

| State   | Code | Status | Last Tested  | Notes            |
| ------- | ---- | ------ | ------------ | ---------------- |
| Wyoming | WY   | ✅     | Oct 14, 2025 | Fully functional |

---

## 🔴 Failing States (4)

| State      | Code | Status | Issue                        | Link                                             |
| ---------- | ---- | ------ | ---------------------------- | ------------------------------------------------ |
| Illinois   | IL   | 🔴     | HTML structure changed       | [Details](scraper/illinois_html_structure.md)    |
| New Mexico | NM   | 🔴     | 2025 session not configured  | [Details](scraper/new_mexico_session_config.md)  |
| Texas      | TX   | 🔴     | 2025 session not configured  | [Details](scraper/texas_session_config.md)       |
| Guam       | GU   | 🔴     | Not extracting dates/actions | [Details](scraper/guam_missing_dates_actions.md) |

---

## 🟡 Partial Success (1)

| State       | Code | Status | Issue               | Notes                                           |
| ----------- | ---- | ------ | ------------------- | ----------------------------------------------- |
| Federal/USA | USA  | 🟡     | Some downloads work | govinfo.gov works, congress.gov amendments fail |

---

## ❓ States Not Yet Tested (45 + DC + Territories)

### States (45)

| State          | Code | Status |
| -------------- | ---- | ------ |
| Alabama        | AL   | ❓     |
| Alaska         | AK   | ❓     |
| Arizona        | AZ   | ❓     |
| Arkansas       | AR   | ❓     |
| California     | CA   | ❓     |
| Colorado       | CO   | ❓     |
| Connecticut    | CT   | ❓     |
| Delaware       | DE   | ❓     |
| Florida        | FL   | ❓     |
| Georgia        | GA   | ❓     |
| Hawaii         | HI   | ❓     |
| Idaho          | ID   | ❓     |
| Indiana        | IN   | ❓     |
| Iowa           | IA   | ❓     |
| Kansas         | KS   | ❓     |
| Kentucky       | KY   | ❓     |
| Louisiana      | LA   | ❓     |
| Maine          | ME   | ❓     |
| Maryland       | MD   | ❓     |
| Massachusetts  | MA   | ❓     |
| Michigan       | MI   | ❓     |
| Minnesota      | MN   | ❓     |
| Mississippi    | MS   | ❓     |
| Missouri       | MO   | ❓     |
| Montana        | MT   | ❓     |
| Nebraska       | NE   | ❓     |
| Nevada         | NV   | ❓     |
| New Hampshire  | NH   | ❓     |
| New Jersey     | NJ   | ❓     |
| New York       | NY   | ❓     |
| North Carolina | NC   | ❓     |
| North Dakota   | ND   | ❓     |
| Ohio           | OH   | ❓     |
| Oklahoma       | OK   | ❓     |
| Oregon         | OR   | ❓     |
| Pennsylvania   | PA   | ❓     |
| Rhode Island   | RI   | ❓     |
| South Carolina | SC   | ❓     |
| South Dakota   | SD   | ❓     |
| Tennessee      | TN   | ❓     |
| Utah           | UT   | ❓     |
| Vermont        | VT   | ❓     |
| Virginia       | VA   | ❓     |
| Washington     | WA   | ❓     |
| West Virginia  | WV   | ❓     |
| Wisconsin      | WI   | ❓     |

### Other Jurisdictions

| Jurisdiction             | Code | Status |
| ------------------------ | ---- | ------ |
| District of Columbia     | DC   | ❓     |
| Puerto Rico              | PR   | ❓     |
| US Virgin Islands        | VI   | ❓     |
| American Samoa           | AS   | ❓     |
| Northern Mariana Islands | MP   | ❓     |

---

## 📊 Summary Statistics

- **Total Jurisdictions:** 56 (50 states + DC + 5 territories)
- **Tested:** 6 (10.7%)
- **Working:** 1 (16.7% of tested)
- **Failing:** 4 (66.7% of tested)
- **Partial:** 1 (16.7% of tested)
- **Not Tested:** 50 (89.3%)

---

## 📝 How to Update This File

When you test a new state:

1. Run the scraper for that state
2. Check if it succeeds or fails
3. Move the state from "Not Yet Tested" to appropriate section
4. If failing, create detailed issue file in `scraper/` folder
5. Update summary statistics

---

## 🎯 Goal

Test all 56 jurisdictions to understand which ones work reliably and which need attention or workarounds.

---

**Last Updated:** October 14, 2025
