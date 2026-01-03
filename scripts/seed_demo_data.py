#!/usr/bin/env python3
"""
Seed Demo Data for CrewCFO
==========================
Creates a complete demo dataset for "Apex Roofing Solutions" showing:
- 12 months of realistic financial transactions
- 5 identified profit leaks
- Industry-typical cost structure with problems visible

Demo Company Profile:
- Revenue: $3.5M annual (~$292K/month)
- Gross Margin: 22% (below industry avg of 25-35%)
- Net Margin: 7% (below good target of 10-15%)
- 5 Profit Leaks totaling ~$175K recoverable annually

Based on Research:
- Materials: 48.5% of revenue (industry benchmark)
- Labor: 18.5% wages + 18.3% contracted
- Overhead: 25-30% of revenue
- Industry net margin: 6-12% (our demo: 7% with leaks)
"""

import os
import sys
import random
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("Error: SUPABASE_URL and SUPABASE_SERVICE_KEY required")
    sys.exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

DEMO_TENANT_ID = "demo-0000-0000-0000-000000000001"

# ============================================================
# MONTHLY FINANCIAL PROFILE ($3.5M annual = ~$292K/month avg)
# Seasonal variation: slower in Jan-Feb, peak in spring/summer
# ============================================================

MONTHLY_REVENUE_PATTERN = {
    1: 0.70,   # January - slow
    2: 0.75,   # February - slow
    3: 0.95,   # March - picking up
    4: 1.15,   # April - busy
    5: 1.25,   # May - peak
    6: 1.20,   # June - peak
    7: 1.10,   # July - hot
    8: 1.05,   # August - hot
    9: 1.10,   # September - storm season
    10: 1.05,  # October - fall
    11: 0.85,  # November - slowing
    12: 0.85,  # December - holidays
}

BASE_MONTHLY_REVENUE = 291667  # $3.5M / 12

# ============================================================
# EXPENSE CATEGORIES WITH PROFIT LEAKS
# ============================================================

# Job Costs (COGS) - ~65% of revenue
JOB_COST_CATEGORIES = {
    "materials": {"pct": 0.35, "vendors": ["ABC Supply", "Beacon Building", "SRS Distribution", "Home Depot Pro"]},
    "direct_labor": {"pct": 0.18, "vendors": ["Payroll - Crews"]},
    "subcontractors": {"pct": 0.08, "vendors": ["Superior Gutters", "Flash Masters", "Skylight Pros"]},
    "equipment_rental": {"pct": 0.02, "vendors": ["United Rentals", "Sunbelt Rentals"]},
    "disposal": {"pct": 0.02, "vendors": ["Waste Management", "Republic Services"]},
}

# Overhead - ~28% of revenue (higher than healthy 25%)
OVERHEAD_CATEGORIES = {
    "payroll_office": {"pct": 0.04, "vendors": ["Payroll - Admin"]},
    "payroll_owner": {"pct": 0.05, "vendors": ["Owner Draw"]},  # PROFIT LEAK: $180K/yr = 5.1%
    "payroll_spouse": {"pct": 0.013, "vendors": ["Payroll - Admin"]},  # PROFIT LEAK: $45K/yr
    "insurance": {"pct": 0.035, "vendors": ["State Farm Commercial", "Hartford Insurance"]},
    "vehicle_fleet": {"pct": 0.02, "vendors": ["Ford Fleet", "Fuel - Shell", "Fuel - Exxon"]},
    "vehicle_personal": {"pct": 0.005, "vendors": ["BMW Financial"]},  # PROFIT LEAK: Personal BMW
    "marketing": {"pct": 0.02, "vendors": ["Google Ads", "Facebook Ads", "Angi Leads", "Home Advisor"]},
    "professional_fees": {"pct": 0.01, "vendors": ["Smith & Associates CPA", "Legal Services LLC"]},
    "office": {"pct": 0.015, "vendors": ["Office Depot", "Verizon Business", "Microsoft 365"]},
    "software": {"pct": 0.005, "vendors": ["JobNimbus", "QuickBooks", "CompanyCam"]},
    "utilities": {"pct": 0.008, "vendors": ["TXU Energy", "AT&T", "Spectrum Business"]},
    "rent": {"pct": 0.02, "vendors": ["Industrial Warehouse LLC"]},
    "entertainment": {"pct": 0.003, "vendors": ["Lakewood Country Club"]},  # PROFIT LEAK: Country club
    "misc": {"pct": 0.01, "vendors": ["Various"]},
}

# ============================================================
# TRANSACTION GENERATORS
# ============================================================

def generate_transactions():
    """Generate 12 months of demo transactions."""
    transactions = []

    # Generate for last 12 months
    today = datetime.now()

    for month_offset in range(12, 0, -1):
        # Calculate month dates
        month_date = today - timedelta(days=month_offset * 30)
        year = month_date.year
        month = month_date.month

        # Get seasonal revenue for this month
        seasonality = MONTHLY_REVENUE_PATTERN.get(month, 1.0)
        monthly_revenue = int(BASE_MONTHLY_REVENUE * seasonality * random.uniform(0.95, 1.05))

        # Generate revenue transactions (invoices)
        transactions.extend(generate_revenue(year, month, monthly_revenue))

        # Generate job cost transactions
        transactions.extend(generate_job_costs(year, month, monthly_revenue))

        # Generate overhead transactions
        transactions.extend(generate_overhead(year, month, monthly_revenue))

    return transactions


def generate_revenue(year: int, month: int, monthly_total: int):
    """Generate revenue transactions (customer invoices)."""
    transactions = []

    # Revenue mix: 70% residential, 30% commercial
    residential_pct = 0.70
    commercial_pct = 0.30

    # Residential jobs: $8K-25K each
    residential_revenue = int(monthly_total * residential_pct)
    residential_job_size = random.randint(8000, 25000)
    num_residential = max(1, residential_revenue // residential_job_size)

    for i in range(num_residential):
        job_amount = random.randint(8000, 25000)
        day = random.randint(1, 28)
        transactions.append({
            "tenant_id": DEMO_TENANT_ID,
            "date": f"{year}-{month:02d}-{day:02d}",
            "description": f"Roof replacement - {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis'])} residence",
            "amount": job_amount,
            "transaction_type": "income",
            "category": "roofing_services",
            "account_type": "Revenue",
            "vendor_name": None,
            "confidence": 0.95,
            "classification": "revenue",
            "qbo_id": f"INV-{uuid4().hex[:8].upper()}",
        })

    # Commercial jobs: $25K-150K each
    commercial_revenue = int(monthly_total * commercial_pct)
    commercial_job_size = random.randint(25000, 80000)
    num_commercial = max(1, commercial_revenue // commercial_job_size)

    commercial_customers = [
        "Riverside Property Management",
        "Texas Commercial Realty",
        "Summit Builders Inc",
        "Metro Development Group",
        "Lone Star Properties",
    ]

    for i in range(num_commercial):
        job_amount = random.randint(25000, 80000)
        day = random.randint(1, 28)
        transactions.append({
            "tenant_id": DEMO_TENANT_ID,
            "date": f"{year}-{month:02d}-{day:02d}",
            "description": f"Commercial roofing - {random.choice(commercial_customers)}",
            "amount": job_amount,
            "transaction_type": "income",
            "category": "commercial_roofing",
            "account_type": "Revenue",
            "vendor_name": None,
            "confidence": 0.95,
            "classification": "revenue",
            "qbo_id": f"INV-{uuid4().hex[:8].upper()}",
        })

    return transactions


def generate_job_costs(year: int, month: int, monthly_revenue: int):
    """Generate job cost (COGS) transactions."""
    transactions = []

    for category, config in JOB_COST_CATEGORIES.items():
        category_total = int(monthly_revenue * config["pct"] * random.uniform(0.95, 1.05))
        vendors = config["vendors"]

        # Split across vendors
        num_transactions = random.randint(3, 8) if category == "materials" else random.randint(1, 3)

        for _ in range(num_transactions):
            amount = int(category_total / num_transactions * random.uniform(0.8, 1.2))
            vendor = random.choice(vendors)
            day = random.randint(1, 28)

            transactions.append({
                "tenant_id": DEMO_TENANT_ID,
                "date": f"{year}-{month:02d}-{day:02d}",
                "description": f"{category.replace('_', ' ').title()} - {vendor}",
                "amount": -abs(amount),  # Negative for expenses
                "transaction_type": "expense",
                "category": category,
                "account_type": "Cost of Goods Sold",
                "vendor_name": vendor,
                "confidence": 0.88,
                "classification": "job_cost",
                "qbo_id": f"EXP-{uuid4().hex[:8].upper()}",
            })

    return transactions


def generate_overhead(year: int, month: int, monthly_revenue: int):
    """Generate overhead transactions including profit leaks."""
    transactions = []

    for category, config in OVERHEAD_CATEGORIES.items():
        category_total = int(monthly_revenue * config["pct"] * random.uniform(0.95, 1.05))
        vendors = config["vendors"]

        # Special handling for profit leak categories
        if category == "payroll_owner":
            # Owner salary: $15,000/month ($180K/year) - above market
            transactions.append({
                "tenant_id": DEMO_TENANT_ID,
                "date": f"{year}-{month:02d}-15",
                "description": "Owner Salary - Mike Thompson",
                "amount": -15000,
                "transaction_type": "expense",
                "category": "payroll",
                "account_type": "Operating Expense",
                "vendor_name": "Payroll",
                "confidence": 0.92,
                "classification": "overhead",
                "qbo_id": f"PAY-{uuid4().hex[:8].upper()}",
            })
            continue

        if category == "payroll_spouse":
            # Spouse salary: $3,750/month ($45K/year) - partially personal
            transactions.append({
                "tenant_id": DEMO_TENANT_ID,
                "date": f"{year}-{month:02d}-15",
                "description": "Admin Salary - Sarah Thompson",
                "amount": -3750,
                "transaction_type": "expense",
                "category": "payroll",
                "account_type": "Operating Expense",
                "vendor_name": "Payroll",
                "confidence": 0.85,
                "classification": "overhead",
                "qbo_id": f"PAY-{uuid4().hex[:8].upper()}",
            })
            continue

        if category == "vehicle_personal":
            # Personal BMW: $1,500/month ($18K/year)
            transactions.append({
                "tenant_id": DEMO_TENANT_ID,
                "date": f"{year}-{month:02d}-05",
                "description": "Vehicle Lease - BMW X5",
                "amount": -1500,
                "transaction_type": "expense",
                "category": "vehicle",
                "account_type": "Operating Expense",
                "vendor_name": "BMW Financial Services",
                "confidence": 0.75,  # Lower confidence - mixed use
                "classification": "overhead",
                "qbo_id": f"AUTO-{uuid4().hex[:8].upper()}",
            })
            continue

        if category == "entertainment":
            # Country club: $1,000/month ($12K/year)
            transactions.append({
                "tenant_id": DEMO_TENANT_ID,
                "date": f"{year}-{month:02d}-01",
                "description": "Lakewood Country Club - Monthly Dues",
                "amount": -1000,
                "transaction_type": "expense",
                "category": "entertainment",
                "account_type": "Operating Expense",
                "vendor_name": "Lakewood Country Club",
                "confidence": 0.70,  # Low confidence - personal?
                "classification": "overhead",
                "qbo_id": f"ENT-{uuid4().hex[:8].upper()}",
            })
            continue

        # Regular overhead categories
        num_transactions = random.randint(1, 3)

        for _ in range(num_transactions):
            amount = int(category_total / num_transactions * random.uniform(0.8, 1.2))
            vendor = random.choice(vendors)
            day = random.randint(1, 28)

            transactions.append({
                "tenant_id": DEMO_TENANT_ID,
                "date": f"{year}-{month:02d}-{day:02d}",
                "description": f"{vendor}",
                "amount": -abs(amount),
                "transaction_type": "expense",
                "category": category.replace("_", " "),
                "account_type": "Operating Expense",
                "vendor_name": vendor,
                "confidence": random.uniform(0.82, 0.95),
                "classification": "overhead",
                "qbo_id": f"EXP-{uuid4().hex[:8].upper()}",
            })

    return transactions


def seed_transactions():
    """Seed all demo transactions to database."""
    print("Generating demo transactions...")
    transactions = generate_transactions()

    print(f"Generated {len(transactions)} transactions")

    # Delete existing demo transactions
    print("Clearing existing demo data...")
    supabase.table("transactions").delete().eq("tenant_id", DEMO_TENANT_ID).execute()

    # Insert in batches
    batch_size = 100
    for i in range(0, len(transactions), batch_size):
        batch = transactions[i:i + batch_size]
        supabase.table("transactions").insert(batch).execute()
        print(f"  Inserted batch {i // batch_size + 1}/{(len(transactions) + batch_size - 1) // batch_size}")

    print(f"Seeded {len(transactions)} demo transactions")

    # Calculate and display summary
    total_revenue = sum(t["amount"] for t in transactions if t["amount"] > 0)
    total_expenses = sum(t["amount"] for t in transactions if t["amount"] < 0)

    print("\n=== DEMO COMPANY SUMMARY ===")
    print(f"Company: Apex Roofing Solutions")
    print(f"Period: Last 12 months")
    print(f"Total Revenue: ${total_revenue:,.0f}")
    print(f"Total Expenses: ${abs(total_expenses):,.0f}")
    print(f"Net Income: ${total_revenue + total_expenses:,.0f}")
    print(f"Net Margin: {((total_revenue + total_expenses) / total_revenue * 100):.1f}%")
    print(f"Gross Margin: ~{((total_revenue - abs(total_expenses) * 0.65) / total_revenue * 100):.1f}%")
    print("\n=== IDENTIFIED PROFIT LEAKS ===")
    print("1. Owner salary above market: $60K/year excess")
    print("2. Spouse salary (unclear duties): $30K/year")
    print("3. Personal vehicle (BMW): $18K/year")
    print("4. Country club membership: $12K/year")
    print("5. Low gross margin (pricing/inefficiency): ~$45K/year recoverable")
    print("TOTAL RECOVERABLE: ~$165K/year")


def main():
    """Main entry point."""
    print("=" * 60)
    print("CrewCFO Demo Data Seeder")
    print("=" * 60)

    # Check if demo tenant exists
    result = supabase.table("tenants").select("id").eq("id", DEMO_TENANT_ID).execute()

    if not result.data:
        print("Creating demo tenant...")
        supabase.table("tenants").insert({
            "id": DEMO_TENANT_ID,
            "company_name": "Apex Roofing Solutions",
            "industry": "Roofing Contractor",
            "annual_revenue": 3500000,
            "employee_count": 12,
        }).execute()
        print("Demo tenant created: Apex Roofing Solutions")
    else:
        print("Demo tenant already exists")

    # Seed transactions
    seed_transactions()

    print("\n" + "=" * 60)
    print("Demo data seeding complete!")
    print("Demo Tenant ID:", DEMO_TENANT_ID)
    print("=" * 60)


if __name__ == "__main__":
    main()
