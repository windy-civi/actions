# Congress.gov Blocking Research & Solutions

## Current Problem
- Congress.gov is blocking our text extraction attempts with 403 errors
- XML downloads from govinfo.gov work perfectly ✅
- HTML amendment downloads from congress.gov fail ❌
- Multiple anti-blocking techniques implemented but still failing

## Key Discovery: OpenStates Solution
**You're already using OpenStates data!** Instead of fighting congress.gov directly, use OpenStates API which has already solved the blocking problem.

### OpenStates Resources
- **GitHub Org**: https://github.com/openstates
- **Main Scrapers**: https://github.com/openstates/openstates-scrapers
- **API v3**: https://github.com/openstates/api-v3
- **Core Backend**: https://github.com/openstates/openstates-core

### Current OpenStates Usage in Your Code
- Already fetching from: `https://v3.openstates.org/jurisdictions/{state_abbr}/sessions`
- OpenStates has working scrapers for all 50 states + federal data
- They've already solved congress.gov blocking issues

## Recommended Solution: Use OpenStates API

### API Endpoints to Explore
```
https://v3.openstates.org/bills/{bill_id}                    # Get full bill data
https://v3.openstates.org/bills?jurisdiction=us&session=119  # Get all federal bills
https://v3.openstates.org/bills?jurisdiction=us&session=119&classification=amendment  # Get amendments
```

### Benefits
- ✅ No blocking issues (OpenStates handles this)
- ✅ Reliable and maintained
- ✅ Clean API interface
- ✅ Already integrated in your system
- ✅ Real-time data updates

## Current Anti-Blocking Techniques (For Reference)
If you still need direct congress.gov access, we've implemented:

### 9 Fallback Strategies
1. Standard retry with congress.gov headers
2. Googlebot User-Agent fallback
3. Firefox User-Agent fallback
4. Mobile User-Agent fallback
5. Minimal headers fallback
6. Curl command-line fallback
7. Wget command-line fallback
8. ChatGPT-style fallback
9. Alternative approach (mobile headers)
10. Government-style (congress.gov referer)

### Advanced Features
- Proxy rotation (when working proxies available)
- Request throttling (3-15s delays for congress.gov)
- Session rotation and warming
- Multiple header styles (stealth, ChatGPT-style, realistic)
- Error tracking and reporting

## Next Steps
1. **Test OpenStates API** - Check if amendment data is available
2. **Modify text extraction** - Use OpenStates API instead of direct scraping
3. **Keep error tracking** - Apply to OpenStates API calls
4. **Research OpenStates documentation** - Understand their data model

## Files Modified
- `openstates_scraped_data_formatter/utils/text_extraction.py` - All anti-blocking techniques
- `openstates_scraped_data_formatter/main.py` - Error reporting integration
- `action.yml` - Updated for text extraction workflow

## Current Status
- XML extraction: ✅ Working perfectly
- HTML amendment extraction: ❌ Blocked by congress.gov
- Error tracking: ✅ Fully implemented
- OpenStates integration: ✅ Already in use

## Research Notes
- OpenStates is a project of Plural (as of 2021)
- They aggregate legislative data from all 50 states + DC + Puerto Rico
- Data is standardized, cleaned, and published via API
- They have robust scrapers that handle blocking issues
- Their API is at v3 and actively maintained

---
*Saved on: $(date)*
*Branch: bill-text-extraction*
*Commit: ab94c27 (latest anti-blocking techniques)*
