#!/usr/bin/env python3
"""
ArtsMetrics Organizational Health Scorecard

Converts parsed NM AG filing metrics into 3-part assessment:
1. Financial Resilience (0-100): ability to sustain operations
2. Governance Risk (0-100): control concentration, compensation practices
3. Program Scale (0-100): organizational size and program focus

Overall score: weighted average (40% resilience, 35% risk mitigation, 25% scale)
"""

import pandas as pd
import json
import sys
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Scorecard:
    fein: str
    org_name: str
    tax_year: int

    # Component scores (0-100)
    financial_resilience: Optional[float] = None
    governance_risk: Optional[float] = None
    program_scale: Optional[float] = None

    # Overall score
    overall_health: Optional[float] = None

    # Sub-factors (for transparency)
    earned_income_pct: Optional[float] = None
    reserve_months: Optional[float] = None
    liabilities_ratio: Optional[float] = None
    comp_to_revenue_pct: Optional[float] = None
    program_expense_pct: Optional[float] = None

    # Health tier
    tier: str = ""

    def assign_tier(self):
        """Assign health tier based on overall score."""
        if self.overall_health is None:
            self.tier = "UNKNOWN"
        elif self.overall_health >= 75:
            self.tier = "STRONG"
        elif self.overall_health >= 60:
            self.tier = "HEALTHY"
        elif self.overall_health >= 45:
            self.tier = "AT-RISK"
        else:
            self.tier = "CRITICAL"


class ScorecardCalculator:
    """Calculate organizational health scores from parsed filing data."""

    # Thresholds for scoring (configurable)
    THRESHOLDS = {
        'excellent_earned_income_pct': 50.0,   # Program revenue as % of total
        'good_earned_income_pct': 30.0,
        'minimum_earned_income_pct': 10.0,

        'minimum_reserve_months': 6,    # Months of operating expenses
        'good_reserve_months': 12,
        'excellent_reserve_months': 18,

        'maximum_liabilities_ratio': 0.3,  # Total liabilities / assets
        'warning_liabilities_ratio': 0.5,

        'maximum_comp_to_revenue': 10.0,  # % of revenue
        'warning_comp_to_revenue': 20.0,
        'critical_comp_to_revenue': 30.0,

        'minimum_program_expense_pct': 65.0,  # Program expenses / total
        'good_program_expense_pct': 75.0,
    }

    @staticmethod
    def calculate_financial_resilience(
        earned_income_pct: Optional[float],
        total_expenses: Optional[float],
        total_net_assets: Optional[float],
        total_assets: Optional[float],
        total_liabilities: Optional[float],
    ) -> tuple[float, dict]:
        """
        Score financial resilience (0-100).

        Factors:
        1. Earned income % (diversification): 0-40 points
        2. Reserve strength (months of expenses): 0-40 points
        3. Solvency (liabilities-to-assets): 0-20 points
        """
        score = 0
        factors = {}

        # Earned income score (0-40)
        # Higher earned income = less dependent on fundraising volatility
        if earned_income_pct is not None:
            if earned_income_pct >= 50:
                earned_score = 40
            elif earned_income_pct >= 30:
                earned_score = 30
            elif earned_income_pct >= 10:
                earned_score = 15
            else:
                earned_score = 5
            score += earned_score
            factors['earned_income_score'] = earned_score
        else:
            factors['earned_income_score'] = 0

        # Reserve strength (0-40)
        # Calculate months of operating expenses in reserves
        if total_net_assets is not None and total_expenses is not None and total_expenses > 0:
            monthly_expenses = total_expenses / 12
            reserve_months = total_net_assets / monthly_expenses if monthly_expenses > 0 else 0

            if reserve_months >= 18:
                reserve_score = 40
            elif reserve_months >= 12:
                reserve_score = 30
            elif reserve_months >= 6:
                reserve_score = 15
            elif reserve_months > 0:
                reserve_score = 5
            else:
                reserve_score = 0

            score += reserve_score
            factors['reserve_score'] = reserve_score
            factors['reserve_months'] = round(reserve_months, 1)
        else:
            factors['reserve_score'] = 0
            factors['reserve_months'] = None

        # Solvency (0-20)
        # Lower liabilities-to-assets = better financial position
        if total_assets is not None and total_liabilities is not None and total_assets > 0:
            liabilities_ratio = total_liabilities / total_assets

            if liabilities_ratio <= 0.2:
                solvency_score = 20
            elif liabilities_ratio <= 0.35:
                solvency_score = 15
            elif liabilities_ratio <= 0.5:
                solvency_score = 10
            elif liabilities_ratio <= 0.75:
                solvency_score = 5
            else:
                solvency_score = 0

            score += solvency_score
            factors['solvency_score'] = solvency_score
            factors['liabilities_ratio'] = round(liabilities_ratio, 2)
        else:
            factors['solvency_score'] = 0
            factors['liabilities_ratio'] = None

        return min(score, 100), factors

    @staticmethod
    def calculate_governance_risk(
        comp_to_revenue_pct: Optional[float],
        program_expense_pct: Optional[float],
        executive_compensation_count: int = 1,
    ) -> tuple[float, dict]:
        """
        Score governance risk mitigation (0-100).
        Higher score = better governance / lower risk.

        Factors:
        1. Compensation concentration (0-50): comp-to-revenue ratio
        2. Program alignment (0-50): program expenses as % of total
        """
        score = 50  # Start at 50 (neutral) for partial data

        factors = {}

        # Compensation risk (0-50)
        if comp_to_revenue_pct is not None:
            if comp_to_revenue_pct <= 5:
                comp_score = 50
            elif comp_to_revenue_pct <= 10:
                comp_score = 40
            elif comp_to_revenue_pct <= 15:
                comp_score = 25
            elif comp_to_revenue_pct <= 25:
                comp_score = 10
            else:
                comp_score = 0

            score = comp_score  # Replace neutral score
            factors['comp_score'] = comp_score
        else:
            factors['comp_score'] = 50

        # Program alignment (0-50)
        # Higher program spending = better mission alignment
        if program_expense_pct is not None:
            if program_expense_pct >= 75:
                program_score = 50
            elif program_expense_pct >= 65:
                program_score = 40
            elif program_expense_pct >= 50:
                program_score = 20
            elif program_expense_pct >= 35:
                program_score = 10
            else:
                program_score = 0

            score = (score + program_score) / 2  # Average the two factors
            factors['program_score'] = program_score
        else:
            factors['program_score'] = 50

        return round(min(score, 100), 1), factors

    @staticmethod
    def calculate_program_scale(
        total_revenue: Optional[float],
        program_expense_pct: Optional[float],
    ) -> tuple[float, dict]:
        """
        Score program scale (0-100).
        Reflects organizational size and scope.

        Factors:
        1. Organizational size (0-60): total annual revenue
        2. Mission centrality (0-40): program expenses % of total
        """
        score = 0
        factors = {}

        # Revenue scale (0-60)
        # Thresholds reflect NM arts sector (median ~$100K, large ~$500K+)
        if total_revenue is not None:
            if total_revenue >= 500000:
                revenue_score = 60
            elif total_revenue >= 200000:
                revenue_score = 45
            elif total_revenue >= 100000:
                revenue_score = 30
            elif total_revenue >= 50000:
                revenue_score = 15
            elif total_revenue > 0:
                revenue_score = 5
            else:
                revenue_score = 0

            score += revenue_score
            factors['revenue_score'] = revenue_score
            factors['revenue_category'] = 'Large' if total_revenue >= 200000 else ('Medium' if total_revenue >= 100000 else 'Small')
        else:
            factors['revenue_score'] = 0
            factors['revenue_category'] = 'Unknown'

        # Mission centrality (0-40)
        if program_expense_pct is not None:
            if program_expense_pct >= 80:
                mission_score = 40
            elif program_expense_pct >= 70:
                mission_score = 30
            elif program_expense_pct >= 60:
                mission_score = 20
            elif program_expense_pct >= 50:
                mission_score = 10
            else:
                mission_score = 0

            score += mission_score
            factors['mission_score'] = mission_score
        else:
            factors['mission_score'] = 20  # Neutral for missing data

        return min(score, 100), factors

    def calculate(self, row: pd.Series) -> Scorecard:
        """Calculate health scorecard for a filing."""

        # Extract metrics
        fein = str(row['FEIN'])
        org_name = row['Organization Name']
        tax_year = int(row['Tax Year'])
        total_revenue = row.get('Total Revenue')
        total_expenses = row.get('Total Expenses')
        total_net_assets = row.get('Total Net Assets')
        total_assets = row.get('Total Assets')
        total_liabilities = row.get('Total Liabilities')
        earned_income_pct = row.get('Earned Income %')
        comp_to_revenue_pct = row.get('Comp-to-Revenue %')

        # Calculate program expense %
        program_expense_pct = None
        if row.get('Program Expenses') is not None and total_expenses is not None and total_expenses > 0:
            program_expense_pct = (row['Program Expenses'] / total_expenses) * 100

        # Calculate component scores
        resilience_score, resilience_factors = self.calculate_financial_resilience(
            earned_income_pct, total_expenses, total_net_assets, total_assets, total_liabilities
        )

        governance_score, governance_factors = self.calculate_governance_risk(
            comp_to_revenue_pct, program_expense_pct
        )

        scale_score, scale_factors = self.calculate_program_scale(
            total_revenue, program_expense_pct
        )

        # Calculate overall score (weighted average)
        # 40% financial resilience, 35% governance, 25% scale
        overall_score = (
            (resilience_score * 0.40) +
            (governance_score * 0.35) +
            (scale_score * 0.25)
        )

        scorecard = Scorecard(
            fein=fein,
            org_name=org_name,
            tax_year=tax_year,
            financial_resilience=round(resilience_score, 1),
            governance_risk=round(governance_score, 1),
            program_scale=round(scale_score, 1),
            overall_health=round(overall_score, 1),
            earned_income_pct=round(earned_income_pct, 1) if earned_income_pct else None,
            reserve_months=resilience_factors.get('reserve_months'),
            liabilities_ratio=resilience_factors.get('liabilities_ratio'),
            comp_to_revenue_pct=round(comp_to_revenue_pct, 1) if comp_to_revenue_pct else None,
            program_expense_pct=round(program_expense_pct, 1) if program_expense_pct else None,
        )
        scorecard.assign_tier()
        return scorecard


def process_csv(csv_path: str, output_csv: str = None, output_json: str = None):
    """Process extracted metrics CSV and generate scorecards."""

    df = pd.read_csv(csv_path)
    calculator = ScorecardCalculator()

    scorecards = []
    for _, row in df.iterrows():
        scorecard = calculator.calculate(row)
        scorecards.append(scorecard)

    # Write CSV
    if output_csv:
        output_df = pd.DataFrame([asdict(sc) for sc in scorecards])
        output_df.to_csv(output_csv, index=False)
        print(f"Scorecard CSV: {output_csv}")

    # Write JSON
    if output_json:
        with open(output_json, 'w') as f:
            json.dump([asdict(sc) for sc in scorecards], f, indent=2)
        print(f"Scorecard JSON: {output_json}")

    # Print summary
    print(f"\nProcessed {len(scorecards)} organizations")
    print("\nTier Summary:")
    tier_counts = pd.DataFrame([asdict(sc) for sc in scorecards])['tier'].value_counts()
    for tier in ['STRONG', 'HEALTHY', 'AT-RISK', 'CRITICAL', 'UNKNOWN']:
        count = tier_counts.get(tier, 0)
        if count > 0:
            print(f"  {tier}: {count}")

    return scorecards


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scorecard.py <extracted_csv> [--csv output.csv] [--json output.json]")
        sys.exit(1)

    csv_path = sys.argv[1]

    output_csv = None
    output_json = None

    for i, arg in enumerate(sys.argv[2:], 2):
        if arg == '--csv' and i + 1 < len(sys.argv):
            output_csv = sys.argv[i + 1]
        elif arg == '--json' and i + 1 < len(sys.argv):
            output_json = sys.argv[i + 1]

    # Default outputs
    if not output_csv:
        output_csv = "artsmetrics_data/processed/scorecards.csv"
    if not output_json:
        output_json = "artsmetrics_data/processed/scorecards.json"

    process_csv(csv_path, output_csv, output_json)
