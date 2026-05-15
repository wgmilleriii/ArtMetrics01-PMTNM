# NM AG Registration Statement Parser Guide

## What It Does

`parse_ag_filings.py` extracts governance and financial metrics from NM Attorney General Charitable Organization Registration Statement PDFs.

**Extracted metrics:**
- Organization info (FEIN, name, tax year)
- Financial data (revenue, expenses, net assets)
- Executive compensation (names, titles, amounts)
- Derived metrics (earned income %, comp-to-revenue %, fundraising efficiency)

## Setup

```bash
# Activate virtual environment
source .venv/bin/activate

# pdfplumber is already installed; verify:
pip list | grep pdfplumber
```

## Usage

### Parse a directory of PDFs

```bash
python3 parse_ag_filings.py <pdf_directory> --csv output.csv --json output.json
```

**Example:**
```bash
# Parse the 21 downloaded NM arts org PDFs
python3 parse_ag_filings.py sample_orgs --csv artsmetrics_data/processed/nm_arts_21_extracted.csv
```

### Output files

- **CSV**: Flat table format, one org-year per row
  - Columns: FEIN, Tax Year, Org Name, Financial metrics, Derived metrics, Issues
  - Good for: Excel, pivot tables, spreadsheet analysis
  
- **JSON**: Nested format with full detail
  - Includes arrays of executive compensation and related-party transactions
  - Good for: downstream processing, database loads

## File Naming Convention

Downloaded PDFs should follow this naming pattern:

```
{OrganizationName}_{FEIN}_{TaxYear}.pdf
```

**Examples:**
- `Albuquerque_Opera_Theater_870123456_2023.pdf`
- `Santa_Fe_Dance_Collective_870234567_2024.pdf`

## What Gets Extracted

### Financial Metrics

| Field | Description |
|-------|-------------|
| `total_revenue` | Total Gross Revenue from Annual Financials section |
| `program_service_revenue` | Program/earned income (subset of total) |
| `investment_income` | Investment & interest income |
| `fundraising_revenue` | Professional fundraising collections (gross) |
| `total_expenses` | Sum of all expenses |
| `program_expenses` | Program service expenses |
| `fundraising_expenses` | Fundraising-specific expenses |
| `management_expenses` | Management & general expenses |
| `total_net_assets` | End-of-year net assets (financial flexibility) |
| `unrestricted_net_assets` | Unrestricted (most flexible) net assets |
| `total_assets`, `total_liabilities` | Balance sheet items |

### Governance Metrics

| Field | Description |
|-------|-------------|
| `executive_compensation[]` | Array of officers with compensation |
| `related_party_transactions[]` | Schedule L related-party transaction details |
| `comp_to_revenue_pct` | Compensation as % of total revenue (concentration risk) |
| `earned_income_pct` | Program service revenue as % of total (resilience) |
| `liabilities_to_assets_ratio` | Debt burden (solvency) |

## Quality Flags

The `issues` field captures extraction problems:

- `No Annual Financials section found` — PDF structure unexpected
- Other warnings indicate partial data extraction

**Extraction confidence** (0.0-1.0): Indicates reliability of parsed data
- 1.0 = high confidence
- < 0.9 = manual review recommended

## Format Support

### Current

- **2014-2017 format**: "Registration Tax Year" label format
- **2018+ format**: "Tax Year YYYY - fiscal period..." single-line format

Both formats extract reliably. Tax years 2023-2024 may have slight variations — check confidence scores.

### Future improvements

- [ ] Parse detailed Schedule L (related-party transactions)
- [ ] Extract Part III narrative program outputs
- [ ] Handle merged/split organizations
- [ ] Parse historical amendments/corrections

## Troubleshooting

### No data extracted for a specific PDF

1. Check the `issues` column in CSV output
2. Open the PDF manually and verify:
   - "Annual Financials" section exists
   - Format matches known patterns
3. If format is different, file an issue with sample PDF

### Wrong tax year

1. Verify filename contains correct year (YYYY)
2. Check PDF's first page for tax year label
3. Run with `--json` output to see raw extracted values

### Missing compensation data

- Older PDFs may use different officer format
- Some orgs have no named officers (unlikely for PMTNM-size orgs)
- Check "Charity Individuals" section manually

## Next Steps After Extraction

1. **Validate**: Check CSV for missing values, obvious errors
2. **Enrich**: Join with IRS 990 data for cross-verification
3. **Analyze**: Calculate scorecard metrics (financial resilience, governance risk, program scale)
4. **Benchmark**: Compare org against peer group (NM music orgs, national affiliates, etc.)

## Example: Process 21 Downloaded Orgs

```bash
# 1. Download 21 org PDFs using download_tracker.html
# 2. Save to sample_orgs/ folder with consistent naming

# 3. Run parser
python3 parse_ag_filings.py sample_orgs \
  --csv artsmetrics_data/processed/nm_arts_21_extracted.csv \
  --json artsmetrics_data/processed/nm_arts_21_extracted.json

# 4. Review results
head -5 artsmetrics_data/processed/nm_arts_21_extracted.csv

# 5. Check for issues
grep -i "issues" artsmetrics_data/processed/nm_arts_21_extracted.csv | grep -v "^Issues" | head
```

## Testing

The parser has been tested on 12 PMTNM tax years (2014-2024):
- ✅ All 12 files parse successfully
- ✅ Financial data matches original PDFs
- ✅ Compensation data accurate
- ✅ Derived metrics calculate correctly

Results: `artsmetrics_data/processed/pmtnm_extracted.csv`
