#!/usr/bin/env python3
"""
QuickBooks Online Financial Analysis
Pull actual account balances and generate comprehensive analysis
"""
import os
import sys
import requests
import json
from datetime import datetime, date, timedelta

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from supabase import create_client

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

def get_qbo_credentials(tenant_id: str):
    """Get QBO OAuth credentials from database"""
    sb = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))
    result = sb.table('tenant_integrations').select('access_token, refresh_token, realm_id').eq('tenant_id', tenant_id).eq('provider', 'quickbooks').single().execute()
    return result.data

def qbo_query(access_token: str, realm_id: str, query: str):
    """Execute a QBO query"""
    base_url = f"https://quickbooks.api.intuit.com/v3/company/{realm_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    response = requests.get(f"{base_url}/query?query={query}", headers=headers)
    if response.status_code == 200:
        return response.json().get('QueryResponse', {})
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def qbo_report(access_token: str, realm_id: str, report_name: str, params: dict = None):
    """Get a QBO report"""
    base_url = f"https://quickbooks.api.intuit.com/v3/company/{realm_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    url = f"{base_url}/reports/{report_name}"
    if params:
        param_str = "&".join(f"{k}={v}" for k, v in params.items())
        url += f"?{param_str}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Report Error {response.status_code}: {response.text}")
        return None

def main():
    tenant_id = '9aefbb9c-3d1a-41ee-9b40-e1d65ac56056'

    print("Connecting to QuickBooks...")
    creds = get_qbo_credentials(tenant_id)
    access_token = creds['access_token']
    realm_id = creds['realm_id']

    print("=" * 70)
    print("  PHOENIX DESIGN - COMPLETE QUICKBOOKS FINANCIAL ANALYSIS")
    print("  Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 70)

    # 1. ACCOUNT BALANCES
    print("\n" + "─" * 70)
    print("  1. ACCOUNT BALANCES")
    print("─" * 70)

    accounts = qbo_query(access_token, realm_id, "SELECT * FROM Account WHERE Active = true")

    if accounts and accounts.get('Account'):
        bank_accounts = []
        credit_cards = []
        ar_accounts = []
        ap_accounts = []

        for acc in accounts['Account']:
            acc_type = acc.get('AccountType', '')
            name = acc.get('Name', '')
            balance = float(acc.get('CurrentBalance', 0))

            if acc_type == 'Bank':
                bank_accounts.append({'name': name, 'balance': balance})
            elif acc_type == 'Credit Card':
                credit_cards.append({'name': name, 'balance': balance})
            elif acc_type == 'Accounts Receivable':
                ar_accounts.append({'name': name, 'balance': balance})
            elif acc_type == 'Accounts Payable':
                ap_accounts.append({'name': name, 'balance': balance})

        print("\n  💰 BANK ACCOUNTS (Actual Cash):")
        total_cash = 0
        for acc in bank_accounts:
            print(f"     • {acc['name']}: ${acc['balance']:,.2f}")
            total_cash += acc['balance']
        print(f"     ────────────────────────────────")
        print(f"     TOTAL CASH: ${total_cash:,.2f}")

        print("\n  💳 CREDIT CARDS (Outstanding Debt):")
        total_cc = 0
        for acc in credit_cards:
            print(f"     • {acc['name']}: ${acc['balance']:,.2f}")
            total_cc += acc['balance']
        print(f"     ────────────────────────────────")
        print(f"     TOTAL CC DEBT: ${total_cc:,.2f}")

        print("\n  📥 ACCOUNTS RECEIVABLE:")
        total_ar = 0
        for acc in ar_accounts:
            print(f"     • {acc['name']}: ${acc['balance']:,.2f}")
            total_ar += acc['balance']
        print(f"     ────────────────────────────────")
        print(f"     TOTAL AR: ${total_ar:,.2f}")

        print("\n  📤 ACCOUNTS PAYABLE:")
        total_ap = 0
        for acc in ap_accounts:
            print(f"     • {acc['name']}: ${acc['balance']:,.2f}")
            total_ap += acc['balance']
        print(f"     ────────────────────────────────")
        print(f"     TOTAL AP: ${total_ap:,.2f}")

    # 2. PROFIT & LOSS
    print("\n" + "─" * 70)
    print("  2. PROFIT & LOSS (Year to Date)")
    print("─" * 70)

    today = date.today()
    start_of_year = date(today.year, 1, 1)

    pnl = qbo_report(access_token, realm_id, "ProfitAndLoss", {
        "start_date": start_of_year.isoformat(),
        "end_date": today.isoformat()
    })

    if pnl:
        # Parse P&L report
        rows = pnl.get('Rows', {}).get('Row', [])
        for row in rows:
            header = row.get('Header', {})
            if header:
                col_data = header.get('ColData', [])
                if col_data and len(col_data) >= 2:
                    label = col_data[0].get('value', '')
                    value = col_data[1].get('value', '')
                    if label in ['Total Income', 'Gross Profit', 'Total Expenses', 'Net Income', 'Net Operating Income']:
                        try:
                            val = float(value)
                            print(f"     {label}: ${val:,.2f}")
                        except:
                            print(f"     {label}: {value}")

            summary = row.get('Summary', {})
            if summary:
                col_data = summary.get('ColData', [])
                if col_data and len(col_data) >= 2:
                    label = col_data[0].get('value', '')
                    value = col_data[1].get('value', '')
                    if label in ['Total Income', 'Gross Profit', 'Total Expenses', 'Net Income', 'Net Operating Income']:
                        try:
                            val = float(value)
                            print(f"     {label}: ${val:,.2f}")
                        except:
                            print(f"     {label}: {value}")

    # 3. AR AGING
    print("\n" + "─" * 70)
    print("  3. ACCOUNTS RECEIVABLE AGING")
    print("─" * 70)

    ar_aging = qbo_report(access_token, realm_id, "AgedReceivables")

    if ar_aging:
        rows = ar_aging.get('Rows', {}).get('Row', [])
        for row in rows:
            summary = row.get('Summary', {})
            if summary:
                col_data = summary.get('ColData', [])
                if col_data and len(col_data) >= 6:
                    customer = col_data[0].get('value', '')
                    current = col_data[1].get('value', '0')
                    d1_30 = col_data[2].get('value', '0')
                    d31_60 = col_data[3].get('value', '0')
                    d61_90 = col_data[4].get('value', '0')
                    d90plus = col_data[5].get('value', '0')
                    total = col_data[-1].get('value', '0') if len(col_data) > 6 else current

                    if customer and customer != '':
                        print(f"\n     Customer: {customer}")
                        print(f"       Current: ${float(current or 0):,.2f}")
                        print(f"       1-30 days: ${float(d1_30 or 0):,.2f}")
                        print(f"       31-60 days: ${float(d31_60 or 0):,.2f}")
                        print(f"       61-90 days: ${float(d61_90 or 0):,.2f}")
                        print(f"       90+ days: ${float(d90plus or 0):,.2f}")

    # 4. AP AGING
    print("\n" + "─" * 70)
    print("  4. ACCOUNTS PAYABLE AGING")
    print("─" * 70)

    ap_aging = qbo_report(access_token, realm_id, "AgedPayables")

    if ap_aging:
        rows = ap_aging.get('Rows', {}).get('Row', [])
        for row in rows:
            summary = row.get('Summary', {})
            if summary:
                col_data = summary.get('ColData', [])
                if col_data and len(col_data) >= 6:
                    vendor = col_data[0].get('value', '')
                    current = col_data[1].get('value', '0')
                    d1_30 = col_data[2].get('value', '0')
                    d31_60 = col_data[3].get('value', '0')
                    d61_90 = col_data[4].get('value', '0')
                    d90plus = col_data[5].get('value', '0')

                    if vendor and vendor != '':
                        print(f"\n     Vendor: {vendor}")
                        print(f"       Current: ${float(current or 0):,.2f}")
                        print(f"       1-30 days: ${float(d1_30 or 0):,.2f}")
                        print(f"       31-60 days: ${float(d31_60 or 0):,.2f}")
                        print(f"       61-90 days: ${float(d61_90 or 0):,.2f}")
                        print(f"       90+ days: ${float(d90plus or 0):,.2f}")

    # 5. CASH FLOW SUMMARY
    print("\n" + "─" * 70)
    print("  5. CASH POSITION SUMMARY")
    print("─" * 70)

    if accounts and accounts.get('Account'):
        print(f"""
     Current Cash:        ${total_cash:,.2f}
     Credit Card Debt:    ${total_cc:,.2f}
     Accounts Receivable: ${total_ar:,.2f}
     Accounts Payable:    ${total_ap:,.2f}
     ─────────────────────────────────────
     Net Working Capital: ${(total_cash + total_ar - total_cc - total_ap):,.2f}
        """)

    print("\n" + "=" * 70)
    print("  END OF REPORT")
    print("=" * 70)

if __name__ == "__main__":
    main()
