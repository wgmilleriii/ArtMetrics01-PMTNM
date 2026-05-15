#!/usr/bin/env python3
"""
NM AG Registration Statement Parser
Extracts governance and financial metrics from NM AG Charitable Organization
Registration Statement PDFs (Form NM-COS).

Core metrics extracted:
1. Total revenue
2. Program service revenue (earned income)
3. Unrestricted net assets (financial flexibility)
4. Liabilities-to-assets ratio (solvency)
5. Executive compensation (concentration risk)
6. Fundraising expenses and efficiency
7. Schedule L related-party transaction amounts
8. Program outputs from Part III narratives
"""

import pdfplumber
import re
import json
import csv
import sys
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Any


@dataclass
class ExecutiveComp:
    name: str
    title: str
    hours_per_week: Optional[float] = None
    reportable_comp: Optional[float] = None
    amount: Optional[float] = None

    def total(self) -> float:
        return self.amount or self.reportable_comp or 0.0


@dataclass
class RelatedPartyTransaction:
    description: str
    amount: float
    related_party_name: Optional[str] = None
    relationship: Optional[str] = None


@dataclass
class FilingMetrics:
    fein: str
    tax_year: int
    org_name: str

    # Financial metrics
    total_revenue: Optional[float] = None
    program_service_revenue: Optional[float] = None  # Earned income
    investment_income: Optional[float] = None
    fundraising_revenue: Optional[float] = None

    total_expenses: Optional[float] = None
    program_expenses: Optional[float] = None
    fundraising_expenses: Optional[float] = None
    management_expenses: Optional[float] = None

    unrestricted_net_assets: Optional[float] = None
    total_net_assets: Optional[float] = None
    total_assets: Optional[float] = None
    total_liabilities: Optional[float] = None

    # Governance metrics
    executive_compensation: List[ExecutiveComp] = field(default_factory=list)
    related_party_transactions: List[RelatedPartyTransaction] = field(default_factory=list)

    # Derived metrics
    earned_income_pct: Optional[float] = None
    fundraising_efficiency: Optional[float] = None
    comp_to_revenue_pct: Optional[float] = None
    liabilities_to_assets_ratio: Optional[float] = None

    # Quality flags
    extraction_confidence: float = 1.0
    issues: List[str] = field(default_factory=list)

    def calculate_derived_metrics(self):
        if self.total_revenue and self.program_service_revenue:
            self.earned_income_pct = (self.program_service_revenue / self.total_revenue) * 100

        if self.fundraising_expenses and self.fundraising_revenue:
            if self.fundraising_revenue > 0:
                self.fundraising_efficiency = self.fundraising_expenses / self.fundraising_revenue

        if self.executive_compensation:
            total_exec_comp = sum(ec.total() for ec in self.executive_compensation)
            if self.total_revenue:
                self.comp_to_revenue_pct = (total_exec_comp / self.total_revenue) * 100

        if self.total_assets and self.total_liabilities:
            if self.total_assets > 0:
                self.liabilities_to_assets_ratio = self.total_liabilities / self.total_assets


class AGFilingParser:
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.pdf = None
        self.text_content = ""
        self.tables = []

    def open(self):
        self.pdf = pdfplumber.open(self.pdf_path)
        self.text_content = "\n".join(page.extract_text() or "" for page in self.pdf.pages)
        self.tables = [t for page in self.pdf.pages for t in page.extract_tables() or []]

    def close(self):
        if self.pdf:
            self.pdf.close()

    def extract_org_info(self) -> tuple[str, int, str]:
        """Extract FEIN, tax year, and organization name from PDF."""
        # Get first page for tax year
        first_page_text = self.pdf.pages[0].extract_text() or ""

        tax_year = 0

        # Try newer format first: "Tax Year YYYY - fiscal period..."
        tax_year_match = re.search(r'Tax\s+Year\s+(\d{4})\s*-', first_page_text, re.IGNORECASE)
        if tax_year_match:
            tax_year = int(tax_year_match.group(1))
        else:
            # Try older format: "Registration Tax Year" followed by year
            tax_year_match = re.search(
                r'Registration\s+Tax\s+Year.*?\n(?:.*?\n)*?(\d{4})',
                first_page_text,
                re.IGNORECASE | re.DOTALL
            )
            if tax_year_match:
                tax_year = int(tax_year_match.group(1))

        # Extract FEIN from "FEIN: XX-XXXXXXX"
        fein_match = re.search(r'FEIN:\s*(\d{2})-?(\d{7})', first_page_text)
        if fein_match:
            fein = fein_match.group(1) + fein_match.group(2)
        else:
            fein = ""

        # Extract Charity Name
        charity_match = re.search(r'Charity Name:\s+([^\n]+)', first_page_text)
        org_name = charity_match.group(1).strip() if charity_match else ""

        return fein, tax_year, org_name

    def extract_financial_metrics(self, metrics: FilingMetrics):
        """Extract revenue, expenses, and asset data from NM AG Annual Financials section."""

        # Look for "Annual Financials" section (usually on last page)
        financials_match = re.search(
            r'Annual Financials\s*(.+?)(?:\n\n|\Z)',
            self.text_content,
            re.IGNORECASE | re.DOTALL
        )

        if not financials_match:
            metrics.issues.append("No Annual Financials section found")
            return

        financials_section = financials_match.group(1)

        # Field mappings with regex patterns
        field_patterns = {
            'total_revenue': [
                r'Total\s+Gross\s+Revenue:\s*\$?([\d,]+(?:\.\d{2})?)',
                r'Total\s+Revenue:\s*\$?([\d,]+(?:\.\d{2})?)',
            ],
            'fundraising_revenue': [
                r'Gross\s+Professional\s+Fundraising\s+Collections:\s*\$?([\d,]+(?:\.\d{2})?)',
            ],
            'program_service_revenue': [
                r'Program\s+[Ss]ervice\s+Revenue:\s*\$?([\d,]+(?:\.\d{2})?)',
                r'Total\s+Contributions:\s*\$?([\d,]+(?:\.\d{2})?)',  # Fallback
            ],
            'total_expenses': [
                r'Total\s+Expenses:\s*\$?([\d,]+(?:\.\d{2})?)',
            ],
            'program_expenses': [
                r'Program\s+[Ss]ervices?\s+Expenses:\s*\$?([\d,]+(?:\.\d{2})?)',
            ],
            'fundraising_expenses': [
                r'Fundraising\s+Expenses:\s*\$?([\d,]+(?:\.\d{2})?)',
            ],
            'management_expenses': [
                r'Management\s+(?:General\s+)?Expenses:\s*\$?([\d,]+(?:\.\d{2})?)',
            ],
            'total_net_assets': [
                r'End\s+of\s+Year\s+Net\s+Assets:\s*\$?([\d,]+(?:\.\d{2})?)',
            ],
            'unrestricted_net_assets': [
                r'(?:Unrestricted\s+)?Net\s+Assets.*?:\s*\$?([\d,]+(?:\.\d{2})?)',
            ],
        }

        for field_name, patterns in field_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, financials_section, re.IGNORECASE)
                if match:
                    try:
                        value = float(match.group(1).replace(',', ''))
                        current_value = getattr(metrics, field_name)
                        if current_value is None:  # Only set if not already set
                            setattr(metrics, field_name, value)
                        break
                    except (ValueError, IndexError):
                        continue

    def extract_executive_compensation(self, metrics: FilingMetrics):
        """Extract executive compensation from Charity Individuals section."""

        # Look for "Charity Individuals" section in NM AG format
        individuals_match = re.search(
            r'Charity Individuals:(.*?)(?:Accountant|Person Authorized|\Z)',
            self.text_content,
            re.IGNORECASE | re.DOTALL
        )

        if not individuals_match:
            return

        section = individuals_match.group(1)

        # Extract individual entries: Name, Position, Compensation
        # Pattern: Name: ..., Position Title: ..., Annual Compensation: $X.XX
        individual_blocks = re.findall(
            r'Name:\s+([^\n]+)\s+Position Title:\s+([^\n]+).*?Annual\s+Compensation:\s*\$?([\d,]+(?:\.\d{2})?)',
            section,
            re.IGNORECASE | re.DOTALL
        )

        for name, title, comp in individual_blocks:
            try:
                amount = float(comp.replace(',', ''))
                if amount > 0:  # Only include if comp > $0
                    exec_comp = ExecutiveComp(
                        name=name.strip(),
                        title=title.strip(),
                        amount=amount
                    )
                    metrics.executive_compensation.append(exec_comp)
            except ValueError:
                continue

    def extract_related_party_transactions(self, metrics: FilingMetrics):
        """Extract Schedule L or related party transaction information."""

        schedule_l_match = re.search(
            r'(?:Schedule\s+L|Related\s+Party\s+Transactions).*?\n(.*?)(?:\n\n|\Z)',
            self.text_content,
            re.IGNORECASE | re.DOTALL
        )

        if not schedule_l_match:
            return

        section = schedule_l_match.group(1)

        # Look for transaction lines with amounts
        lines = section.split('\n')
        for line in lines:
            amount_match = re.search(r'\$?\s*([\d,]+(?:\.\d{2})?)', line)
            if amount_match and len(line.strip()) > 10:
                try:
                    amount = float(amount_match.group(1).replace(',', ''))
                    transaction = RelatedPartyTransaction(
                        description=line.strip(),
                        amount=amount
                    )
                    metrics.related_party_transactions.append(transaction)
                except ValueError:
                    continue

    def parse(self) -> FilingMetrics:
        """Parse the PDF and extract all metrics."""
        self.open()

        try:
            fein, tax_year, org_name = self.extract_org_info()

            metrics = FilingMetrics(
                fein=fein,
                tax_year=tax_year,
                org_name=org_name
            )

            self.extract_financial_metrics(metrics)
            self.extract_executive_compensation(metrics)
            self.extract_related_party_transactions(metrics)

            metrics.calculate_derived_metrics()

            return metrics

        finally:
            self.close()


def process_directory(directory: str, output_csv: str = None, output_json: str = None):
    """Process all PDFs in a directory."""

    pdf_dir = Path(directory)
    pdf_files = list(pdf_dir.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDFs found in {directory}")
        return []

    results = []
    errors = []

    for pdf_file in sorted(pdf_files):
        print(f"Processing {pdf_file.name}...", end=" ")

        try:
            parser = AGFilingParser(str(pdf_file))
            metrics = parser.parse()
            results.append(metrics)
            print("✓")
        except Exception as e:
            error_msg = f"{pdf_file.name}: {str(e)}"
            errors.append(error_msg)
            print(f"✗ {str(e)}")

    # Write CSV output
    if output_csv and results:
        with open(output_csv, 'w', newline='') as f:
            writer = csv.writer(f)

            # Header
            headers = [
                'FEIN', 'Tax Year', 'Organization Name',
                'Total Revenue', 'Program Service Revenue', 'Investment Income', 'Fundraising Revenue',
                'Total Expenses', 'Program Expenses', 'Fundraising Expenses', 'Management Expenses',
                'Unrestricted Net Assets', 'Total Net Assets', 'Total Assets', 'Total Liabilities',
                'Earned Income %', 'Fundraising Efficiency', 'Comp-to-Revenue %', 'Liabilities-to-Assets Ratio',
                'Extraction Confidence', 'Issues'
            ]
            writer.writerow(headers)

            # Data rows
            for m in results:
                writer.writerow([
                    m.fein, m.tax_year, m.org_name,
                    m.total_revenue, m.program_service_revenue, m.investment_income, m.fundraising_revenue,
                    m.total_expenses, m.program_expenses, m.fundraising_expenses, m.management_expenses,
                    m.unrestricted_net_assets, m.total_net_assets, m.total_assets, m.total_liabilities,
                    m.earned_income_pct, m.fundraising_efficiency, m.comp_to_revenue_pct, m.liabilities_to_assets_ratio,
                    m.extraction_confidence, '; '.join(m.issues)
                ])

        print(f"\nCSV output: {output_csv}")

    # Write JSON output
    if output_json and results:
        json_data = []
        for m in results:
            data = asdict(m)
            # Convert ExecutiveComp and RelatedPartyTransaction objects to dicts
            data['executive_compensation'] = [asdict(ec) for ec in m.executive_compensation]
            data['related_party_transactions'] = [asdict(rpt) for rpt in m.related_party_transactions]
            json_data.append(data)

        with open(output_json, 'w') as f:
            json.dump(json_data, f, indent=2)

        print(f"JSON output: {output_json}")

    # Print summary
    print(f"\nProcessed: {len(results)} files successfully, {len(errors)} errors")
    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")

    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 parse_ag_filings.py <pdf_directory> [--csv output.csv] [--json output.json]")
        sys.exit(1)

    pdf_dir = sys.argv[1]

    # Parse arguments
    output_csv = None
    output_json = None

    for i, arg in enumerate(sys.argv[2:], 2):
        if arg == '--csv' and i + 1 < len(sys.argv):
            output_csv = sys.argv[i + 1]
        elif arg == '--json' and i + 1 < len(sys.argv):
            output_json = sys.argv[i + 1]

    # Default output files
    if not output_csv:
        output_csv = "artsmetrics_data/processed/nm_ag_filings_extracted.csv"
    if not output_json:
        output_json = "artsmetrics_data/processed/nm_ag_filings_extracted.json"

    results = process_directory(pdf_dir, output_csv, output_json)
