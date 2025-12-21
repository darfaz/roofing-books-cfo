#!/usr/bin/env python3
"""Add missing columns to transactions table"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

sb = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

# Check if category column exists by trying a query
try:
    result = sb.table("transactions").select("category").limit(1).execute()
    print("✅ category column already exists")
except Exception as e:
    if "category" in str(e):
        print("❌ category column missing - please add via SQL Editor")
    else:
        print(f"Error: {e}")

# Check customer_id
try:
    result = sb.table("transactions").select("customer_id").limit(1).execute()
    print("✅ customer_id column already exists")
except Exception as e:
    if "customer_id" in str(e):
        print("❌ customer_id column missing")

# Check vendor_id
try:
    result = sb.table("transactions").select("vendor_id").limit(1).execute()
    print("✅ vendor_id column already exists")
except Exception as e:
    if "vendor_id" in str(e):
        print("❌ vendor_id column missing")

print("\n" + "="*50)
print("SQL to run in Supabase SQL Editor:")
print("="*50)
print("""
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS category VARCHAR(100);
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS customer_id UUID;
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS vendor_id UUID;
""")
