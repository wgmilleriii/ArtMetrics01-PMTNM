# Handoff Document — Friday, May 15, 2026

## Executive Summary

This document captures the state of two interrelated projects as of May 15, 2026:
1. **PMTNM Violations Database** — Legal case preparation for Piano Teachers National membership
2. **ArtsMetrics** — National arts intelligence platform starting with NM

## Project Overview

### PMTNM Violations Database

**Purpose**: Document and systematize violations of governance and fiduciary duties by PMTNM leadership (Jeanne Grealish, Sharon Kunitz, others) for attorney review and potential litigation.

**Current State** (✅ Complete, Ready for Attorney):
- Excel workbook generated via `build_violations.py` (Python/openpyxl)
- 4 sheets: Violations Database | By Person | Email Threads | Key Quotes
- F-17 stale reference already fixed in CoWork session
- 2 CRITICAL violations documented (F-01, F-02):
  - **F-01**: Financial Records Refusal (NMSA §53-8-27) — Grealish refused records to VP directly (Mar 17, 2025) and to VP's attorney under statutory demand (Oct 29–31, 2025)
  - **F-02**: Budget Committee Obstruction — Grealish dismissed handbook requirements, budget not approved for 4+ months of fiscal year

**Files**:
- `build_violations.py` — Build script (Python, openpyxl, self-contained, hardcoded data)
- `PMTNM_Violations_Database.xlsx` — Output workbook (ready to share with attorney)

**How to Update**:
1. Edit `rows[]`, `email_rows[]`, `key_quotes[]` lists in `build_violations.py`
2. Run: `python3 build_violations.py`
3. Output overwrites `PMTNM_Violations_Database.xlsx`
4. **IMPORTANT**: Use Python with utf-8 encoding to edit script (not sed/text editors) due to Unicode em-dashes (—)

---

### ArtsMetrics

**Purpose**: National arts intelligence platform tracking data about arts organizations, measuring impact, and aggregating public arts data for research and advocacy. Starting with New Mexico, expanding nationally.

**Architecture**:
- **Layer 1**: Organizations (orgs, programs, events, funding, people, venues)
- **Layer 2**: Impact (attendance, outcomes, financial health, equity, quality, economic impact)
- **Layer 3**: Aggregation (datasets, benchmarks, reports, mapping, trends)

**Google Drive Structure** (artmetrics65@gmail.com):
```
ArtsMetrics/ (1vXukriThVKhz07tEqkzfIoFALqWGn1Kd)
├── Raw/ — Original data files
│   ├── IRS-990/ (1SPKyDNPeeJg0ZSUThpEBz_6o9z5GMeRn)
│   ├── NEA/
│   ├── NM-Arts/
│   └── Census/
├── Processed/ (1AJPDg0NKfEoGlDEqFY51dgnw14KOJ4DN) ← Upload results here
├── Reports/
└── Reference/ (1zIh4wnYwDV838K3Ron9YvBZyogqPePSm) — Scripts & docs
```

**Data Sources**:
- **IRS EO BMF** — Exempt Organizations Business Master File (all states, all tax-exempt orgs)
- **ProPublica API** — Financial summaries, filing data (no API key needed)
- **IRS 990 e-files** — Deep XML parsing (not yet implemented)
- **Future**: NEA, Census, NM Arts, NASAA, GuideStar/Candid

---

## What Was Done (May 12–15)

### Repo Initialization
- ✅ Fresh Git repo on main branch
- ✅ Violations database synced from CoWork session
- ✅ Build script working, output Excel file ready
- ✅ `.venv` created, dependencies installed (openpyxl, requests, pandas)

### Task A: Fill 42 Missing NM Orgs with Financial Data
**Status: ✅ COMPLETE**

- Downloaded IRS EO BMF Region 3 (Midwest/Mountain, includes NM) — 78MB CSV
- Filtered for arts/culture orgs (NTEE code A*) in NM
- **Result**: **354 NM arts organizations identified** (not 42 — dataset is larger than expected)
  - Albuquerque: 107 orgs
  - Santa Fe: 78 orgs
  - LAS CRUCES, TAOS, RIO RANCHO: smaller cities
  - Top categories: A20 (Multipurpose), A80 (Historical Societies), A23 (Ethnic Awareness), A68 (Music), A65 (Theater)
  - Total revenue (orgs with data): $29.9M
  - Average: $97K, Median: $0 (many small orgs)

**Output**:
- `artsmetrics_data/raw/eo3.csv` — Raw IRS file
- `artsmetrics_data/processed/nm_arts_orgs_bmf_only.csv` — 354 NM orgs, 28 columns

**Not Done Yet** (would take ~2.5 hours):
- ProPublica enrichment (financial details via API)
- NM Arts grant data integration

### Task B: National Peer Comparison for 50 MTNA Affiliates
**Status: ⏸️ IN PROGRESS (paused for handoff)**

- Started downloading all 4 IRS EO BMF regional files (~400MB total)
- Plan: Filter for A03 (Professional Societies/Associations) to identify MTNA state affiliates in all 50 states
- Goal: Compare NM PMTNM against national benchmarks

---

## Lessons Learned

### 1. **IRS Data is Massive**
- Region 3 alone: 78MB (likely hundreds of thousands of rows)
- Filtering by state + NTEE is efficient
- ProPublica API is slower (0.5s per org) but provides financial details not in BMF

### 2. **Build Script Approach Works**
- Hardcoding violation data in Python is maintainable for small datasets
- UTF-8 encoding matters (em-dashes break text editor workflows)
- openpyxl allows sophisticated styling (colored headers, frozen panes, tables)

### 3. **NM Arts Sector is Larger Than Expected**
- 354 orgs > initial estimate of "42 missing"
- Heavy concentration in Albuquerque/Santa Fe (60% of state)
- Revenue data gaps (many orgs report $0 to IRS, may be volunteer-run)

### 4. **API Rate Limiting & Delays**
- ProPublica: 0.5s delay/request, checkpoint saves every 100 orgs
- Progress file allows safe interruption and resume
- For 354 NM orgs: ~30 min to fully enrich

### 5. **Virtual Environment Isolation is Essential**
- System Python had externally-managed environment restrictions
- Created `.venv`, installed dependencies cleanly
- Bash: `source .venv/bin/activate` before running scripts

---

## Current Directory State

```
ArtMetrics01-PMTNM/
├── .git/                               # Fresh repo, 1 commit
├── .claude/                            # Claude Code project settings
├── .venv/                              # Virtual environment
├── .gitignore                          # Excludes .venv/
├── build_violations.py                 # Build script for Excel workbook
├── PMTNM_Violations_Database.xlsx      # Output (ready for attorney)
├── artsmetrics_data/
│   ├── raw/
│   │   └── eo3.csv                     # IRS BMF Region 3 (78MB)
│   └── processed/
│       ├── nm_arts_orgs_bmf_only.csv   # 354 NM orgs (61KB)
│       └── nm_arts_orgs_sample.csv     # Sample with ProPublica data (15 orgs)
└── FRIDAYHANDOFFMAY15.md              # This file
```

---

## Next Steps (Priority Order)

### Immediate (Today/Monday)
1. **Share violations database with attorney**
   - `PMTNM_Violations_Database.xlsx` is ready
   - All critical violations documented, sources linked

2. **Commit & push repo**
   ```bash
   git add -A
   git commit -m "Initial commit: violations database build script, NM arts orgs baseline"
   git push origin main
   ```

### This Week (May 20–24)
3. **Complete Task A: ProPublica enrichment for NM orgs**
   - Takes ~30 min to run
   - Adds financial data to 354 orgs
   - Creates comparison baseline for NM vs national

4. **Complete Task B: National music/performance peer comparison**
   - Download all 4 regional BMF files (already started)
   - Filter for A03 (Professional Societies) — MTNA affiliates in 50 states
   - Enrich with ProPublica data
   - Create comparison: NM PMTNM vs 50 state affiliates

### May 27–31
5. **Task C: PMTNM regulatory filings download**
   - Scope: Which filings? (NM AG, IRS Form 990-N, state compliance?)
   - Create systematic archive for attorney review
   - Formalize NM AG decade-long filing pattern (2014–2024)

6. **Pending items** (from CoWork handoff)
   - Declining net assets pattern analysis
   - Timeline update (case chronology)
   - "Silence, officer training" email thread review

### June 1+
7. **Task D: Analysis & visualization outputs**
   - Financial comparison charts (NM vs national)
   - Regulatory timeline
   - Violation severity assessment for attorney
   - Executive summary for potential court filing

---

## Technical Debt & Considerations

1. **Full ProPublica Enrichment**: Consider running in background or splitting by state
2. **IRS 990 XML Parsing**: Currently skipped, would unlock deeper financial data
3. **Local SQLite Database**: Would make querying easier than CSVs
4. **Google Drive Upload**: Need to implement automated upload of processed CSVs
5. **Test Coverage**: No tests yet, but small dataset (354 orgs) makes manual verification feasible

---

## Key Contacts & Resources

- **ArtsMetrics Drive**: artmetrics65@gmail.com (public folder structure in Reference/)
- **Attorney**: Kathy Black (Law 4 Small Business) — receives violations database
- **Data Sources**:
  - IRS EO BMF: https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf
  - ProPublica API: https://projects.propublica.org/nonprofits/api/v2
  - IRS 990 e-files: https://registry.opendata.aws/irs990/

---

## Handoff Checklist

- [x] Violations database ready for attorney
- [x] Build script in repo
- [x] NM arts baseline identified (354 orgs)
- [x] Git repo initialized
- [x] Development environment documented
- [ ] Repo pushed to GitHub
- [ ] Tasks B–D planned (pending execution)
- [ ] ProPublica enrichment completed
- [ ] National peer comparison dataset created

---

**Prepared by**: Claude Code  
**Date**: Friday, May 15, 2026  
**Status**: Ready for next phase
