# Known Problems

This directory tracks known issues with state scrapers and our formatter code.

## 📂 Organization

- **`scraper/`** - Issues with OpenStates scrapers (upstream)
- **`formatter/`** - Issues with our formatting code

## 🔴 Active Scraper Issues

### Session Configuration Issues

- [New Mexico - 2025 1st Special Session](scraper/new_mexico_session_config.md)
- [Texas - 89(2) 2025 Session](scraper/texas_session_config.md)

### HTML Structure Issues

- [Illinois - XPath Selector Broken](scraper/illinois_html_structure.md)

### Data Extraction Issues

- [Guam - Not Extracting Dates or Actions](scraper/guam_missing_dates_actions.md)

## 🟡 Active Formatter Issues

None currently - Guam issue moved to scraper category (root cause is upstream)

## ✅ Working States

These states are currently working correctly:

- Tennessee (TN)
- Wyoming (WY)
- Federal/USA (congress) - mostly working (skips amendments)

## 📝 Adding New Issues

1. Create a new `.md` file in the appropriate folder
2. Use existing files as templates
3. Include: status, error message, root cause, workaround
4. Update this README to link to the new issue

---

**Last Updated:** October 14, 2025
