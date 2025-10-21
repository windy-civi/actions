# 📊 USA Data Pipeline - Data Summary

## Project Status

Successfully formatted all scraped federal bill data from the **119th Congressional Session** using the OpenStates data pipeline.

**Last Updated**: October 17, 2025

### Recent Updates

**October 17, 2025** - ✅ **Fixed Missing Senate Bills Issue**

- Updated Docker image from `6a0ce774f2c12b7fa61b25d6c964212dfe3b636c` to `latest`
- Resolved scraper crash on "Decision of Chair Not Sustained" vote status
- **Restored 2,995 S bills** (Senate Bills) that were previously missing
- **Restored 89 SJRES bills** (Senate Joint Resolutions) that were previously missing
- Data is now **complete** with all 8 bill types

---

## 📈 Data Statistics

### Processed Bills (Session 119)

- **Total Unique Bills**: 10,278
- **Total Vote Events**: 374
- **Source**: GovInfo.gov via OpenStates scrapers
- **Docker Image**: `latest` (fixed scraper crash issue)

### Bill Type Distribution

| Bill Type | Count      | Description                            |
| --------- | ---------- | -------------------------------------- |
| HR        | 5,733      | House Bills                            |
| S         | 2,995      | Senate Bills ✅ (restored)             |
| HRES      | 803        | House Resolutions                      |
| SRES      | 449        | Senate Resolutions                     |
| HJRES     | 131        | House Joint Resolutions                |
| SJRES     | 89         | Senate Joint Resolutions ✅ (restored) |
| HCONRES   | 56         | House Concurrent Resolutions           |
| SCONRES   | 22         | Senate Concurrent Resolutions          |
| **TOTAL** | **10,278** |                                        |

### Chamber Distribution

- **House (H prefix)**: 6,723 bills (65.4%)
- **Senate (S prefix)**: 3,555 bills (34.6%)

---

## 📁 Data Structure

### Directory Organization

```
data_output/
├── data_processed/
│   └── country:us/
│       └── congress/
│           └── sessions/
│               └── 119/
│                   └── bills/
│                       └── {BILL_ID}/
│                           ├── logs/          # Timestamped action JSONs
│                           ├── files/         # Source documents (XML + TXT)
│                           ├── metadata.json  # Comprehensive bill metadata
│                           └── placeholder.json
├── data_not_processed/
│   └── missing_session/    # 151 unprocessed event files
└── event_archive/          # 147 event files awaiting post-processing
```

### Bill Folder Structure Example

**Example: HR1 - "One Big Beautiful Bill Act"**

```
HR1/
├── logs/ (76 JSON files)
│   ├── 20250211T050000Z_referred_to_the_house_committee_on_energy_and_commerce.json
│   ├── 20250211T050000Z.classification.introduction.lower.json
│   └── ... (additional timestamped actions)
├── files/
│   ├── BILLS-119hr1eas_Engrossed_Amendment_Senate_extracted.txt
│   ├── BILLS-119hr1eas_Engrossed_Amendment_Senate.xml
│   ├── BILLS-119hr1eh_Engrossed_in_House_extracted.txt
│   ├── BILLS-119hr1eh_Engrossed_in_House.xml
│   ├── BILLS-119hr1enr_Enrolled_Bill_extracted.txt
│   ├── BILLS-119hr1enr_Enrolled_Bill.xml
│   ├── BILLS-119hr1pcs_Placed_on_Calendar_Senate_extracted.txt
│   ├── BILLS-119hr1pcs_Placed_on_Calendar_Senate.xml
│   ├── BILLS-119hr1rh_Reported_in_House_extracted.txt
│   ├── BILLS-119hr1rh_Reported_in_House.xml
│   ├── PLAW-119publ21_Public_Law_extracted.txt
│   └── PLAW-119publ21_Public_Law.xml
├── metadata.json
└── placeholder.json
```

---

## ⏱️ Processing Timestamps

Last processed data from OpenStates (from `latest_timestamp_seen.txt`):

```json
{
  "bills": "2025-10-10T04:00:00",
  "vote_events": "2025-10-09T16:25:00",
  "events": "1900-01-01T00:00:00"
}
```

**Notes:**

- Bills: Last updated October 10, 2025 at 04:00 AM
- Vote Events: Last updated October 9, 2025 at 4:25 PM
- Events: Not yet processed (default timestamp)

---

## 🔍 Data Quality Notes

### Successfully Processed

✅ 7,121 unique bills with complete metadata
✅ Timestamped action logs for each bill
✅ Source documents (XML) with extracted text (TXT)
✅ Blockchain-style versioned data structure
✅ Deterministic output (removed `_id` and `scraped_at` fields)
✅ Proper session mapping to 119th Congress

### Unprocessed Data

⚠️ **Missing Session Information (151 event files)**

- Location: `data_not_processed/missing_session/`
- Issue: Events couldn't be matched to bills due to missing session information
- Example: `event_01d9f656-a888-11f0-8eb4-2af993d425c1.json`
- Action Needed: Review and either manually map or investigate data source

📦 **Event Archive (147 event files)**

- Location: `event_archive/`
- Status: Temporary storage for events pending post-processing
- Action Needed: Run post-processor to link events to bill actions

### Notable Observations

1. **No Regular Senate Bills (S prefix only)**

   - Dataset contains only Senate Resolutions (SRES, SCONRES)
   - Regular Senate bills (S1, S2, etc.) are not present in this dataset
   - This may reflect the actual data available from OpenStates for session 119

2. **House Bills Dominate**

   - 94.4% of bills originate from the House
   - 5.6% are Senate resolutions

3. **Bill Lifecycle Documentation**
   - Many bills include multiple document versions (engrossed, enrolled, public law)
   - HR1 became Public Law 119-21 (signed July 4, 2025)

---

## ✅ Compliance with Project Rules

This repository adheres to all standards defined in `PROJECT_RULES.MD`:

| Rule                            | Status | Notes                                  |
| ------------------------------- | ------ | -------------------------------------- |
| Blockchain-style versioned data | ✅     | Timestamped logs maintained            |
| Deterministic output            | ✅     | `_id` and `scraped_at` removed         |
| Proper directory structure      | ✅     | `country:us/congress/sessions/119/`    |
| Error handling                  | ✅     | Unprocessed items logged separately    |
| Timestamp tracking              | ✅     | `latest_timestamp_seen.txt` maintained |
| Source attribution              | ✅     | Maintained in metadata and files       |
| Immutable logs                  | ✅     | Once written, logs never modified      |
| Session mapping                 | ✅     | All bills mapped to session 119        |
| Data sanitization               | ✅     | OpenStates metadata cleaned            |

---

## 🎯 Use Cases

### Downstream AI Analysis

This formatted dataset is optimized for:

1. **Legislative Text Analysis**

   - Full bill text in extracted TXT format
   - Original XML for structured parsing
   - Metadata for context and relationships

2. **Bill Lifecycle Tracking**

   - Timestamped action logs show progression
   - Multiple document versions (engrossed, enrolled, enacted)
   - Classification tracking (introduction, committee, passage, signature)

3. **Congressional Activity Analysis**

   - Bill type distribution analysis
   - Chamber activity comparison
   - Sponsor and co-sponsor networks

4. **Policy Research**
   - Full text search across 7,121 bills
   - Subject classification
   - Cross-reference with events and votes

---

## 📊 Quick Statistics

```
Total Bills Processed:       7,121
Total Files Generated:      44,387
  - JSON files:            28,389
  - TXT files:              7,999
  - XML files:              7,999

Processing Dates:
  - Bills:      Oct 10, 2025
  - Votes:      Oct 9, 2025
  - Events:     Pending

Storage Organization:
  - Data Processed:        ✅ Complete
  - Data Not Processed:    151 events
  - Event Archive:         147 events
```

---

## 🔄 Next Steps

### Immediate Actions

1. **Process Event Archive**

   - Run post-processor on 147 archived events
   - Link events to corresponding bill actions
   - Update event_archive status

2. **Investigate Missing Sessions**

   - Review 151 unprocessed event files
   - Determine why session information is missing
   - Manual mapping or data source investigation

3. **Verify Senate Bill Coverage**
   - Confirm if regular Senate bills (S prefix) should be included
   - Check OpenStates API for S1, S2, etc.
   - Update scraper if needed

### Future Enhancements

1. **Multi-Repository Deployment**

   - Deploy to 56 jurisdiction repositories (50 states + federal + 5 territories)
   - Configure GitHub Actions workflows
   - Set up nightly automated processing

2. **Data Analysis Tools**

   - Create scripts for common queries
   - Build visualization dashboards
   - Generate summary reports

3. **Monitoring & Alerts**
   - Track processing success rates
   - Alert on data quality issues
   - Monitor API rate limits

---

## 📞 Support

For questions or issues related to this data pipeline:

- Review `PROJECT_RULES.MD` for detailed guidelines
- Check `README.md` for setup instructions
- Submit issues via GitHub (Windy Civi ecosystem)

---

_Document Generated: October 15, 2025_
_Data Coverage: 119th Congressional Session_
_Pipeline Version: 1.0_
