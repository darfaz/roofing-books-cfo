"""
Owner Dashboard - "Am I okay?" view
Streamlit application for roofing contractor owners
"""
import os
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment
load_dotenv()

# Page config
st.set_page_config(
    page_title="Roofing Books CFO",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stMetric {
        background-color: #1E1E1E;
        padding: 15px;
        border-radius: 10px;
    }
    .health-banner {
        background: linear-gradient(90deg, #1a1a2e 0%, #16213e 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        color: white;
    }
    .action-item {
        background: #1a1a2e;
        padding: 10px 15px;
        border-radius: 5px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA FUNCTIONS
# ============================================================

@st.cache_resource
def get_supabase():
    """Get Supabase client"""
    return create_client(
        os.getenv("SUPABASE_URL", ""),
        os.getenv("SUPABASE_ANON_KEY", "")
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
        {"priority": "🔴", "item": "Follow up on Johnson invoice ($15,000) - 45 days overdue", "impact": "High"},
        {"priority": "🟡", "item": "Review Smith job margins (currently 18%)", "impact": "Medium"},
        {"priority": "🟢", "item": "Send estimate follow-up to Williams prospect", "impact": "Low"},
    ]

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
    # For demo, use mock data
    # In production, replace with real tenant_id from auth
    USE_MOCK = True
    tenant_id = "demo"
    
    if USE_MOCK:
        data = get_mock_data()
        cash = data["cash_position"]
        revenue = data["revenue"]
        ar_aging = data["ar_aging"]
        forecast = data["forecast"]
        jobs = data["jobs"]
    else:
        cash = get_cash_position(tenant_id) or {}
        revenue = get_revenue_mtd(tenant_id)
        ar_aging = get_ar_aging(tenant_id)
        forecast = get_forecast(tenant_id)
        jobs = get_jobs_profitability(tenant_id)
    
    # Header
    st.title("🏠 Owner Dashboard")
    st.caption(f"Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    
    # ========================================
    # Health Banner
    # ========================================
    runway = cash.get("runway_weeks", 0)
    ar_overdue_pct = (ar_aging.get("61-90", 0) + ar_aging.get("90+", 0)) / max(sum(ar_aging.values()), 1) * 100
    
    if runway >= 8 and ar_overdue_pct < 15:
        health_color = "🟢"
        health_status = "Healthy"
        health_bg = "linear-gradient(90deg, #1a472a 0%, #2d5a3d 100%)"
    elif runway >= 4:
        health_color = "🟡"
        health_status = "Watch"
        health_bg = "linear-gradient(90deg, #5a4a1a 0%, #6b5a2d 100%)"
    else:
        health_color = "🔴"
        health_status = "Critical"
        health_bg = "linear-gradient(90deg, #4a1a1a 0%, #5a2d2d 100%)"
    
    st.markdown(f"""
    <div style="background: {health_bg}; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h2 style="color: white; margin: 0;">{health_color} Overall Status: {health_status}</h2>
        <p style="color: #ccc; margin: 5px 0 0 0;">
            Cash runway: {runway} weeks | AR overdue: {ar_overdue_pct:.0f}% | Revenue MTD: {revenue['progress']*100:.0f}% of target
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # ========================================
    # Row 1: Key Metrics
    # ========================================
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💵 Cash Balance",
            f"${cash.get('total_cash', 0):,.0f}",
            f"{cash.get('change_wow', 0):+.0%} WoW"
        )
    
    with col2:
        progress_pct = revenue['progress'] * 100
        delta_color = "normal" if progress_pct >= 80 else "inverse"
        st.metric(
            "📈 Revenue MTD",
            f"${revenue['mtd']:,.0f}",
            f"{progress_pct:.0f}% of ${revenue['target']/1000:.0f}K target"
        )
    
    with col3:
        total_ar = sum(ar_aging.values())
        overdue = ar_aging.get("61-90", 0) + ar_aging.get("90+", 0)
        st.metric(
            "📋 AR Outstanding",
            f"${total_ar:,.0f}",
            f"${overdue:,.0f} overdue",
            delta_color="inverse" if overdue > 0 else "normal"
        )
    
    with col4:
        # Backlog - mock for now
        backlog = 350000
        backlog_jobs = 8
        st.metric(
            "🔧 Backlog",
            f"${backlog:,.0f}",
            f"{backlog_jobs} jobs scheduled"
        )
    
    st.divider()
    
    # ========================================
    # Row 2: Charts
    # ========================================
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 13-Week Cash Forecast")
        
        if forecast:
            df = pd.DataFrame(forecast)
            
            fig = go.Figure()
            
            # Confidence band
            fig.add_trace(go.Scatter(
                x=df['week_start_date'],
                y=df['optimistic_cash'],
                name='Optimistic',
                line=dict(color='rgba(46, 204, 113, 0.5)', dash='dot'),
                showlegend=True
            ))
            
            fig.add_trace(go.Scatter(
                x=df['week_start_date'],
                y=df['ending_cash'],
                name='Baseline',
                line=dict(color='#3498db', width=3),
                fill='tonexty',
                fillcolor='rgba(52, 152, 219, 0.1)'
            ))
            
            fig.add_trace(go.Scatter(
                x=df['week_start_date'],
                y=df['pessimistic_cash'],
                name='Pessimistic',
                line=dict(color='rgba(231, 76, 60, 0.5)', dash='dot'),
                fill='tonexty',
                fillcolor='rgba(52, 152, 219, 0.1)'
            ))
            
            # Minimum balance line
            fig.add_hline(y=25000, line_dash="dash", line_color="orange",
                         annotation_text="Min Balance ($25K)")
            
            fig.update_layout(
                height=350,
                margin=dict(l=0, r=0, t=10, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                yaxis_tickformat='$,.0f',
                xaxis_title="",
                yaxis_title=""
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No forecast data available")
    
    with col2:
        st.subheader("📋 AR Aging")
        
        ar_df = pd.DataFrame({
            'Bucket': list(ar_aging.keys()),
            'Amount': list(ar_aging.values())
        })
        
        colors = ['#2ecc71', '#f1c40f', '#e67e22', '#e74c3c']
        
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
            yaxis_title=""
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # ========================================
    # Row 3: Jobs & Actions
    # ========================================
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("🔨 Job Profitability")
        
        if jobs:
            jobs_df = pd.DataFrame(jobs)
            
            # Color by margin
            def margin_color(margin):
                if margin >= 35:
                    return '#2ecc71'
                elif margin >= 25:
                    return '#f1c40f'
                else:
                    return '#e74c3c'
            
            jobs_df['color'] = jobs_df['actual_margin_pct'].apply(margin_color)
            
            fig = px.treemap(
                jobs_df,
                path=['job_number'],
                values='contract_amount',
                color='actual_margin_pct',
                color_continuous_scale=['#e74c3c', '#f1c40f', '#2ecc71'],
                range_color=[15, 45],
                hover_data=['name', 'actual_cost', 'status']
            )
            
            fig.update_layout(
                height=300,
                margin=dict(l=0, r=0, t=10, b=0)
            )
            
            fig.update_traces(
                textinfo="label+value",
                texttemplate="%{label}<br>$%{value:,.0f}"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Low margin warning
            low_margin_jobs = [j for j in jobs if j.get('actual_margin_pct', 0) < 25]
            if low_margin_jobs:
                st.warning(f"⚠️ {len(low_margin_jobs)} job(s) below 25% margin")
        else:
            st.info("No job data available")
    
    with col2:
        st.subheader("⚡ Action Items")
        
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
        st.subheader("📈 Quick Stats")
        st.metric("Jobs Completed MTD", "12")
        st.metric("Avg Job Size", "$18,500")
        st.metric("Win Rate", "34%")

# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()
