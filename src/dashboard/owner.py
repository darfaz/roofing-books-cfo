"""
Owner Dashboard - "Am I okay?" view
Streamlit application for roofing contractor owners
"""
import os
import sys
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.qbo.client import QBOClient

# Load environment
load_dotenv()

# Page config
st.set_page_config(
    page_title="CrewCFO | Owner Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to match marketing website design
st.markdown("""
<style>
    /* Main theme - match marketing website colors */
    .main > div {
        padding-top: 1rem;
        background-color: #0a0f1a;
    }
    
    [data-testid="stAppViewContainer"] {
        background-color: #0a0f1a;
        color: white;
    }
    
    [data-testid="stHeader"] {
        background-color: #0a0f1a;
        height: 0;
    }
    
    [data-testid="stSidebar"] {
        background-color: #0f172a;
    }
    
    /* Typography */
    h1, h2, h3 {
        color: white !important;
        font-weight: 700;
    }
    
    /* Metrics cards - match website card style */
    [data-testid="metric-container"] {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    
    [data-testid="metric-container"] label {
        color: #94a3b8 !important;
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: white !important;
        font-size: 1.875rem;
        font-weight: 700;
    }
    
    [data-testid="metric-container"] [data-testid="metric-delta"] {
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    /* Health banner */
    .health-banner {
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        color: white;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    .health-banner.healthy {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(52, 211, 153, 0.1) 100%);
        border-color: rgba(16, 185, 129, 0.3);
    }
    
    .health-banner.watch {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(251, 191, 36, 0.1) 100%);
        border-color: rgba(245, 158, 11, 0.3);
    }
    
    .health-banner.critical {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(248, 113, 113, 0.1) 100%);
        border-color: rgba(239, 68, 68, 0.3);
    }
    
    .health-banner h2 {
        margin: 0;
        font-size: 1.875rem;
        font-weight: 700;
    }
    
    .health-banner p {
        margin: 0.5rem 0 0 0;
        color: #cbd5e1;
        font-size: 1rem;
    }
    
    /* Charts background */
    [data-testid="stPlotlyChart"] {
        background-color: #0f172a;
        border-radius: 12px;
        border: 1px solid #1e293b;
        padding: 1rem;
    }
    
    /* Subheaders */
    .stSubheader {
        color: white !important;
        font-weight: 600;
        padding: 1rem 0 0.5rem 0;
    }
    
    /* Action items styling */
    .action-item {
        background: #0f172a;
        border: 1px solid #1e293b;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
    }
    
    .action-priority {
        font-size: 1.25rem;
        line-height: 1;
    }
    
    .action-text {
        flex: 1;
        color: #e2e8f0;
        font-size: 0.875rem;
        line-height: 1.4;
    }
    
    .action-impact {
        color: #94a3b8;
        font-size: 0.75rem;
        text-transform: uppercase;
        font-weight: 500;
    }
    
    /* Dividers */
    hr {
        border: none;
        height: 1px;
        background: #1e293b;
        margin: 2rem 0;
    }
    
    /* Warning/info boxes */
    [data-testid="stAlert"] {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 8px;
        color: white;
    }
    
    /* Caption text */
    .caption {
        color: #64748b;
        font-size: 0.875rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA FUNCTIONS
# ============================================================

@st.cache_resource
def get_supabase():
    """Get Supabase client"""
    # Use service key for dashboard to allow full access
    # In production, use RLS policies and anon key with proper auth
    service_key = os.getenv("SUPABASE_SERVICE_KEY", "")
    anon_key = os.getenv("SUPABASE_ANON_KEY", "")
    # Prefer service key if available, fallback to anon key
    key = service_key if service_key else anon_key
    return create_client(
        os.getenv("SUPABASE_URL", ""),
        key
    )

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cash_position(tenant_id: str):
    """Get latest cash position"""
    supabase = get_supabase()
    result = supabase.table("cash_positions")\
        .select("*")\
        .eq("tenant_id", tenant_id)\
        .order("position_date", desc=True)\
        .limit(2)\
        .execute()
    
    if not result.data:
        return None
    
    current = result.data[0]
    previous = result.data[1] if len(result.data) > 1 else None
    
    # Calculate week-over-week change
    if previous:
        change = (current["total_cash"] - previous["total_cash"]) / previous["total_cash"]
    else:
        change = 0
    
    return {
        **current,
        "change_wow": change
    }

@st.cache_data(ttl=300)
def get_revenue_mtd(tenant_id: str):
    """Get month-to-date revenue"""
    supabase = get_supabase()
    
    # First day of current month
    today = datetime.now()
    month_start = today.replace(day=1).strftime("%Y-%m-%d")
    
    result = supabase.table("transactions")\
        .select("total_amount")\
        .eq("tenant_id", tenant_id)\
        .eq("transaction_type", "invoice")\
        .gte("transaction_date", month_start)\
        .execute()
    
    total = sum(float(t["total_amount"]) for t in result.data)
    
    # Get target (could be from settings, using 100K as default)
    target = 100000
    
    return {
        "mtd": total,
        "target": target,
        "progress": total / target if target > 0 else 0
    }

@st.cache_data(ttl=300)
def get_ar_aging(tenant_id: str):
    """Get AR aging buckets"""
    supabase = get_supabase()
    
    result = supabase.table("transactions")\
        .select("total_amount, transaction_date")\
        .eq("tenant_id", tenant_id)\
        .eq("transaction_type", "invoice")\
        .neq("status", "voided")\
        .execute()
    
    buckets = {"Current": 0, "31-60": 0, "61-90": 0, "90+": 0}
    today = datetime.now().date()
    
    for txn in result.data:
        txn_date = datetime.fromisoformat(txn["transaction_date"]).date()
        days = (today - txn_date).days
        amount = float(txn["total_amount"])
        
        if days <= 30:
            buckets["Current"] += amount
        elif days <= 60:
            buckets["31-60"] += amount
        elif days <= 90:
            buckets["61-90"] += amount
        else:
            buckets["90+"] += amount
    
    return buckets

@st.cache_data(ttl=300)
def get_forecast(tenant_id: str):
    """Get 13-week cash forecast"""
    supabase = get_supabase()
    
    result = supabase.table("cash_forecasts")\
        .select("*")\
        .eq("tenant_id", tenant_id)\
        .order("forecast_date", desc=True)\
        .order("week_number")\
        .limit(13)\
        .execute()
    
    return result.data

@st.cache_data(ttl=300)
def get_jobs_profitability(tenant_id: str):
    """Get recent jobs with profitability"""
    supabase = get_supabase()
    
    result = supabase.table("jobs")\
        .select("job_number, name, contract_amount, actual_cost, actual_margin_pct, status")\
        .eq("tenant_id", tenant_id)\
        .in_("status", ["in_progress", "completed"])\
        .order("created_at", desc=True)\
        .limit(20)\
        .execute()
    
    return result.data

@st.cache_data(ttl=300)
def get_action_items(tenant_id: str):
    """Get priority action items"""
    # In a real app, this would query overdue items, low margin jobs, etc.
    # For now, return mock data
    return [
        {"priority": ":red_circle:", "item": "Follow up on Johnson invoice ($15,000) - 45 days overdue", "impact": "High"},
        {"priority": ":orange_circle:", "item": "Review Smith job margins (currently 18%)", "impact": "Medium"},
        {"priority": ":green_circle:", "item": "Send estimate follow-up to Williams prospect", "impact": "Low"},
    ]

# ============================================================
# QBO DATA FUNCTIONS
# ============================================================

@st.cache_resource
def get_qbo_client(tenant_id: str):
    """Get QBO client instance"""
    try:
        return QBOClient(tenant_id)
    except Exception as e:
        st.error(f"Error connecting to QBO: {str(e)}")
        return None

@st.cache_data(ttl=300)
def get_qbo_cash_position(tenant_id: str):
    """Get cash position from QBO"""
    client = get_qbo_client(tenant_id)
    if not client:
        return None
    
    try:
        total_cash = client.get_cash_accounts_balance()
        
        # Calculate AR total from invoices (only unpaid)
        today = datetime.now().date()
        start_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
        invoices = client.get_invoices(start_date, end_date)
        # Only count invoices with outstanding balance
        ar_total = sum(inv.get("balance", 0) for inv in invoices if inv.get("balance", 0) > 0)
        
        # Calculate AP total from bills (only unpaid)
        bills = client.get_bills(start_date, end_date)
        # Only count bills with outstanding balance
        ap_total = sum(bill.get("balance", 0) for bill in bills if bill.get("balance", 0) > 0)
        
        # Calculate week-over-week change (simplified - would need historical data)
        # For now, just return current balance
        return {
            "total_cash": total_cash,
            "change_wow": 0.0,  # TODO: Calculate from historical data
            "runway_weeks": 12,  # TODO: Calculate from expenses
            "ar_total": ar_total,
            "ap_total": ap_total
        }
    except Exception as e:
        st.error(f"Error fetching cash position: {str(e)}")
        return None

@st.cache_data(ttl=300)
def get_qbo_revenue_mtd(tenant_id: str):
    """Get month-to-date revenue from QBO"""
    client = get_qbo_client(tenant_id)
    if not client:
        return None
    
    try:
        today = datetime.now()
        month_start = today.replace(day=1).strftime("%Y-%m-%d")
        revenue_data = client.get_revenue_mtd(month_start)
        
        return {
            "mtd": revenue_data.get("mtd", 0),
            "target": revenue_data.get("target", 100000),
            "progress": revenue_data.get("mtd", 0) / revenue_data.get("target", 100000) if revenue_data.get("target", 0) > 0 else 0
        }
    except Exception as e:
        st.error(f"Error fetching revenue: {str(e)}")
        return None

@st.cache_data(ttl=300)
def get_qbo_ar_aging(tenant_id: str):
    """Get AR aging from QBO invoices"""
    client = get_qbo_client(tenant_id)
    if not client:
        return None
    
    try:
        # Get invoices from last year
        today = datetime.now().date()
        start_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
        
        invoices = client.get_invoices(start_date, end_date)
        
        buckets = {"Current": 0, "31-60": 0, "61-90": 0, "90+": 0}
        
        for inv in invoices:
            txn_date_str = inv.get("txn_date")
            if not txn_date_str:
                continue
            
            try:
                txn_date = datetime.strptime(txn_date_str, "%Y-%m-%d").date()
                days = (today - txn_date).days
                balance = inv.get("balance", 0)
                
                if days <= 30:
                    buckets["Current"] += balance
                elif days <= 60:
                    buckets["31-60"] += balance
                elif days <= 90:
                    buckets["61-90"] += balance
                else:
                    buckets["90+"] += balance
            except (ValueError, TypeError):
                continue
        
        return buckets
    except Exception as e:
        st.error(f"Error fetching AR aging: {str(e)}")
        return None

@st.cache_data(ttl=300)
def get_qbo_forecast(tenant_id: str):
    """Get cash forecast (simplified from QBO data)"""
    client = get_qbo_client(tenant_id)
    if not client:
        return None
    
    try:
        # Get current cash balance
        current_cash = client.get_cash_accounts_balance()
        
        # Simple forecast - in production this would use actual forecast logic
        forecast = []
        for i in range(13):
            week_start = datetime.now() + timedelta(weeks=i)
            # Simplified projection
            pessimistic = current_cash * (0.95 ** i)
            baseline = current_cash * (1.02 ** i)
            optimistic = current_cash * (1.08 ** i)
            
            forecast.append({
                "week_number": i,
                "week_start_date": week_start.strftime("%Y-%m-%d"),
                "pessimistic_cash": pessimistic,
                "ending_cash": baseline,
                "optimistic_cash": optimistic
            })
        
        return forecast
    except Exception as e:
        st.error(f"Error generating forecast: {str(e)}")
        return None

# ============================================================
# MOCK DATA (remove once connected to real DB)
# ============================================================

def get_mock_data():
    """Mock data for demo purposes"""
    return {
        "cash_position": {
            "total_cash": 125000,
            "change_wow": 0.08,
            "runway_weeks": 12,
            "ar_total": 95000,
            "ar_current": 65000,
            "ar_overdue": 30000,
            "ap_total": 42000,
        },
        "revenue": {
            "mtd": 87500,
            "target": 100000,
            "progress": 0.875
        },
        "ar_aging": {"Current": 65000, "31-60": 20000, "61-90": 8000, "90+": 2000},
        "forecast": [
            {"week_number": i, "week_start_date": (datetime.now() + timedelta(weeks=i)).strftime("%Y-%m-%d"),
             "pessimistic_cash": 125000 * (0.95 ** i),
             "ending_cash": 125000 * (1.02 ** i),
             "optimistic_cash": 125000 * (1.08 ** i)}
            for i in range(13)
        ],
        "jobs": [
            {"job_number": "JOB-2024-001", "name": "Smith Residence", "contract_amount": 18000, "actual_cost": 12000, "actual_margin_pct": 33.3, "status": "completed"},
            {"job_number": "JOB-2024-002", "name": "Johnson Commercial", "contract_amount": 45000, "actual_cost": 28000, "actual_margin_pct": 37.8, "status": "in_progress"},
            {"job_number": "JOB-2024-003", "name": "Williams Repair", "contract_amount": 8500, "actual_cost": 7000, "actual_margin_pct": 17.6, "status": "completed"},
            {"job_number": "JOB-2024-004", "name": "Davis New Build", "contract_amount": 32000, "actual_cost": 18000, "actual_margin_pct": 43.8, "status": "in_progress"},
            {"job_number": "JOB-2024-005", "name": "Miller Insurance", "contract_amount": 22000, "actual_cost": 14500, "actual_margin_pct": 34.1, "status": "completed"},
        ]
    }

# ============================================================
# MAIN DASHBOARD
# ============================================================

def main():
    # Get tenant_id - in production, this would come from auth
    # For now, use a default or check for tenant in Supabase
    tenant_id = os.getenv("TENANT_ID", "demo")
    
    # Check if QBO is connected
    use_qbo = True
    try:
        qbo_client = get_qbo_client(tenant_id)
        if qbo_client is None:
            use_qbo = False
            st.warning("⚠️ QBO not connected. Using mock data. Please connect QBO in settings.")
    except Exception as e:
        use_qbo = False
        st.warning(f"⚠️ QBO connection error: {str(e)}. Using mock data.")
    
    if use_qbo:
        # Fetch from QBO
        cash = get_qbo_cash_position(tenant_id)
        revenue = get_qbo_revenue_mtd(tenant_id)
        ar_aging = get_qbo_ar_aging(tenant_id)
        forecast = get_qbo_forecast(tenant_id)
        
        # For now, use mock jobs data (QBO doesn't have job costing by default)
        # Wrap in try-except to handle Supabase errors gracefully
        try:
            jobs_data = get_jobs_profitability(tenant_id)
            jobs = jobs_data if jobs_data else get_mock_data()["jobs"]
        except Exception as e:
            # If Supabase query fails (e.g., table doesn't exist or no permissions), use mock data
            jobs = get_mock_data()["jobs"]
            if "jobs" not in str(e).lower():  # Only show error if it's not about missing jobs table
                st.warning(f"Could not fetch jobs from database: {str(e)[:100]}")
        
        # Fallback to mock if any data is missing
        if not cash or not revenue or not ar_aging:
            st.warning("⚠️ Some QBO data is missing. Using mock data for missing values.")
            mock_data = get_mock_data()
            cash = cash or mock_data["cash_position"]
            revenue = revenue or mock_data["revenue"]
            ar_aging = ar_aging or mock_data["ar_aging"]
            forecast = forecast or mock_data["forecast"]
    else:
        # Use mock data
        data = get_mock_data()
        cash = data["cash_position"]
        revenue = data["revenue"]
        ar_aging = data["ar_aging"]
        forecast = data["forecast"]
        jobs = data["jobs"]
    
    # Header with CrewCFO branding
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
        <span style="font-size: 2rem;">:house:</span>
        <h1 style="margin: 0; font-size: 2rem; font-weight: 700; color: white;">CrewCFO</h1>
    </div>
    """, unsafe_allow_html=True)
    st.caption(f"Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    
    # ========================================
    # Health Banner
    # ========================================
    runway = cash.get("runway_weeks", 0)
    ar_overdue_pct = (ar_aging.get("61-90", 0) + ar_aging.get("90+", 0)) / max(sum(ar_aging.values()), 1) * 100

    if runway >= 8 and ar_overdue_pct < 15:
        health_status = "Healthy"
        health_emoji = ":green_circle:"
        health_bg = "rgba(16, 185, 129, 0.15)"
        health_border = "rgba(16, 185, 129, 0.4)"
        health_text_color = "#10b981"
    elif runway >= 4:
        health_status = "Warning"
        health_emoji = ":orange_circle:"
        health_bg = "rgba(245, 158, 11, 0.15)"
        health_border = "rgba(245, 158, 11, 0.4)"
        health_text_color = "#f59e0b"
    else:
        health_status = "Alert"
        health_emoji = ":red_circle:"
        health_bg = "rgba(239, 68, 68, 0.15)"
        health_border = "rgba(239, 68, 68, 0.4)"
        health_text_color = "#ef4444"

    st.markdown(f"""
    <div style="background: {health_bg}; border: 1px solid {health_border}; padding: 20px; border-radius: 12px; margin-bottom: 24px;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.5rem; color: {health_text_color};">{health_emoji}</span>
            <span style="font-size: 1.5rem; font-weight: 700; color: {health_text_color};">{health_status}</span>
        </div>
        <p style="color: #94a3b8; margin: 8px 0 0 0; font-size: 0.95rem;">
            Cash runway: {runway} weeks &nbsp;|&nbsp; AR overdue: {ar_overdue_pct:.0f}% &nbsp;|&nbsp; Revenue MTD: {revenue['progress']*100:.0f}% of target
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # ========================================
    # Row 1: Key Metrics (4 cards)
    # ========================================
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            ":dollar: Cash Balance",
            f"${cash.get('total_cash', 0):,.0f}",
            f"{cash.get('change_wow', 0):+.0%} WoW"
        )

    with col2:
        progress_pct = revenue['progress'] * 100
        st.metric(
            ":chart_with_upwards_trend: Revenue MTD",
            f"${revenue['mtd']:,.0f}",
            f"{progress_pct:.0f}% of ${revenue['target']/1000:.0f}K target"
        )

    with col3:
        total_ar = sum(ar_aging.values())
        overdue = ar_aging.get("61-90", 0) + ar_aging.get("90+", 0)
        st.metric(
            ":clipboard: AR Outstanding",
            f"${total_ar:,.0f}",
            f"${overdue:,.0f} overdue",
            delta_color="inverse" if overdue > 0 else "normal"
        )

    with col4:
        # Backlog - mock for now
        backlog = 350000
        backlog_jobs = 8
        st.metric(
            ":wrench: Backlog",
            f"${backlog:,.0f}",
            f"{backlog_jobs} jobs scheduled"
        )
    
    st.divider()
    
    # ========================================
    # Row 2: Charts
    # ========================================
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(":chart_with_upwards_trend: 13-Week Cash Forecast")

        if forecast:
            df = pd.DataFrame(forecast)

            fig = go.Figure()

            # Baseline line (emerald accent)
            fig.add_trace(go.Scatter(
                x=df['week_start_date'],
                y=df['ending_cash'],
                name='Baseline',
                line=dict(color='#10b981', width=3),
                mode='lines'
            ))

            # Optimistic line (lighter emerald)
            fig.add_trace(go.Scatter(
                x=df['week_start_date'],
                y=df['optimistic_cash'],
                name='Optimistic',
                line=dict(color='#34d399', width=2, dash='dot'),
                mode='lines'
            ))

            # Pessimistic line (amber)
            fig.add_trace(go.Scatter(
                x=df['week_start_date'],
                y=df['pessimistic_cash'],
                name='Pessimistic',
                line=dict(color='#f59e0b', width=2, dash='dot'),
                mode='lines'
            ))

            # Minimum balance line
            fig.add_hline(
                y=25000,
                line_dash="dash",
                line_color="#ef4444",
                annotation_text="Min Balance ($25K)",
                annotation_font_color="#94a3b8"
            )

            # Dark theme layout
            fig.update_layout(
                height=350,
                margin=dict(l=0, r=0, t=10, b=0),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    font=dict(color="#94a3b8")
                ),
                yaxis_tickformat='$,.0f',
                xaxis_title="",
                yaxis_title="",
                paper_bgcolor='#0f172a',
                plot_bgcolor='#0f172a',
                xaxis=dict(
                    gridcolor='#1e293b',
                    tickfont=dict(color='#94a3b8'),
                    linecolor='#1e293b'
                ),
                yaxis=dict(
                    gridcolor='#1e293b',
                    tickfont=dict(color='#94a3b8'),
                    linecolor='#1e293b'
                )
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No forecast data available")
    
    with col2:
        st.subheader(":clipboard: AR Aging")

        ar_df = pd.DataFrame({
            'Bucket': list(ar_aging.keys()),
            'Amount': list(ar_aging.values())
        })

        colors = ['#10b981', '#f59e0b', '#f97316', '#ef4444']

        fig = px.bar(
            ar_df,
            x='Bucket',
            y='Amount',
            color='Bucket',
            color_discrete_sequence=colors
        )

        fig.update_layout(
            height=350,
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
            yaxis_tickformat='$,.0f',
            xaxis_title="",
            yaxis_title="",
            paper_bgcolor='#0f172a',
            plot_bgcolor='#0f172a',
            xaxis=dict(
                gridcolor='#1e293b',
                tickfont=dict(color='#94a3b8'),
                linecolor='#1e293b'
            ),
            yaxis=dict(
                gridcolor='#1e293b',
                tickfont=dict(color='#94a3b8'),
                linecolor='#1e293b'
            )
        )

        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # ========================================
    # Row 3: Jobs & Actions
    # ========================================
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader(":hammer: Job Profitability")

        if jobs:
            jobs_df = pd.DataFrame(jobs)

            # Color by margin
            def margin_color(margin):
                if margin >= 35:
                    return '#10b981'
                elif margin >= 25:
                    return '#f59e0b'
                else:
                    return '#ef4444'

            jobs_df['color'] = jobs_df['actual_margin_pct'].apply(margin_color)

            fig = px.treemap(
                jobs_df,
                path=['job_number'],
                values='contract_amount',
                color='actual_margin_pct',
                color_continuous_scale=['#ef4444', '#f59e0b', '#10b981'],
                range_color=[15, 45],
                hover_data=['name', 'actual_cost', 'status']
            )

            fig.update_layout(
                height=300,
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor='#0f172a'
            )

            fig.update_traces(
                textinfo="label+value",
                texttemplate="%{label}<br>$%{value:,.0f}"
            )

            st.plotly_chart(fig, use_container_width=True)

            # Low margin warning
            low_margin_jobs = [j for j in jobs if j.get('actual_margin_pct', 0) < 25]
            if low_margin_jobs:
                st.warning(f":warning: {len(low_margin_jobs)} job(s) below 25% margin")
        else:
            st.info("No job data available")

    with col2:
        st.subheader(":zap: Action Items")
        
        actions = get_action_items(tenant_id)
        
        for action in actions:
            with st.container():
                cols = st.columns([1, 10, 2])
                with cols[0]:
                    st.write(action["priority"])
                with cols[1]:
                    st.write(action["item"])
                with cols[2]:
                    st.caption(action["impact"])
        
        st.divider()

        # Quick stats
        st.subheader(":bar_chart: Quick Stats")
        st.metric("Jobs Completed MTD", "12")
        st.metric("Avg Job Size", "$18,500")
        st.metric("Win Rate", "34%")

# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()
