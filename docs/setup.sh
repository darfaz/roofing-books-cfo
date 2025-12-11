#!/bin/bash
# Roofing CFO MVP - Quick Start Setup Script
# Run: chmod +x setup.sh && ./setup.sh

set -e

echo "🏗️ Roofing CFO MVP Setup"
echo "========================"

# Check Python version
python3 --version || { echo "❌ Python 3.9+ required"; exit 1; }

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Install core dependencies
echo "📥 Installing Python packages..."
pip install --upgrade pip
pip install \
    python-quickbooks \
    python-accounting \
    langchain \
    langchain-anthropic \
    langchain-openai \
    streamlit \
    plotly \
    supabase \
    pandas \
    numpy \
    python-dotenv \
    fastapi \
    uvicorn \
    httpx \
    pydantic

# Clone InvoiceNet for OCR
echo "📄 Setting up InvoiceNet OCR..."
if [ ! -d "lib/invoicenet" ]; then
    git clone https://github.com/naiveHobo/InvoiceNet.git lib/invoicenet
    pip install -r lib/invoicenet/requirements.txt
fi

# Create project structure
echo "📁 Creating project structure..."
mkdir -p src/{services,models,utils}
mkdir -p src/services/{qbo,classification,ocr,forecasting}
mkdir -p tests

# Create .env template
echo "🔐 Creating .env template..."
cat > .env.example << 'EOF'
# QuickBooks Online
QBO_CLIENT_ID=your_client_id
QBO_CLIENT_SECRET=your_client_secret
QBO_REDIRECT_URI=http://localhost:8000/callback
QBO_ENVIRONMENT=sandbox  # or production

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key

# Anthropic (for classification)
ANTHROPIC_API_KEY=sk-ant-...

# Avalara (for tax)
AVALARA_USERNAME=your_username
AVALARA_PASSWORD=your_password
AVALARA_ENVIRONMENT=sandbox  # or production

# Slack (for notifications)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# App Settings
APP_ENV=development
LOG_LEVEL=INFO
EOF

# Create basic app structure
echo "🐍 Creating application files..."

# Main FastAPI app
cat > src/main.py << 'EOF'
"""Roofing CFO API - Main entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="Roofing CFO API",
    description="AI-powered bookkeeping for roofing contractors",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "0.1.0"}

# Import routers
# from src.services.qbo import router as qbo_router
# from src.services.classification import router as classification_router
# app.include_router(qbo_router, prefix="/api/qbo", tags=["QuickBooks"])
# app.include_router(classification_router, prefix="/api/classify", tags=["Classification"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
EOF

# QBO Service skeleton
cat > src/services/qbo/client.py << 'EOF'
"""QuickBooks Online integration using python-quickbooks"""
import os
from quickbooks import QuickBooks
from quickbooks.objects.account import Account
from quickbooks.objects.bill import Bill
from quickbooks.objects.invoice import Invoice
from quickbooks.objects.purchase import Purchase
from dotenv import load_dotenv

load_dotenv()

class QBOClient:
    def __init__(self):
        self.client = None
    
    def connect(self, access_token: str, refresh_token: str, realm_id: str):
        """Initialize QBO connection with OAuth tokens"""
        self.client = QuickBooks(
            sandbox=(os.getenv("QBO_ENVIRONMENT") == "sandbox"),
            consumer_key=os.getenv("QBO_CLIENT_ID"),
            consumer_secret=os.getenv("QBO_CLIENT_SECRET"),
            access_token=access_token,
            refresh_token=refresh_token,
            company_id=realm_id
        )
        return self
    
    def get_transactions(self, start_date: str, end_date: str = None):
        """Fetch transactions for date range"""
        if not self.client:
            raise ValueError("QBO client not connected")
        
        purchases = Purchase.filter(
            start_date=start_date,
            end_date=end_date,
            qb=self.client
        )
        return purchases
    
    def get_chart_of_accounts(self):
        """Fetch chart of accounts"""
        accounts = Account.all(qb=self.client)
        return [
            {
                "id": a.Id,
                "name": a.Name,
                "type": a.AccountType,
                "code": a.AcctNum,
                "active": a.Active
            }
            for a in accounts
        ]
    
    def create_bill(self, vendor_id: str, line_items: list, memo: str = None):
        """Create a bill in QBO"""
        from quickbooks.objects.vendor import Vendor
        from quickbooks.objects.detailline import AccountBasedExpenseLine
        
        vendor = Vendor.get(vendor_id, qb=self.client)
        
        bill = Bill()
        bill.VendorRef = vendor.to_ref()
        bill.Line = []
        
        for item in line_items:
            line = AccountBasedExpenseLine()
            line.Amount = item["amount"]
            line.Description = item.get("description", "")
            # Set account reference
            bill.Line.append(line)
        
        if memo:
            bill.PrivateNote = memo
        
        bill.save(qb=self.client)
        return bill.Id

# Singleton instance
qbo = QBOClient()
EOF

# Classification Service skeleton
cat > src/services/classification/agent.py << 'EOF'
"""Transaction classification agent using LangChain + Claude"""
import os
from typing import Optional
from pydantic import BaseModel, Field
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from dotenv import load_dotenv

load_dotenv()

class TransactionClassification(BaseModel):
    """Classification result for a transaction"""
    account_code: str = Field(description="Account code to classify to")
    account_name: str = Field(description="Account name")
    job_id: Optional[str] = Field(description="Job ID if applicable", default=None)
    confidence: float = Field(description="Confidence score 0-1")
    reasoning: str = Field(description="Brief explanation of classification")

class ClassificationAgent:
    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            temperature=0,
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.parser = PydanticOutputParser(pydantic_object=TransactionClassification)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert bookkeeper for roofing contractors.
Your job is to classify transactions to the correct account in the chart of accounts.

CHART OF ACCOUNTS:
{chart_of_accounts}

ACTIVE JOBS:
{active_jobs}

CLASSIFICATION RULES:
1. Materials from suppliers (Home Depot, ABC Supply, etc.) → 5100 Materials COGS
2. Subcontractor payments → 5200 Subcontractor COGS
3. Payroll/wages → 5300 Labor COGS
4. Vehicle expenses → 6400 Vehicle Expense
5. Office supplies → 6200 Office Expense
6. If job number mentioned in memo, assign job_id

{format_instructions}"""),
            ("human", """Classify this transaction:
Vendor: {vendor}
Amount: ${amount}
Date: {date}
Memo: {memo}
""")
        ])
    
    def classify(
        self,
        vendor: str,
        amount: float,
        date: str,
        memo: str,
        chart_of_accounts: str,
        active_jobs: str
    ) -> TransactionClassification:
        """Classify a single transaction"""
        
        chain = self.prompt | self.llm | self.parser
        
        result = chain.invoke({
            "vendor": vendor,
            "amount": amount,
            "date": date,
            "memo": memo,
            "chart_of_accounts": chart_of_accounts,
            "active_jobs": active_jobs,
            "format_instructions": self.parser.get_format_instructions()
        })
        
        return result

# Usage example
if __name__ == "__main__":
    agent = ClassificationAgent()
    
    # Sample chart of accounts
    coa = """
    5100 - Materials COGS (Direct Cost)
    5200 - Subcontractor COGS (Direct Cost)
    5300 - Labor COGS (Direct Cost)
    6100 - Advertising (Operating Expense)
    6200 - Office Expense (Operating Expense)
    6300 - Insurance (Operating Expense)
    6400 - Vehicle Expense (Operating Expense)
    """
    
    # Sample active jobs
    jobs = """
    JOB-2024-001: Smith Residence - Roof Replacement
    JOB-2024-002: Johnson Commercial - New Construction
    JOB-2024-003: Williams Home - Storm Repair
    """
    
    result = agent.classify(
        vendor="Home Depot",
        amount=1234.56,
        date="2024-01-15",
        memo="Shingles and underlayment for Smith job",
        chart_of_accounts=coa,
        active_jobs=jobs
    )
    
    print(f"Account: {result.account_code} - {result.account_name}")
    print(f"Job: {result.job_id}")
    print(f"Confidence: {result.confidence}")
    print(f"Reasoning: {result.reasoning}")
EOF

# Streamlit Dashboard skeleton
cat > src/dashboard/owner.py << 'EOF'
"""Owner Dashboard - "Am I okay?" view"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Roofing CFO - Owner Dashboard",
    page_icon="🏠",
    layout="wide"
)

# Mock data - replace with Supabase queries
def get_mock_data():
    return {
        "cash_balance": 125000,
        "cash_change_wow": 0.08,
        "runway_weeks": 12,
        "next_payroll": 45000,
        "mtd_revenue": 87500,
        "mtd_target": 100000,
        "ytd_revenue": 875000,
        "ar_total": 95000,
        "ar_current": 65000,
        "ar_31_60": 20000,
        "ar_61_90": 8000,
        "ar_90_plus": 2000,
        "ap_total": 42000,
        "backlog_value": 350000,
        "backlog_jobs": 8,
        "estimates_count": 12,
        "estimates_value": 180000,
    }

data = get_mock_data()

# Header
st.title("🏠 Owner Dashboard")
st.caption(f"Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")

# Health Banner
runway = data["runway_weeks"]
if runway >= 8:
    health_color = "🟢"
    health_status = "Healthy"
elif runway >= 4:
    health_color = "🟡"
    health_status = "Watch"
else:
    health_color = "🔴"
    health_status = "Critical"

st.markdown(f"""
<div style="background: linear-gradient(90deg, #1a1a2e 0%, #16213e 100%); 
            padding: 20px; border-radius: 10px; margin-bottom: 20px;">
    <h2 style="color: white; margin: 0;">{health_color} Overall Status: {health_status}</h2>
    <p style="color: #888; margin: 5px 0 0 0;">Cash runway: {runway} weeks | AR overdue: {((data['ar_61_90'] + data['ar_90_plus']) / data['ar_total'] * 100):.0f}%</p>
</div>
""", unsafe_allow_html=True)

# Row 1: Key Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "💵 Cash Balance",
        f"${data['cash_balance']:,.0f}",
        f"{data['cash_change_wow']:+.0%} WoW"
    )

with col2:
    progress = data['mtd_revenue'] / data['mtd_target']
    st.metric(
        "📈 Revenue MTD",
        f"${data['mtd_revenue']:,.0f}",
        f"{progress:.0%} of target"
    )

with col3:
    st.metric(
        "📋 AR Outstanding",
        f"${data['ar_total']:,.0f}",
        f"${data['ar_61_90'] + data['ar_90_plus']:,.0f} overdue"
    )

with col4:
    st.metric(
        "🔧 Backlog",
        f"${data['backlog_value']:,.0f}",
        f"{data['backlog_jobs']} jobs"
    )

st.divider()

# Row 2: Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("13-Week Cash Forecast")
    
    # Generate forecast data
    weeks = pd.date_range(start=datetime.now(), periods=13, freq='W')
    forecast_df = pd.DataFrame({
        'Week': weeks,
        'Pessimistic': [data['cash_balance'] * (0.95 ** i) for i in range(13)],
        'Baseline': [data['cash_balance'] * (1.02 ** i) for i in range(13)],
        'Optimistic': [data['cash_balance'] * (1.08 ** i) for i in range(13)]
    })
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=forecast_df['Week'], y=forecast_df['Optimistic'], 
                             name='Optimistic', line=dict(color='green', dash='dot')))
    fig.add_trace(go.Scatter(x=forecast_df['Week'], y=forecast_df['Baseline'], 
                             name='Baseline', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=forecast_df['Week'], y=forecast_df['Pessimistic'], 
                             name='Pessimistic', line=dict(color='red', dash='dot')))
    fig.add_hline(y=25000, line_dash="dash", line_color="orange", 
                  annotation_text="Minimum Balance")
    fig.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("AR Aging")
    
    ar_data = pd.DataFrame({
        'Bucket': ['Current', '31-60 Days', '61-90 Days', '90+ Days'],
        'Amount': [data['ar_current'], data['ar_31_60'], data['ar_61_90'], data['ar_90_plus']]
    })
    
    colors = ['#2ecc71', '#f1c40f', '#e67e22', '#e74c3c']
    fig = px.bar(ar_data, x='Bucket', y='Amount', color='Bucket',
                 color_discrete_sequence=colors)
    fig.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Row 3: Action Items
st.subheader("⚡ Action Items")

actions = [
    {"priority": "🔴", "item": "Follow up on Johnson invoice ($15,000) - 45 days overdue", "impact": "High"},
    {"priority": "🟡", "item": "Review Smith job margins (currently 18%)", "impact": "Medium"},
    {"priority": "🟢", "item": "Send estimate follow-up to Williams prospect", "impact": "Low"},
]

for action in actions:
    st.markdown(f"""
    <div style="background: #1a1a2e; padding: 10px 15px; border-radius: 5px; margin-bottom: 10px; display: flex; align-items: center;">
        <span style="font-size: 20px; margin-right: 10px;">{action['priority']}</span>
        <span style="flex: 1;">{action['item']}</span>
        <span style="color: #888; font-size: 12px;">{action['impact']} impact</span>
    </div>
    """, unsafe_allow_html=True)
EOF

mkdir -p src/dashboard
mv src/dashboard/owner.py src/dashboard/owner.py 2>/dev/null || true

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and fill in credentials"
echo "2. Run API: python src/main.py"
echo "3. Run Dashboard: streamlit run src/dashboard/owner.py"
echo "4. Start ActivePieces: docker run -d -p 8080:80 activepieces/activepieces"
echo ""
echo "📚 Read implementation/oss_implementation_guide.md for detailed instructions"
EOF

chmod +x /home/claude/spec-kit-books-cfo-roofers/setup.sh
