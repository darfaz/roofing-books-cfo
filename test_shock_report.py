#!/usr/bin/env python3
"""Test Shock Report generation end-to-end"""
import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

load_dotenv()

from supabase import create_client

# Initialize Supabase
sb = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

TENANT_ID = "84d3e124-75ab-49b4-9607-6594c082e087"

print("=" * 60)
print("SHOCK REPORT GENERATION TEST")
print("=" * 60)

# Step 1: Check tenant exists
print("\n1. Checking tenant...")
try:
    result = sb.table("tenants").select("*").eq("id", TENANT_ID).execute()
    if result.data:
        print(f"   ✅ Tenant found: {result.data[0].get('name', 'Unknown')}")
    else:
        print(f"   ❌ Tenant not found, creating...")
        sb.table("tenants").insert({
            "id": TENANT_ID,
            "name": "Test Roofing Company",
            "industry": "roofing",
            "owner_salary": 150000,
            "revenue_range": "1M-5M"
        }).execute()
        print("   ✅ Tenant created")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Step 2: Check for transactions
print("\n2. Checking transactions...")
try:
    result = sb.table("transactions").select("*", count="exact").eq("tenant_id", TENANT_ID).execute()
    count = result.count or len(result.data)
    print(f"   Found {count} transactions")

    if count == 0:
        print("   Creating sample transactions for testing...")
        sample_txns = [
            {"tenant_id": TENANT_ID, "description": "Roofing job - Smith residence", "total_amount": 15000, "transaction_type": "invoice", "category": "revenue", "transaction_date": "2024-01-15"},
            {"tenant_id": TENANT_ID, "description": "Roofing job - Johnson commercial", "total_amount": 45000, "transaction_type": "invoice", "category": "revenue", "transaction_date": "2024-02-10"},
            {"tenant_id": TENANT_ID, "description": "Materials purchase - Home Depot", "total_amount": -8500, "transaction_type": "bill", "category": "materials", "transaction_date": "2024-01-20"},
            {"tenant_id": TENANT_ID, "description": "Owner distribution", "total_amount": -10000, "transaction_type": "expense", "category": "owner_distribution", "transaction_date": "2024-02-01"},
            {"tenant_id": TENANT_ID, "description": "Truck payment", "total_amount": -850, "transaction_type": "expense", "category": "vehicle", "transaction_date": "2024-02-05"},
            {"tenant_id": TENANT_ID, "description": "Insurance payment", "total_amount": -2500, "transaction_type": "expense", "category": "insurance", "transaction_date": "2024-02-15"},
            {"tenant_id": TENANT_ID, "description": "Payroll - crew", "total_amount": -12000, "transaction_type": "expense", "category": "labor", "transaction_date": "2024-02-20"},
            {"tenant_id": TENANT_ID, "description": "Roofing job - Williams estate", "total_amount": 28000, "transaction_type": "invoice", "category": "revenue", "transaction_date": "2024-03-05"},
        ]
        for txn in sample_txns:
            sb.table("transactions").insert(txn).execute()
        print(f"   ✅ Created {len(sample_txns)} sample transactions")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Step 3: Generate Shock Report
print("\n3. Generating Shock Report...")
try:
    from services.valuation.shock_report import ShockReportEngine

    engine = ShockReportEngine()
    report = engine.generate_shock_report(TENANT_ID)

    print("\n" + "=" * 60)
    print("SHOCK REPORT RESULTS")
    print("=" * 60)

    if report.get("success"):
        data = report.get("data", {})
        print(f"\n📊 Reported EBITDA: ${data.get('reported_ebitda', 0):,.0f}")
        print(f"📉 Defensible EBITDA: ${data.get('defensible_ebitda', 0):,.0f}")
        print(f"💰 Value Gap: ${data.get('value_gap', 0):,.0f}")
        print(f"\n🎯 Applied Multiple: {data.get('applied_multiple', 0):.2f}x")
        print(f"📈 Target Multiple: {data.get('target_multiple', 0):.2f}x")

        print(f"\n💵 Current Valuation: ${data.get('current_valuation', 0):,.0f}")
        print(f"🎯 Target Valuation: ${data.get('target_valuation', 0):,.0f}")
        print(f"📈 Potential Upside: ${data.get('potential_upside', 0):,.0f}")

        print("\n✅ Shock Report generated successfully!")
    else:
        print(f"❌ Error: {report.get('error', 'Unknown error')}")

except Exception as e:
    import traceback
    print(f"❌ Error generating shock report: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
