"""
Roofing Books CFO - API Server
FastAPI application for bookkeeping automation
"""
import os
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import httpx
from dotenv import load_dotenv
from supabase import create_client, Client
import uvicorn

# Load environment variables
load_dotenv()

# Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL", ""),
    os.getenv("SUPABASE_SERVICE_KEY", "")
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events"""
    print("🚀 Starting Roofing Books CFO API...")
    yield
    print("👋 Shutting down...")

app = FastAPI(
    title="Roofing Books CFO API",
    description="AI-powered bookkeeping for roofing contractors",
    version="0.1.0",
    lifespan=lifespan
)

# CORS - allow all for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "timestamp": datetime.utcnow().isoformat()
    }

# ============================================================
# QUICKBOOKS OAUTH
# ============================================================

QBO_AUTH_URL = "https://appcenter.intuit.com/connect/oauth2"
QBO_TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"

@app.get("/auth/qbo/connect")
async def qbo_connect(tenant_id: str):
    """
    Start QuickBooks OAuth flow
    
    Usage: GET /auth/qbo/connect?tenant_id=YOUR_TENANT_UUID
    """
    client_id = os.getenv("QBO_CLIENT_ID")
    redirect_uri = os.getenv("QBO_REDIRECT_URI")
    
    if not client_id or not redirect_uri:
        raise HTTPException(500, "QBO credentials not configured")
    
    # Store tenant_id in state for callback
    state = tenant_id
    
    # Scopes needed for bookkeeping
    scopes = "com.intuit.quickbooks.accounting"
    
    auth_url = (
        f"{QBO_AUTH_URL}?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope={scopes}&"
        f"state={state}"
    )
    
    return RedirectResponse(auth_url)

@app.get("/auth/qbo/callback")
async def qbo_callback(code: str, state: str, realmId: str):
    """
    QuickBooks OAuth callback
    
    Intuit redirects here after user authorizes
    """
    client_id = os.getenv("QBO_CLIENT_ID")
    client_secret = os.getenv("QBO_CLIENT_SECRET")
    redirect_uri = os.getenv("QBO_REDIRECT_URI")
    
    tenant_id = state  # We stored tenant_id in state
    
    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        response = await client.post(
            QBO_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
            },
            auth=(client_id, client_secret),
            headers={"Accept": "application/json"}
        )
    
    if response.status_code != 200:
        raise HTTPException(400, f"Token exchange failed: {response.text}")
    
    tokens = response.json()
    
    # Store tokens in Supabase
    result = supabase.table("tenant_integrations").upsert({
        "tenant_id": tenant_id,
        "provider": "quickbooks",
        "access_token": tokens.get("access_token"),
        "refresh_token": tokens.get("refresh_token"),
        "token_expires_at": datetime.utcnow().isoformat(),  # TODO: Calculate properly
        "realm_id": realmId,
        "is_active": True,
        "metadata": {
            "token_type": tokens.get("token_type"),
            "expires_in": tokens.get("expires_in")
        }
    }).execute()
    
    return {
        "status": "connected",
        "tenant_id": tenant_id,
        "realm_id": realmId,
        "message": "QuickBooks connected successfully!"
    }

# ============================================================
# TRANSACTIONS
# ============================================================

@app.get("/api/transactions")
async def list_transactions(
    tenant_id: str,
    limit: int = 50,
    offset: int = 0,
    status: str = None
):
    """List transactions for a tenant"""
    query = supabase.table("transactions")\
        .select("*, customers(name), vendors(name)")\
        .eq("tenant_id", tenant_id)\
        .order("transaction_date", desc=True)\
        .range(offset, offset + limit - 1)
    
    if status:
        query = query.eq("classification_status", status)
    
    result = query.execute()
    return {"transactions": result.data, "count": len(result.data)}

@app.post("/api/transactions/{transaction_id}/classify")
async def classify_transaction(transaction_id: str, account_id: str, job_id: str = None):
    """Manually classify a transaction"""
    update_data = {
        "classification_status": "manual_classified",
        "classified_by": "user",
        "classified_at": datetime.utcnow().isoformat()
    }
    
    # Update transaction
    result = supabase.table("transactions")\
        .update(update_data)\
        .eq("id", transaction_id)\
        .execute()
    
    # Update transaction line with account
    supabase.table("transaction_lines")\
        .update({"account_id": account_id, "job_id": job_id})\
        .eq("transaction_id", transaction_id)\
        .execute()
    
    return {"status": "classified", "transaction_id": transaction_id}

# ============================================================
# JOBS
# ============================================================

@app.get("/api/jobs")
async def list_jobs(
    tenant_id: str,
    status: str = None,
    limit: int = 50
):
    """List jobs for a tenant"""
    query = supabase.table("jobs")\
        .select("*, customers(name)")\
        .eq("tenant_id", tenant_id)\
        .order("created_at", desc=True)\
        .limit(limit)
    
    if status:
        query = query.eq("status", status)
    
    result = query.execute()
    return {"jobs": result.data, "count": len(result.data)}

@app.get("/api/jobs/{job_id}/costs")
async def get_job_costs(job_id: str):
    """Get cost breakdown for a job"""
    result = supabase.table("job_costs")\
        .select("*, vendors(name)")\
        .eq("job_id", job_id)\
        .order("cost_date", desc=True)\
        .execute()
    
    # Summarize by category
    summary = {}
    for cost in result.data:
        cat = cost["cost_category"]
        if cat not in summary:
            summary[cat] = 0
        summary[cat] += float(cost["total_cost"])
    
    return {
        "job_id": job_id,
        "costs": result.data,
        "summary": summary,
        "total": sum(summary.values())
    }

# ============================================================
# CASH FLOW
# ============================================================

@app.get("/api/cash/position")
async def get_cash_position(tenant_id: str):
    """Get current cash position"""
    result = supabase.table("cash_positions")\
        .select("*")\
        .eq("tenant_id", tenant_id)\
        .order("position_date", desc=True)\
        .limit(1)\
        .execute()
    
    if not result.data:
        return {"error": "No cash position data"}
    
    return result.data[0]

@app.get("/api/cash/forecast")
async def get_cash_forecast(tenant_id: str):
    """Get 13-week cash forecast"""
    result = supabase.table("cash_forecasts")\
        .select("*")\
        .eq("tenant_id", tenant_id)\
        .order("forecast_date", desc=True)\
        .order("week_number", desc=False)\
        .limit(13)\
        .execute()
    
    return {"forecast": result.data}

# ============================================================
# CHART OF ACCOUNTS
# ============================================================

@app.get("/api/accounts")
async def list_accounts(tenant_id: str, active_only: bool = True):
    """List chart of accounts"""
    query = supabase.table("accounts")\
        .select("*")\
        .eq("tenant_id", tenant_id)\
        .order("code")
    
    if active_only:
        query = query.eq("is_active", True)
    
    result = query.execute()
    return {"accounts": result.data}

# ============================================================
# AR AGING
# ============================================================

@app.get("/api/ar/aging")
async def get_ar_aging(tenant_id: str):
    """Get AR aging summary"""
    # Use the view we created
    result = supabase.rpc("get_ar_aging", {"p_tenant_id": tenant_id}).execute()
    
    # If RPC not set up, fall back to direct query
    if not result.data:
        result = supabase.table("transactions")\
            .select("*, customers(name)")\
            .eq("tenant_id", tenant_id)\
            .eq("transaction_type", "invoice")\
            .neq("status", "voided")\
            .execute()
    
    # Calculate aging buckets
    buckets = {"current": 0, "31-60": 0, "61-90": 0, "90+": 0}
    invoices = []
    
    for txn in result.data:
        days = (datetime.now().date() - datetime.fromisoformat(txn["transaction_date"]).date()).days
        amount = float(txn["total_amount"])
        
        if days <= 30:
            buckets["current"] += amount
        elif days <= 60:
            buckets["31-60"] += amount
        elif days <= 90:
            buckets["61-90"] += amount
        else:
            buckets["90+"] += amount
        
        invoices.append({
            "id": txn["id"],
            "customer": txn.get("customers", {}).get("name", "Unknown"),
            "amount": amount,
            "date": txn["transaction_date"],
            "days_outstanding": days
        })
    
    return {
        "buckets": buckets,
        "total": sum(buckets.values()),
        "invoices": sorted(invoices, key=lambda x: x["days_outstanding"], reverse=True)
    }

# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=os.getenv("APP_ENV") == "development"
    )
