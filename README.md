# ArtsMetrics: Arts Nonprofit Organizational Health Index

## What Is This?

ArtsMetrics is an **organizational health index** for arts nonprofits, focusing on **governance intelligence** as an early warning system for organizational dysfunction.

**Why it matters:** The IRS 990 tells you an organization's financials. State AG charity registrations tell you *who controls what* — which reveals governance failures invisible in 990 data.

**Example:** One person controlling checks, funds, records, and legal authority simultaneously? IRS data won't catch it. AG registration data will.

### The Three Data Layers

| Source | Reveals | ArtsMetrics Use |
|--------|---------|-----------------|
| IRS EO BMF | Org exists | Baseline: identify NM arts sector |
| IRS Form 990 | Financials | Financial resilience metrics |
| **State AG Registry** | **Who controls what** | **Governance risk detection** ← **Key insight** |

## Current Status: NM Proof of Concept

### ✅ Complete

**Parser** (`parse_ag_filings.py`)
- Extracts metrics from NM AG registration statement PDFs
- Handles 2014-2017 and 2018+ format variations
- Output: CSV + JSON with financial and governance data
- Tested on 12 PMTNM files (2014-2024) ✓

**Scorecard** (`scorecard.py`)
- 3-part organizational health score (0-100)
  - Financial Resilience (40%): reserves, earned income, solvency
  - Governance Risk (35%): compensation concentration, program alignment
  - Program Scale (25%): organization size
- 4 health tiers: STRONG → HEALTHY → AT-RISK → CRITICAL
- Applied to PMTNM shows 10-year decline (50.8 → 27.0)

**Download Tracker** (`download_tracker.html`)
- Interactive page for 21 NM arts organizations
- Direct links to NM AG portal search pages
- Progress tracking, file naming guide, localStorage persistence

**Documentation**
- `WORKFLOW.md`: End-to-end process (download → parse → scorecard → analyze)
- `PARSER_GUIDE.md`: Parser usage, field definitions, troubleshooting
- `WEB_SCRAPING_EXPLORATION.md`: Why automated data retrieval isn't practical here

### 📊 PMTNM Baseline

**10-year financial & governance trend (2014-2024):**

| Year | Overall | Tier | Revenue | Comp % | Notes |
|------|---------|------|---------|--------|-------|
| 2014 | 50.8 | AT-RISK | $23,963 | 6.3% | Decent reserves, weak governance |
| 2015-2019 | ~40 | CRITICAL | $12,579-18,817 | 13-14% | Revenue volatile, comp rising |
| 2020 | 26.8 | CRITICAL | $10,461 | 16.7% | Severe liquidity crisis |
| 2024 | 27.0 | CRITICAL | $7,114 | 24.6% | Revenue collapsed 70%, compensation ratio doubled |

**Key finding:** Governance risk indicators (comp concentration, sole control) preceded financial collapse. Detecting these early in other orgs could enable intervention.

## Next: Process 21 NM Arts Organizations

### Step 1: Download PDFs (~30 minutes)

Open `download_tracker.html` in your browser and download 21 organization registration statements from the NM AG portal.

- 21 orgs across 4 categories (Dance, Theater, Museum, Music)
- Save to `sample_orgs/` folder
- Naming: `{OrgName}_{FEIN}_{TaxYear}.pdf`

### Step 2: Parse + Score (~2 minutes automated)

```bash
source .venv/bin/activate

# Extract financial and governance metrics
python3 parse_ag_filings.py sample_orgs \
  --csv artsmetrics_data/processed/nm_arts_21_extracted.csv

# Calculate organizational health scores
python3 scorecard.py artsmetrics_data/processed/nm_arts_21_extracted.csv \
  --csv artsmetrics_data/processed/nm_arts_21_scorecards.csv
```

### Step 3: Analyze Results

Compare 21 organizations across:
- **Financial resilience** (reserves, earned income, solvency)
- **Governance risk** (compensation concentration, control structure)
- **Program scale** (organization size, program spending)

Flag organizations scoring CRITICAL (<45) or AT-RISK (45-59) for potential intervention.

Compare against PMTNM baseline to identify similar risk patterns.

## Repository Structure

```
.
├── download_tracker.html              # Download UI for 21 orgs
├── parse_ag_filings.py                # PDF parser (NM AG statements)
├── scorecard.py                       # Health score calculator
├── WORKFLOW.md                        # End-to-end workflow guide
├── PARSER_GUIDE.md                    # Parser usage & troubleshooting
├── WEB_SCRAPING_EXPLORATION.md        # Why automation isn't practical here
├── PMTNM/                             # 12 PMTNM PDF files (2014-2024)
├── sample_orgs/                       # (You'll download 21 files here)
└── artsmetrics_data/
    ├── raw/
    │   └── eo3.csv                    # IRS BMF Region 3 (all states, all sectors)
    └── processed/
        ├── nm_arts_orgs_bmf_only.csv  # 354 NM arts orgs baseline
        ├── pmtnm_extracted.csv        # PMTNM metrics (12 years)
        ├── pmtnm_scorecards.csv       # PMTNM health scores (12 years)
        ├── nm_arts_21_extracted.csv   # (You'll generate this)
        └── nm_arts_21_scorecards.csv  # (You'll generate this)
```

## Vision: 50-State Expansion

**Current:** NM proof of concept (21 orgs)
**Next:** Expand to 50 states, normalize AG registry formats, create national index

**Why this scales:**
- Each state has an AG charity registry (quality varies, but all have something)
- Parser adapts to state-specific PDF formats
- National index becomes early warning system for arts nonprofits nationwide

**Market opportunity:**
- Funders vetting org health before grants
- MTNA national monitoring state affiliates
- State arts agencies overseeing nonprofit ecosystem
- Organization members understanding governance structure

**Competitive advantage:** No one has built this systematically for the arts sector yet.

## For Attorneys & Litigation Support

The governance health assessment (AG registration data) is particularly valuable for:
- **Pre-litigation analysis:** Identifying pattern of control concentration + financial decline
- **Discovery support:** AG registrations show who claimed authority at key moments
- **Expert testimony:** Organizational health scores provide quantified governance risk assessment
- **Pattern documentation:** Multi-year trend shows escalating risk (PMTNM example: 50.8 → 27.0 over 10 years)

The PMTNM violations database (separate project) documents specific breaches; this ArtsMetrics framework provides systemic governance failure detection.

## Technical Details

### Parser

- **Input:** NM AG Charitable Organization Registration Statement PDFs (2014+)
- **Output:** CSV and JSON with extracted metrics
- **Key fields:** FEIN, tax year, org name, revenue, expenses, net assets, compensation, related-party transactions
- **Format support:** 2014-2017 format (old) and 2018+ format (new)
- **Quality:** Extraction confidence flag, issues list for manual review

### Scorecard

- **Methodology:** Weighted 3-part scoring (40% resilience, 35% governance, 25% scale)
- **Thresholds:** Configurable in `scorecard.py` (based on NM arts sector norms)
- **Output:** Health tier (STRONG/HEALTHY/AT-RISK/CRITICAL) + sub-scores
- **Benchmarking:** Compare against peer group (similar revenue size) or PMTNM baseline

### Dependencies

- `pdfplumber` — PDF text/table extraction
- `pandas` — CSV processing
- `requests`, `beautifulsoup4` — Web utilities (for portal exploration)

All installed in `.venv/`

## Questions?

- **How do I use the parser?** → See `PARSER_GUIDE.md`
- **What's the full workflow?** → See `WORKFLOW.md`
- **Why not automate downloads?** → See `WEB_SCRAPING_EXPLORATION.md`
- **How is this different from 990 analysis?** → See project memory: `artmetrics_value_prop.md`

## Contact

Project lead: Willis Glen "Chip" Miller III
Data: NM Attorney General Charity Registry, IRS EO BMF, ProPublica API
