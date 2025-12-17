"""
Test script for QBO transaction sync
"""
import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

load_dotenv()

from services.qbo.sync import QBOSyncService

def test_sync():
    tenant_id = os.getenv("TENANT_ID")
    
    if not tenant_id:
        print("❌ ERROR: TENANT_ID not found in .env file")
        return
    
    print(f"Testing QBO transaction sync for tenant: {tenant_id}")
    print("-" * 60)
    
    try:
        sync_service = QBOSyncService(tenant_id)
        
        # Test incremental sync (or full sync if first time)
        print("\n1. Running incremental sync...")
        result = sync_service.sync_incremental()
        
        print(f"✅ Sync completed!")
        print(f"   Status: {result['status']}")
        print(f"   Total fetched: {result['total_fetched']}")
        print(f"   Stored in DB: {result['synced_count']}")
        print(f"   Date range: {result['start_date']} to {result['end_date']}")
        
        if result.get('errors'):
            print(f"\n⚠️  Errors encountered:")
            for error in result['errors']:
                print(f"   - {error}")
        else:
            print("\n✅ No errors!")
        
        # Show what was synced
        if result['synced_count'] > 0:
            print(f"\n📊 Synced {result['synced_count']} transactions to Supabase")
            print("   Check your Supabase transactions table to verify")
        
        print("\n" + "=" * 60)
        print("✅ Sync test completed successfully!")
        print("=" * 60)
        
    except ValueError as e:
        print(f"❌ ERROR: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check that QBO is connected (tenant_integrations table)")
        print("2. Verify tokens are valid and not expired")
        print("3. Ensure tenant_id is correct")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sync()





