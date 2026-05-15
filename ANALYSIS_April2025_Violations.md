# Analysis: April 28, 2025 PMTNM Board Meeting Transcript

**Date Analyzed:** May 15, 2026  
**Status:** Initial cleanup and violation review complete

---

## Summary

### Transcript Status
- ✅ **Original File:** 1,988 lines with 663 timestamp headers (redundant)
- ✅ **Cleaned File:** `April282025_CLEAN.txt` created, headers removed
- ✅ **Reduction:** 3% file size reduction (headers+deduplication)

---

## Key Content Found in April Meeting

### 1. FUNDRAISING DISCUSSION (Violation Context)
**Timestamp:** Lines 1215-1272 (fundraising section)

**Key Speakers:** Jeanne, Sam, Sharon  
**Key Points:**
- Jeanne: "Last year we had donors which enabled us to bring in the pianist...A couple of thousand dollar donations from individuals."
- Sam: Discussion of whether fundraising should go to specific events vs. general Treasury
- **Tatiana's Role:** Jeanne credits Tatiana with donor cultivation: "The asking of this one donor came from Tatiana...She worked to get the money from an individual."
- Jeanne's statement: "There's just a matter of asking. Who's Larry? And asking...One of them was a person who had heard this pianist once before and said I'd like to hear him again, so here's a thousand dollars."
- Jeanne paid $750 personally for a French pianist from "family trust"

**Violation Implications:**
- Supports **existing L-06** (Larry/NMSM Business Promotion) context
- **Related to F-11** (Terri Reck TOTY interference): Tatiana's involvement in fundraising while also being TOTY winner (2023) shows pattern of institutional preference

---

## Violations Database Status

### Build Script Verification
- ✅ **46 total violations** properly documented in `build_violations.py`
- ✅ All major violation IDs present: F-01 through F-17, L-01 through L-07, E-01 through E-04, M-01 through M-07, S-01 through S-05, G-01, G-02, A-01, R-01 through R-03

### Sync Status with Excel File
- ✅ `PMTNM_Violations_Database.xlsx` (59KB) exists
- Need to verify: All 46 violations from build_violations.py are reflected in the Excel file

---

## Outstanding Items (From Handoff)

### 1. ❓ Terri/Teri Reck "hadn't contributed" Comment
- **Source noted as:** "Spring 2025 Board Meeting transcript/notes"
- **Status:** NOT found in April 28 meeting
- **Violation location:** F-08 in violations database
- **Action needed:** Check if this comes from a different Spring 2025 meeting

### 2. ❓ Stale F-17 Reference (From Handoff)
- **Issue:** By Person sheet in violations database allegedly references removed F-17
- **F-17 Status:** Present in build_violations.py as "Officer Compensation Without Board Authorization"
- **Action needed:** Verify "By Person" sheet in Excel for stale refs

### 3. ✅ Fundraising Comments Assessment
- **Found in April meeting:** Significant discussion of Jeanne's approach to donor cultivation
- **Key element:** Tatiana's prominent role in fundraising activities
- **Note:** Not a violation per se, but context supporting existing violations (L-06, F-11)

---

## Recommendations

### For Violations Database Synchronization
1. **Compare build_violations.py with PMTNM_Violations_Database.xlsx**
   - Verify all 46 violations are in Excel
   - Check for discrepancies in evidence fields
   - Verify "By Person" sheet has no stale references

2. **Verify Spring 2025 Meeting Documentation**
   - Locate source of Teri Reck "hadn't contributed" comment
   - Confirm this is documented in F-08 with correct evidence link

3. **Jeanne's Fundraising Pattern**
   - April meeting shows Jeanne characterizes fundraising as "just a matter of asking"
   - Payment of $750 from "family trust" for pianist may warrant review under private benefit rules
   - Combined with F-06 (personal furniture storage), suggests pattern worth noting

### For Transcript Cleanup
- Clean transcript saved as `April282025_CLEAN.txt`
- File is readable and organized by content sections
- Recommend manual review for transcription errors (audio → text conversion artifacts visible)

---

## Files Generated

- `April282025_CLEAN.txt` - Deduplicated, cleaned April 2025 meeting transcript
- `ANALYSIS_April2025_Violations.md` - This document

---

## Next Steps

1. **Priority 1:** Sync violations database files before sharing with attorney
2. **Priority 2:** Locate and verify Teri Reck comment source
3. **Priority 3:** Review Excel file for any missing or misstated violations
