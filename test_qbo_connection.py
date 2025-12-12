# -*- coding: utf-8 -*-
"""
Test script to verify QBO connection is working
"""
import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

load_dotenv()

from services.qbo.client import QBOClient

def test_connection():
    tenant_id = os.getenv("TENANT_ID")
    
    if not tenant_id:
        print("❌ ERROR: TENANT_ID not found in .env file")
        return
    
    print(f"Testing QBO connection for tenant: {tenant_id}")
    print("-" * 50)
    
    try:
        # Initialize client
        client = QBOClient(tenant_id)
        print("✅ QBO Client initialized")
        
        # Test getting credentials
        access_token, realm_id = client._get_credentials()
        print(f"✅ Credentials retrieved")
        print(f"   Realm ID: {realm_id}")
        print(f"   Access Token: {access_token[:20]}...")
        
        # Test API call - get company info
        print("\nTesting API connection...")
        company_info = client.get_company_info()
        print(f"✅ API connection successful!")
        print(f"   Company Name: {company_info.get('company_name')}")
        print(f"   Legal Name: {company_info.get('legal_name')}")
        
        # Test getting accounts
        print("\nTesting accounts fetch...")
        accounts = client.get_accounts()
        print(f"✅ Retrieved {len(accounts)} accounts")
        if accounts:
            print(f"   Sample account: {accounts[0]['name']} ({accounts[0]['account_type']})")
        
        # Test getting cash balance
        print("\nTesting cash balance...")
        cash_balance = client.get_cash_accounts_balance()
        print(f"✅ Cash balance: ${cash_balance:,.2f}")
        
        # Test getting invoices
        print("\nTesting invoices fetch...")
        invoices = client.get_invoices()
        print(f"✅ Retrieved {len(invoices)} invoices with balances")
        
        print("\n" + "=" * 50)
        print("✅ All tests passed! QBO connection is working.")
        print("=" * 50)
        
    except ValueError as e:
        print(f"❌ ERROR: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check that tenant_integrations table has your tenant_id")
        print("2. Verify tokens are present and not expired")
        print("3. Make sure is_active = true")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_connection()

