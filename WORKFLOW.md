# ArtsMetrics NM Arts Organizations Analysis Workflow

## Overview

This workflow processes NM AG registration statement PDFs to assess organizational health and governance risk across 21+ arts organizations in New Mexico.

**Outcome:** Comparative scorecard showing financial resilience, governance risk, and program scale for each organization, with peer benchmarking and risk flagging.

## Architecture

```
Downloaded PDFs
    ↓
[parse_ag_filings.py] → Extracted metrics (CSV/JSON)
    ↓
[scorecard.py] → Organizational health scores (CSV/JSON)
    ↓
[Analysis & benchmarking] → Risk rankings, peer groups, recommendations
```

## Step 1: Download PDFs (You)

Use `download_tracker.html` to systematically download 21 NM arts organization registration statements.

**What you're downloading:**
- 21 organizations across 4 categories (Dance, Theater, Museum, Music)
- Most recent tax year available (2023-2024)
- From NM Attorney General Charity Registry

**File naming convention:**
```
{OrganizationName}_{FEIN}_{TaxYear}.pdf
```

**Storage:**
```
sample_orgs/
├── Albuquerque_Opera_Theater_870123456_2023.pdf
├── Santa_Fe_Dance_Collective_870234567_2024.pdf
└── ... (21 total)
```

**Time estimate:** ~30 minutes for 21 manual downloads

## Step 2: Parse PDFs (Automated)

```bash
source .venv/bin/activate
python3 parse_ag_filings.py sample_orgs \
  --csv artsmetrics_data/processed/nm_arts_21_extracted.csv \
  --json artsmetrics_data/processed/nm_arts_21_extracted.json
```

**Output:** CSV and JSON with extracted metrics
- FEIN, organization name, tax year
- Financial metrics: revenue, expenses, net assets
- Governance: executive compensation, related-party transactions
- Derived metrics: earned income %, comp-to-revenue %, reserve months

**Time estimate:** 30 seconds for 21 organizations

**Example output:**
```csv
FEIN,Tax Year,Organization Name,Total Revenue,Program Service Revenue,Comp-to-Revenue %,...
870123456,2023,Albuquerque Opera Theater,450000,180000,12.5,...
870234567,2024,Santa Fe Dance Collective,125000,62500,18.2,...
...
```

## Step 3: Calculate Scorecards (Automated)

```bash
python3 scorecard.py artsmetrics_data/processed/nm_arts_21_extracted.csv \
  --csv artsmetrics_data/processed/nm_arts_21_scorecards.csv \
  --json artsmetrics_data/processed/nm_arts_21_scorecards.json
```

**Output:** CSV and JSON with health scores (0-100) across 3 dimensions

### Scoring System

| Component | Weight | Measures |
|-----------|--------|----------|
| **Financial Resilience** | 40% | Earned income diversity, reserve strength, solvency |
| **Governance Risk** | 35% | Compensation concentration, program alignment |
| **Program Scale** | 25% | Organizational revenue size, mission centrality |

### Health Tiers

| Tier | Score | Meaning |
|------|-------|---------|
| **STRONG** | 75-100 | Financially stable, sound governance, sustainable |
| **HEALTHY** | 60-74 | Solid fundamentals, manageable risks |
| **AT-RISK** | 45-59 | Financial stress, governance concerns |
| **CRITICAL** | <45 | Severe risks, urgent intervention needed |

**Example scorecard:**
```
FEIN         Org Name                    Year  Overall  Tier       Resilience  Governance  Scale
870123456    Albuquerque Opera Theater   2023  72.5     HEALTHY    78.0        68.0        70.0
870234567    Santa Fe Dance Collective   2024  52.3     AT-RISK    58.0        42.0        55.0
```

**Time estimate:** 10 seconds for 21 organizations

## Step 4: Analysis & Interpretation

### Key Metrics to Review

For each organization, check:

1. **Governance Red Flags**
   - Comp-to-revenue > 20% (concentration risk)
   - Program expenses < 60% (mission drift)
   - Sole control of financial functions (from raw filing)

2. **Financial Warning Signs**
   - Reserve months < 6 (liquidity crisis)
   - Liabilities-to-assets > 0.5 (solvency risk)
   - Earned income < 10% (fundraising dependent)

3. **Comparative Position**
   - Compare each org's score against:
     - Peer group (similar revenue size)
     - PMTNM baseline (control case)
     - State average (from 21-org sample)

### Example Analysis Questions

1. **Which orgs are most financially resilient?**
   ```sql
   SELECT fein, org_name, financial_resilience 
   FROM scorecards 
   WHERE financial_resilience > 70 
   ORDER BY financial_resilience DESC
   ```

2. **Which have governance risk flags?**
   ```sql
   SELECT fein, org_name, governance_risk, comp_to_revenue_pct 
   FROM scorecards 
   WHERE comp_to_revenue_pct > 20 AND governance_risk < 40
   ```

3. **Which are at-risk or critical?**
   ```sql
   SELECT org_name, overall_health, tier 
   FROM scorecards 
   WHERE tier IN ('AT-RISK', 'CRITICAL')
   ORDER BY overall_health
   ```

## PMTNM Baseline

Use PMTNM's scorecard as a reference for a high-risk organization:

```
Tax Year 2024: 27.0/100 CRITICAL
- Financial Resilience: 45/100 (low earned income, declining assets)
- Governance Risk: 15/100 (24.6% compensation-to-revenue)
- Program Scale: 15/100 (revenue collapsed to $7,114)
```

**Comparison utility:**
- Organizations scoring below PMTNM (27) have even worse fiscal health
- Organizations scoring 40-60 have similar governance/resilience challenges
- Organizations scoring 60+ are in relatively better position

## Files Generated

After completing all steps, you'll have:

```
artsmetrics_data/processed/
├── nm_arts_21_extracted.csv          # Raw metrics for 21 orgs
├── nm_arts_21_extracted.json         # Detailed extraction (+ compensation)
├── nm_arts_21_scorecards.csv         # Health scores for 21 orgs
└── nm_arts_21_scorecards.json        # Detailed scores (+ sub-factors)

Reference (existing):
├── pmtnm_extracted.csv               # PMTNM 2014-2024 baseline
├── pmtnm_scorecards.csv              # PMTNM health trend
└── PMTNM/                             # Original PDFs (12 years)
```

## Next Steps (Post-Analysis)

1. **Peer Grouping**
   - Cluster orgs by revenue size, discipline, health tier
   - Identify patterns (dance orgs more resilient? larger = healthier?)

2. **Risk Reporting**
   - Flag top 5 at-risk organizations for potential advocacy/support
   - Highlight governance red flags (comp concentration, sole control)

3. **National Benchmarking** (Task B)
   - Compare NM arts sector scores against national MTNA affiliates
   - Assess whether NM is healthier/weaker than national average

4. **Visualization**
   - Scatter plots: revenue vs. governance risk
   - Trend lines: organization size vs. reserves
   - Risk heatmaps by discipline and city

## Troubleshooting

### Parser extracted wrong data for a PDF
- Check `issues` column in CSV output
- Open PDF manually to verify format
- File an issue with sample PDF for format update

### Scorecard scores seem off
- Verify extracted metrics are correct first
- Check thresholds in `scorecard.py` THRESHOLDS dict
- Thresholds can be tuned based on domain knowledge

### Want to compare against different peer group
- Modify `scorecard.py` to accept different weighting (e.g., 50% resilience for smaller orgs)
- Add grouping logic to filter by revenue size or discipline

## Command Reference

```bash
# Activate environment
source .venv/bin/activate

# Parse PDFs
python3 parse_ag_filings.py sample_orgs \
  --csv artsmetrics_data/processed/nm_arts_21_extracted.csv

# Calculate scorecards
python3 scorecard.py artsmetrics_data/processed/nm_arts_21_extracted.csv \
  --csv artsmetrics_data/processed/nm_arts_21_scorecards.csv

# View results
head artsmetrics_data/processed/nm_arts_21_scorecards.csv

# Compare to PMTNM
head artsmetrics_data/processed/pmtnm_scorecards.csv
```

## Total Time

| Step | Time |
|------|------|
| Download 21 PDFs | ~30 min |
| Parse + extract metrics | <1 min |
| Calculate scorecards | <1 min |
| **Subtotal** | **~31 min** |
| Analysis & interpretation | 30+ min (open-ended) |
| **Total** | **~60+ min** |

## Questions?

- **Parser issues:** Check `PARSER_GUIDE.md`
- **Scorecard methodology:** Check `scorecard.py` comments and thresholds
- **PMTNM violations context:** Check `FRIDAYHANDOFFMAY15.md`
