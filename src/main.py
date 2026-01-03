"""
Roofing Books CFO - API Server
FastAPI application for bookkeeping automation
"""
import os
import logging
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)
from fastapi import FastAPI, HTTPException, Request, Depends, Body, UploadFile, File, Form, BackgroundTasks, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from src.services.qbo.sync import QBOSyncService
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

# Auth helper (Supabase Auth -> tenant context)
from src.utils.auth import get_current_tenant_id

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events"""
    print("🚀 Starting Roofing Books CFO API...")
    # Ensure Supabase Storage bucket(s) exist (service role only)
    try:
        supabase.storage.create_bucket("deal-room", options={"public": False})
    except Exception:
        # bucket may already exist or the storage API may be unavailable in some envs
        pass
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
async def qbo_connect(tenant_id: str, return_url: str = "/dashboard"):
    """
    Start QuickBooks OAuth flow

    Usage: GET /auth/qbo/connect?tenant_id=YOUR_TENANT_UUID&return_url=/dashboard
    """
    import base64
    import json

    client_id = os.getenv("QBO_CLIENT_ID")
    redirect_uri = os.getenv("QBO_REDIRECT_URI")

    if not client_id or not redirect_uri:
        raise HTTPException(500, "QBO credentials not configured")

    # Store tenant_id and return_url in state (base64 encoded JSON)
    state_data = {"tenant_id": tenant_id, "return_url": return_url}
    state = base64.urlsafe_b64encode(json.dumps(state_data).encode()).decode()

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

def run_initial_sync(tenant_id: str):
    """Background task to sync QBO data after connection"""
    try:
        print(f"[QBO Sync] Starting initial sync for tenant {tenant_id}")
        sync_service = QBOSyncService(tenant_id)
        result = sync_service.sync_transactions(start_date=None)  # Last 12 months
        print(f"[QBO Sync] Completed for tenant {tenant_id}: {result.get('synced_count')} transactions")
    except Exception as e:
        print(f"[QBO Sync] Error for tenant {tenant_id}: {e}")


@app.get("/auth/qbo/callback")
async def qbo_callback(code: str, state: str, realmId: str, background_tasks: BackgroundTasks):
    """
    QuickBooks OAuth callback

    Intuit redirects here after user authorizes.
    Automatically triggers initial data sync in background.
    """
    import base64
    import json

    client_id = os.getenv("QBO_CLIENT_ID")
    client_secret = os.getenv("QBO_CLIENT_SECRET")
    redirect_uri = os.getenv("QBO_REDIRECT_URI")

    # Decode state to get tenant_id and return_url
    try:
        state_data = json.loads(base64.urlsafe_b64decode(state).decode())
        tenant_id = state_data.get("tenant_id")
        return_url = state_data.get("return_url", "/dashboard")
    except Exception:
        # Fallback for old-style state (just tenant_id)
        tenant_id = state
        return_url = "/dashboard"

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

    # Calculate token expiration
    expires_in = tokens.get("expires_in", 3600)  # Default to 1 hour if not provided
    token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

    # Store tokens in Supabase (upsert on tenant_id + provider)
    supabase.table("tenant_integrations").upsert(
        {
            "tenant_id": tenant_id,
            "provider": "quickbooks",
            "access_token": tokens.get("access_token"),
            "refresh_token": tokens.get("refresh_token"),
            "token_expires_at": token_expires_at.isoformat(),
            "realm_id": realmId,
            "is_active": True,
            "metadata": {
                "token_type": tokens.get("token_type"),
                "expires_in": expires_in
            }
        },
        on_conflict="tenant_id,provider"
    ).execute()

    # Trigger initial sync in background (doesn't block redirect)
    background_tasks.add_task(run_initial_sync, tenant_id)

    # Redirect to the return URL (dashboard)
    # Add sync_started param so frontend can show "syncing..." status
    separator = "&" if "?" in return_url else "?"
    return RedirectResponse(url=f"{return_url}{separator}sync_started=true", status_code=302)


@app.post("/auth/qbo/disconnect")
async def qbo_disconnect(tenant_id: str):
    """
    Disconnect QuickBooks integration for a tenant.

    This revokes the connection and deletes stored tokens,
    allowing the user to connect a different QBO account.
    """
    # First, try to revoke the token with Intuit (best practice)
    try:
        result = supabase.table("tenant_integrations")\
            .select("access_token, refresh_token")\
            .eq("tenant_id", tenant_id)\
            .eq("provider", "quickbooks")\
            .single()\
            .execute()

        if result.data and result.data.get("refresh_token"):
            # Revoke token with Intuit
            client_id = os.getenv("QBO_CLIENT_ID")
            client_secret = os.getenv("QBO_CLIENT_SECRET")

            async with httpx.AsyncClient() as client:
                await client.post(
                    "https://developer.api.intuit.com/v2/oauth2/tokens/revoke",
                    data={"token": result.data["refresh_token"]},
                    auth=(client_id, client_secret),
                    headers={"Accept": "application/json"}
                )
    except Exception:
        # Continue even if revocation fails - we still want to clear local tokens
        pass

    # Delete the integration record
    supabase.table("tenant_integrations")\
        .delete()\
        .eq("tenant_id", tenant_id)\
        .eq("provider", "quickbooks")\
        .execute()

    return {"success": True, "message": "QuickBooks disconnected successfully"}


@app.get("/api/qbo/status")
async def get_qbo_status(tenant_id: str):
    """
    Check QuickBooks connection status for a tenant

    Returns:
        connected: bool - whether QBO is connected
        realm_id: str - QBO company ID (if connected)
        expires_at: str - token expiration time (if connected)
    """
    result = supabase.table("tenant_integrations")\
        .select("realm_id, is_active, token_expires_at, created_at, updated_at")\
        .eq("tenant_id", tenant_id)\
        .eq("provider", "quickbooks")\
        .limit(1)\
        .execute()

    if not result.data:
        return {
            "connected": False,
            "message": "No QuickBooks integration found for this tenant"
        }

    integration = result.data[0]
    return {
        "connected": integration.get("is_active", False),
        "realm_id": integration.get("realm_id"),
        "token_expires_at": integration.get("token_expires_at"),
        "created_at": integration.get("created_at"),
        "updated_at": integration.get("updated_at")
    }


@app.get("/api/qbo/balances")
async def get_qbo_balances(tenant_id: str):
    """
    Get actual QuickBooks balances - cash and AR directly from QB API.

    IMPORTANT: This returns ACTUAL QB data, not computed from transactions.
    - Cash: From Bank account CurrentBalance
    - AR: Sum of all invoice Balance fields (unpaid portion)
    - AP: Sum of all bill Balance fields (unpaid portion)

    Returns:
        cash_balance: Actual bank account balance
        ar_balance: Sum of unpaid invoice balances
        ap_balance: Sum of unpaid bill balances
    """
    from src.services.qbo.client import QBOClient

    try:
        client = QBOClient(tenant_id)

        # Get actual cash balance from bank accounts
        cash_balance = client.get_cash_accounts_balance()

        # Get actual AR from invoice balances
        invoices = client.get_invoices()
        ar_balance = sum(inv.get("balance", 0) for inv in invoices)

        # Get actual AP from bill balances
        bills = client.get_bills()
        ap_balance = sum(abs(bill.get("balance", 0)) for bill in bills)

        return {
            "success": True,
            "cash_balance": round(cash_balance, 2),
            "ar_balance": round(ar_balance, 2),
            "ap_balance": round(ap_balance, 2),
            "source": "quickbooks_api",
            "timestamp": datetime.now().isoformat()
        }
    except ValueError as e:
        return {
            "success": False,
            "error": str(e),
            "cash_balance": None,
            "ar_balance": None,
            "ap_balance": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to fetch QB balances: {str(e)}",
            "cash_balance": None,
            "ar_balance": None,
            "ap_balance": None
        }


@app.get("/api/qbo/debug")
async def debug_qbo_data(tenant_id: str, entity_type: str = "Purchase"):
    """
    Debug endpoint to query QBO directly and see raw response

    Args:
        tenant_id: Tenant UUID
        entity_type: QBO entity type to query (Purchase, Invoice, Deposit, Account, Bill)

    Returns:
        Raw QBO query response for debugging
    """
    from src.services.qbo.client import QBOClient

    try:
        client = QBOClient(tenant_id)

        # Query without date filter first to see all data
        query_str = f"SELECT * FROM {entity_type} MAXRESULTS 10"
        results = client.query(query_str)

        # Also get company info
        company_info = {}
        try:
            company_info = client.get_company_info()
        except Exception as e:
            company_info = {"error": str(e)}

        return {
            "success": True,
            "company_info": company_info,
            "entity_type": entity_type,
            "query": query_str,
            "count": len(results),
            "results": results[:10]  # Limit to 10 for debugging
        }
    except ValueError as e:
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
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
async def classify_transaction(transaction_id: str, account_id: str = None, job_id: str = None):
    """
    Classify a transaction
    
    If account_id is provided, manually classify.
    If not provided, use AI classification agent.
    """
    from src.services.qbo.classification_workflow import ClassificationWorkflow

    # Get tenant_id from transaction
    txn_result = supabase.table("transactions")\
        .select("tenant_id")\
        .eq("id", transaction_id)\
        .limit(1)\
        .execute()
    
    if not txn_result.data:
        raise HTTPException(404, "Transaction not found")
    
    tenant_id = txn_result.data[0]["tenant_id"]
    
    if account_id:
        # Manual classification
        update_data = {
            "classification_status": "manual_classified",
            "classified_by": "user",
            "classified_at": datetime.utcnow().isoformat()
        }
        
        supabase.table("transactions")\
            .update(update_data)\
            .eq("id", transaction_id)\
            .execute()
        
        # Update or create transaction line
        existing_line = supabase.table("transaction_lines")\
            .select("id")\
            .eq("transaction_id", transaction_id)\
            .limit(1)\
            .execute()
        
        if existing_line.data:
            supabase.table("transaction_lines")\
                .update({"account_id": account_id, "job_id": job_id})\
                .eq("id", existing_line.data[0]["id"])\
                .execute()
        else:
            supabase.table("transaction_lines")\
                .insert({
                    "transaction_id": transaction_id,
                    "account_id": account_id,
                    "job_id": job_id,
                    "line_number": 1
                })\
                .execute()
        
        return {"status": "classified", "transaction_id": transaction_id, "method": "manual"}
    else:
        # AI classification
        workflow = ClassificationWorkflow(tenant_id)
        result = workflow.classify_transaction_by_id(transaction_id)
        return result

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
# FINANCE COMMAND CENTER API
# ============================================================

@app.get("/api/finance/ap/aging")
async def get_ap_aging(tenant_id: str = Depends(get_current_tenant_id)):
    """
    Get AP aging summary with buckets

    Returns:
        AP aging by bucket (current, 1-30, 31-60, 61-90, 90+)
        with total, overdue amount, and bills list
    """
    from src.services.finance.ap import APService

    try:
        ap_service = APService(tenant_id)
        aging = ap_service.calculate_ap_aging()

        return {
            "success": True,
            "data": aging
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"Failed to get AP aging: {str(e)}"
                }
            }
        )


@app.get("/api/finance/ap/upcoming")
async def get_ap_upcoming_payments(
    tenant_id: str = Depends(get_current_tenant_id),
    days_ahead: int = 30
):
    """
    Get upcoming AP payments for cash planning

    Args:
        days_ahead: Number of days to look ahead (default: 30)

    Returns:
        List of bills due in the next N days
    """
    from src.services.finance.ap import APService

    try:
        ap_service = APService(tenant_id)
        upcoming = ap_service.get_upcoming_payments(days_ahead=days_ahead)

        return {
            "success": True,
            "data": {
                "days_ahead": days_ahead,
                "payments": upcoming,
                "total": sum(p["amount"] for p in upcoming),
                "count": len(upcoming)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"Failed to get upcoming payments: {str(e)}"
                }
            }
        )


@app.get("/api/finance/ap/by-vendor")
async def get_ap_by_vendor(tenant_id: str = Depends(get_current_tenant_id)):
    """
    Get AP summary by vendor

    Returns:
        List of vendors with their AP totals
    """
    from src.services.finance.ap import APService

    try:
        ap_service = APService(tenant_id)
        summary = ap_service.get_vendor_summary()

        return {
            "success": True,
            "data": {
                "vendors": summary,
                "total": sum(v["total"] for v in summary)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"Failed to get vendor summary: {str(e)}"
                }
            }
        )


@app.get("/api/finance/ap/metrics")
async def get_ap_metrics(tenant_id: str = Depends(get_current_tenant_id)):
    """
    Get key AP metrics for dashboard cards
    """
    from src.services.finance.ap import APService

    try:
        ap_service = APService(tenant_id)
        metrics = ap_service.get_ap_metrics()

        return {
            "success": True,
            "data": metrics
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"Failed to get AP metrics: {str(e)}"
                }
            }
        )


@app.get("/api/finance/cash-forecast")
async def get_13_week_cash_forecast(
    tenant_id: str = Depends(get_current_tenant_id),
    scenario: str = "base"
):
    """
    Get 13-week rolling cash flow forecast

    Args:
        scenario: "optimistic", "base", or "pessimistic"

    Returns:
        Complete forecast with weekly projections
    """
    from src.services.finance.cash_forecast import CashFlowForecastService

    try:
        if scenario not in ["base", "optimistic", "pessimistic"]:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Scenario must be 'base', 'optimistic', or 'pessimistic'"
                    }
                }
            )

        forecast_service = CashFlowForecastService(tenant_id)
        forecast = forecast_service.generate_13_week_forecast(scenario=scenario)

        return {
            "success": True,
            "data": forecast
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"Failed to generate cash forecast: {str(e)}"
                }
            }
        )


@app.get("/api/finance/cash-forecast/all-scenarios")
async def get_all_cash_forecast_scenarios(tenant_id: str = Depends(get_current_tenant_id)):
    """
    Get 13-week cash forecast for all three scenarios

    Returns:
        Base, optimistic, and pessimistic forecasts
    """
    from src.services.finance.cash_forecast import CashFlowForecastService

    try:
        forecast_service = CashFlowForecastService(tenant_id)
        all_scenarios = forecast_service.get_all_scenarios()

        return {
            "success": True,
            "data": all_scenarios
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"Failed to generate forecasts: {str(e)}"
                }
            }
        )


@app.get("/api/finance/cash-forecast/alert")
async def get_cash_alert_status(tenant_id: str = Depends(get_current_tenant_id)):
    """
    Get cash position health status for dashboard

    Returns:
        Status (healthy/good/caution/critical) with recommendations
    """
    from src.services.finance.cash_forecast import CashFlowForecastService

    try:
        forecast_service = CashFlowForecastService(tenant_id)
        alert = forecast_service.get_cash_alert_status()

        return {
            "success": True,
            "data": alert
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"Failed to get cash alert: {str(e)}"
                }
            }
        )


@app.get("/api/finance/budget/variance")
async def get_budget_variance(
    tenant_id: str = Depends(get_current_tenant_id),
    year: int = None,
    month: int = None
):
    """
    Get budget vs actual variance for a month

    Args:
        year: Year (defaults to current)
        month: Month 1-12 (defaults to current)

    Returns:
        Variance analysis by category
    """
    from src.services.finance.budget import BudgetService
    from datetime import date

    try:
        if not year:
            year = date.today().year
        if not month:
            month = date.today().month

        if month < 1 or month > 12:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Month must be between 1 and 12"
                    }
                }
            )

        budget_service = BudgetService(tenant_id)
        try:
            variance = budget_service.calculate_variance(year, month)
        except Exception:
            # If budget calculation fails (e.g., missing tables), return default response
            variance = {
                "status": "no_budget",
                "period": f"{year}-{month:02d}",
                "message": "Budget tracking not yet configured"
            }

        return {
            "success": True,
            "data": variance
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"Failed to get variance: {str(e)}"
                }
            }
        )


@app.get("/api/finance/budget/ytd")
async def get_budget_ytd(
    tenant_id: str = Depends(get_current_tenant_id),
    year: int = None,
    through_month: int = None
):
    """
    Get year-to-date budget performance

    Args:
        year: Year (defaults to current)
        through_month: Last month to include (defaults to current)

    Returns:
        YTD variance analysis
    """
    from src.services.finance.budget import BudgetService
    from datetime import date

    try:
        if not year:
            year = date.today().year
        if not through_month:
            through_month = date.today().month

        budget_service = BudgetService(tenant_id)
        ytd = budget_service.get_ytd_performance(year, through_month)

        return {
            "success": True,
            "data": ytd
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"Failed to get YTD performance: {str(e)}"
                }
            }
        )


@app.get("/api/finance/budget/metrics")
async def get_budget_metrics(
    tenant_id: str = Depends(get_current_tenant_id),
    year: int = None,
    month: int = None
):
    """
    Get key budget metrics for dashboard display

    Returns:
        Status, monthly actuals vs budget, YTD, and top overages
    """
    from src.services.finance.budget import BudgetService

    try:
        budget_service = BudgetService(tenant_id)
        metrics = budget_service.get_dashboard_metrics(year, month)

        return {
            "success": True,
            "data": metrics
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"Failed to get budget metrics: {str(e)}"
                }
            }
        )


@app.post("/api/finance/budget")
async def save_budget(
    tenant_id: str = Depends(get_current_tenant_id),
    request_body: dict = Body(...)
):
    """
    Save or update budget for a month

    Request body:
        year: Budget year
        month: Budget month (1-12)
        categories: Budget categories with amounts

    Returns:
        Saved budget data
    """
    from src.services.finance.budget import BudgetService

    try:
        year = request_body.get("year")
        month = request_body.get("month")
        categories = request_body.get("categories")

        if not year or not month:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "year and month are required"
                    }
                }
            )

        if not categories:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "categories are required"
                    }
                }
            )

        budget_service = BudgetService(tenant_id)
        budget = budget_service.save_budget(year, month, categories)

        return {
            "success": True,
            "data": budget
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"Failed to save budget: {str(e)}"
                }
            }
        )

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
# QBO SYNC
# ============================================================

@app.post("/api/sync/qbo")
async def sync_qbo_transactions(
    tenant_id: str,
    start_date: str = None,
    end_date: str = None,
    incremental: bool = False,
    auto_classify: bool = False
):
    """
    Sync transactions from QuickBooks to Supabase
    
    Args:
        tenant_id: Tenant UUID
        start_date: Start date in YYYY-MM-DD format (optional, defaults to 30 days ago)
        end_date: End date in YYYY-MM-DD format (optional, defaults to today)
        incremental: If True, only sync since last sync (ignores start_date/end_date)
        auto_classify: If True, automatically classify synced transactions
    
    Returns:
        Sync results with count and status
    """
    from src.services.qbo.sync import QBOSyncService
    from src.services.qbo.classification_workflow import ClassificationWorkflow

    try:
        sync_service = QBOSyncService(tenant_id)
        
        if incremental:
            sync_result = sync_service.sync_incremental()
        else:
            sync_result = sync_service.sync_transactions(start_date, end_date)
        
        # Auto-classify if requested and sync was successful
        classification_result = None
        if auto_classify and sync_result.get("synced_count", 0) > 0:
            workflow = ClassificationWorkflow(tenant_id)
            classification_result = workflow.classify_unclassified_transactions(limit=100)
        
        return {
            "status": "success",
            "sync_result": sync_result,
            "classification_result": classification_result
        }
    except ValueError as e:
        raise HTTPException(400, f"Sync failed: {str(e)}")
    except Exception as e:
        raise HTTPException(500, f"Sync error: {str(e)}")

@app.post("/api/transactions/classify/batch")
async def classify_transactions_batch(
    tenant_id: str,
    limit: int = 50,
    transaction_types: list[str] = None
):
    """
    Classify unclassified transactions in batch

    Args:
        tenant_id: Tenant UUID
        limit: Maximum number of transactions to classify
        transaction_types: Optional list of transaction types to filter

    Returns:
        Classification results
    """
    from src.services.qbo.classification_workflow import ClassificationWorkflow

    try:
        workflow = ClassificationWorkflow(tenant_id)
        result = workflow.classify_unclassified_transactions(
            limit=limit,
            transaction_types=transaction_types
        )
        return result
    except Exception as e:
        raise HTTPException(500, f"Classification error: {str(e)}")


# ============================================================
# PAYROLL DATA API
# ============================================================

@app.get("/api/qbo/payroll/accounts")
async def get_payroll_accounts(tenant_id: str):
    """
    Get all payroll-related accounts from QuickBooks Chart of Accounts.

    Identifies accounts by:
    - AccountSubType (PayrollExpenses, PayrollTaxExpenses, etc.)
    - Account names containing payroll keywords

    Returns:
        List of payroll accounts with classifications
    """
    from src.services.qbo.client import QBOClient

    try:
        client = QBOClient(tenant_id)
        accounts = client.get_payroll_accounts()

        return {
            "success": True,
            "data": {
                "accounts": accounts,
                "count": len(accounts)
            }
        }
    except ValueError as e:
        raise HTTPException(400, f"QBO Error: {str(e)}")
    except Exception as e:
        raise HTTPException(500, f"Failed to get payroll accounts: {str(e)}")


@app.get("/api/qbo/payroll/transactions")
async def get_payroll_transactions(
    tenant_id: str,
    start_date: str = None,
    end_date: str = None
):
    """
    Get all transactions posted to payroll-related accounts.

    This captures payroll expenses from:
    - Direct payroll entries from QBO Payroll
    - Journal entries from external payroll (Gusto, ADP)
    - Manual payroll entries

    Args:
        tenant_id: Tenant UUID
        start_date: Start date YYYY-MM-DD (defaults to 1 year ago)
        end_date: End date YYYY-MM-DD (defaults to today)

    Returns:
        List of payroll transactions with account details
    """
    from src.services.qbo.client import QBOClient

    try:
        client = QBOClient(tenant_id)
        transactions = client.get_payroll_transactions(start_date, end_date)

        return {
            "success": True,
            "data": {
                "transactions": transactions,
                "count": len(transactions)
            }
        }
    except ValueError as e:
        raise HTTPException(400, f"QBO Error: {str(e)}")
    except Exception as e:
        raise HTTPException(500, f"Failed to get payroll transactions: {str(e)}")


@app.get("/api/qbo/payroll/summary")
async def get_payroll_summary(
    tenant_id: str,
    start_date: str = None,
    end_date: str = None
):
    """
    Get summarized payroll data for analysis and overhead calculation.

    Returns:
        - Total payroll expense
        - Breakdown by classification (wages, taxes, benefits, workers comp)
        - Monthly trend
        - Average monthly payroll (for break-even calculation)
    """
    from src.services.qbo.client import QBOClient

    try:
        client = QBOClient(tenant_id)
        summary = client.get_payroll_summary(start_date, end_date)

        return {
            "success": True,
            "data": summary
        }
    except ValueError as e:
        raise HTTPException(400, f"QBO Error: {str(e)}")
    except Exception as e:
        raise HTTPException(500, f"Failed to get payroll summary: {str(e)}")


@app.get("/api/qbo/overhead/summary")
async def get_overhead_summary(tenant_id: str):
    """
    Get comprehensive overhead analysis with break-even calculation.

    This is the foundation for the $99 Profit Leak Report.

    Automatically classifies ALL expense accounts as:
    - OVERHEAD: Fixed costs (rent, utilities, admin payroll, insurance, etc.)
    - JOB COSTS: Variable costs (materials, labor, subs, equipment rental)

    Returns:
        - Total overhead by category
        - Job costs by category
        - Calculated gross margin from actual data
        - Break-even at current and scenario margins
        - Confidence scores for classification accuracy
    """
    from src.services.qbo.client import QBOClient

    try:
        client = QBOClient(tenant_id)
        analysis = client.get_overhead_analysis()

        return {
            "success": True,
            "data": analysis
        }
    except ValueError as e:
        raise HTTPException(400, f"QBO Error: {str(e)}")
    except Exception as e:
        raise HTTPException(500, f"Failed to get overhead analysis: {str(e)}")


@app.get("/api/qbo/overhead/demo")
async def get_overhead_demo():
    """
    Demo endpoint returning simulated data for a $2M roofing contractor
    with all 5 profit leaks. Use this to test the Profit Leaks UI.

    The 5 Profit Leaks simulated:
    1. LOW GROSS MARGIN (18%) - underpricing jobs
    2. HIGH MATERIALS COST (42% of revenue) - material waste/theft
    3. LABOR INEFFICIENCY (28% of revenue) - crew productivity issues
    4. OVERHEAD CREEP (24% of revenue) - excessive fixed costs
    5. UNTRACKED EXPENSES ($48k) - money leaking through mixed expenses
    """
    from datetime import datetime, timedelta

    # Calculate date range (last 12 months)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    # $2M annual roofing contractor with problems
    annual_revenue = 2_000_000
    monthly_revenue = annual_revenue / 12  # $166,667

    # LEAK 1: Low gross margin (18% instead of healthy 35%+)
    # This means job costs are 82% of revenue
    gross_margin_pct = 0.18
    job_costs_pct = 1 - gross_margin_pct  # 82%
    annual_job_costs = annual_revenue * job_costs_pct  # $1,640,000
    monthly_job_costs = annual_job_costs / 12  # $136,667

    # LEAK 2: High materials (42% of revenue, should be 30-35%)
    materials = annual_revenue * 0.42  # $840,000

    # LEAK 3: Labor inefficiency (28% of revenue, should be 20-22%)
    direct_labor = annual_revenue * 0.28  # $560,000

    # Other job costs (12% of revenue)
    subcontractors = annual_revenue * 0.06  # $120,000
    equipment = annual_revenue * 0.03  # $60,000
    disposal = annual_revenue * 0.02  # $40,000
    permits = annual_revenue * 0.01  # $20,000

    # LEAK 4: High overhead (24% of revenue, should be 15-18%)
    annual_overhead = annual_revenue * 0.24  # $480,000
    monthly_overhead = annual_overhead / 12  # $40,000

    # Overhead breakdown (typical problem areas)
    overhead_by_category = {
        "payroll": 168_000,        # Admin salaries - high at $14k/month
        "insurance": 84_000,       # GL + WC + Auto - $7k/month
        "rent": 48_000,            # Yard/office rent - $4k/month
        "marketing": 60_000,       # Advertising spend - $5k/month (maybe not generating ROI)
        "utilities": 18_000,       # Electric/gas/water - $1.5k/month
        "professional_fees": 24_000,  # Accountant/lawyer - $2k/month
        "office": 30_000,          # Supplies/software - $2.5k/month
        "depreciation": 36_000,    # Vehicle/equipment depreciation - $3k/month
        "other_overhead": 12_000,  # Misc - $1k/month
    }

    # Job costs breakdown
    job_costs_by_category = {
        "materials": materials,        # $840,000 - LEAK!
        "direct_labor": direct_labor,  # $560,000 - LEAK!
        "subcontractors": subcontractors,
        "equipment": equipment,
        "disposal": disposal,
        "permits": permits,
    }

    # Monthly overhead trend (simulate 12 months with some variation)
    monthly_trend = {}
    base_overhead = monthly_overhead
    for i in range(12):
        month_date = start_date + timedelta(days=30*i)
        month_key = month_date.strftime("%Y-%m")
        variation = 1 + (0.1 * ((i % 3) - 1))  # +/- 10% variation
        monthly_trend[month_key] = {
            cat: round(val / 12 * variation, 2)
            for cat, val in overhead_by_category.items()
        }

    # LEAK 5: Mixed expenses (untracked costs)
    mixed_expenses_total = 48_000  # $4k/month in unclassified expenses
    mixed_expenses_count = 156  # ~13 transactions per month unclassified

    # Calculate break-even at current margin
    break_even_monthly = monthly_overhead / gross_margin_pct  # $40k / 0.18 = $222,222
    break_even_annual = break_even_monthly * 12

    # Break-even scenarios
    scenarios = {
        "20%": {"margin": 0.20, "monthly_break_even": monthly_overhead / 0.20, "annual_break_even": annual_overhead / 0.20, "is_current": False},
        "25%": {"margin": 0.25, "monthly_break_even": monthly_overhead / 0.25, "annual_break_even": annual_overhead / 0.25, "is_current": False},
        "30%": {"margin": 0.30, "monthly_break_even": monthly_overhead / 0.30, "annual_break_even": annual_overhead / 0.30, "is_current": False},
        "35%": {"margin": 0.35, "monthly_break_even": monthly_overhead / 0.35, "annual_break_even": annual_overhead / 0.35, "is_current": False},
        "40%": {"margin": 0.40, "monthly_break_even": monthly_overhead / 0.40, "annual_break_even": annual_overhead / 0.40, "is_current": False},
    }

    # Return the simulated analysis
    demo_analysis = {
        "period": {
            "start": start_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d"),
            "months": 12
        },
        "overhead": {
            "total": annual_overhead,
            "monthly_average": monthly_overhead,
            "by_category": overhead_by_category,
            "monthly_trend": monthly_trend,
            "transaction_count": 847  # Realistic transaction count
        },
        "job_costs": {
            "total": annual_job_costs,
            "monthly_average": monthly_job_costs,
            "by_category": job_costs_by_category,
            "transaction_count": 1423  # Realistic transaction count
        },
        "revenue": {
            "total": annual_revenue,
            "monthly_average": monthly_revenue
        },
        "profitability": {
            "gross_margin": gross_margin_pct,
            "gross_margin_pct": f"{gross_margin_pct * 100:.1f}%",
            "gross_profit_monthly": monthly_revenue * gross_margin_pct
        },
        "break_even": {
            "current_margin": {
                "margin": gross_margin_pct,
                "monthly": break_even_monthly,
                "annual": break_even_annual
            },
            "scenarios": scenarios
        },
        "mixed_expenses": {
            "total": mixed_expenses_total,
            "count": mixed_expenses_count,
            "note": "These expenses couldn't be automatically classified - review needed"
        },
        "confidence": {
            "overhead_avg": 0.72,  # Lower confidence due to mixed expenses
            "job_cost_avg": 0.68   # Lower confidence
        },
        "_demo_note": "SIMULATED DATA: $2M roofing contractor with 5 profit leaks"
    }

    return {
        "success": True,
        "data": demo_analysis,
        "demo": True
    }


@app.get("/api/qbo/expenses/classified")
async def get_expenses_classified(tenant_id: str):
    """
    Get all expense accounts with overhead vs job cost classification.

    Each account is classified as:
    - overhead: Fixed costs that don't scale with jobs
    - job_cost: Variable costs that scale with job volume
    - mixed: Needs manual review

    Includes confidence score and classification reasoning.
    """
    from src.services.qbo.client import QBOClient

    try:
        client = QBOClient(tenant_id)
        accounts = client.get_expense_accounts_classified()

        # Group by classification
        overhead = [a for a in accounts if a["classification"] == "overhead"]
        job_cost = [a for a in accounts if a["classification"] == "job_cost"]
        mixed = [a for a in accounts if a["classification"] == "mixed"]

        return {
            "success": True,
            "data": {
                "accounts": accounts,
                "summary": {
                    "overhead_count": len(overhead),
                    "job_cost_count": len(job_cost),
                    "mixed_count": len(mixed),
                    "total": len(accounts)
                },
                "by_classification": {
                    "overhead": overhead,
                    "job_cost": job_cost,
                    "mixed": mixed
                }
            }
        }
    except ValueError as e:
        raise HTTPException(400, f"QBO Error: {str(e)}")
    except Exception as e:
        raise HTTPException(500, f"Failed to classify expenses: {str(e)}")


@app.get("/api/qbo/profit-leak-report")
async def get_profit_leak_report(tenant_id: str):
    """
    Generate the $99 Instant Profit Leak Report.

    This is the tripwire offer deliverable - shows:
    1. Break-even floor (monthly revenue needed to cover overhead)
    2. True overhead run-rate by category
    3. Top profit leaks ranked by $ impact
    4. Gross margin from actual job cost data

    The report identifies where money is leaking and
    quantifies the opportunity to recover it.
    """
    from src.services.qbo.client import QBOClient

    try:
        client = QBOClient(tenant_id)

        # Get comprehensive overhead analysis
        analysis = client.get_overhead_analysis()

        # Get company info
        company_info = client.get_company_info()

        # Get cash position
        cash_balance = client.get_cash_accounts_balance()

        # Identify profit leaks (overhead categories that are high relative to revenue)
        profit_leaks = []
        overhead_cats = analysis["overhead"]["by_category"]
        monthly_revenue = analysis["revenue"]["monthly_average"]

        for category, amount in overhead_cats.items():
            if monthly_revenue > 0:
                pct_of_revenue = (amount / analysis["period"]["months"]) / monthly_revenue
                # Flag if overhead category is > 5% of revenue (except rent which can be higher)
                threshold = 0.10 if category == "rent" else 0.05
                if pct_of_revenue > threshold:
                    profit_leaks.append({
                        "category": category,
                        "monthly_amount": round(amount / analysis["period"]["months"], 2),
                        "annual_impact": round(amount, 2),
                        "pct_of_revenue": round(pct_of_revenue * 100, 1),
                        "severity": "high" if pct_of_revenue > threshold * 2 else "medium",
                        "recommendation": _get_leak_recommendation(category, pct_of_revenue)
                    })

        # Sort by annual impact
        profit_leaks.sort(key=lambda x: -x["annual_impact"])

        # Calculate key metrics
        break_even = analysis["break_even"]["current_margin"]
        gross_margin = analysis["profitability"]["gross_margin"]

        # Determine overall health
        if gross_margin >= 0.35:
            margin_health = "healthy"
            margin_message = "Your gross margin is strong for the roofing industry."
        elif gross_margin >= 0.25:
            margin_health = "average"
            margin_message = "Your gross margin is average. There's room for improvement."
        else:
            margin_health = "concerning"
            margin_message = "Your gross margin is below industry average. Review job pricing and costs."

        return {
            "success": True,
            "data": {
                "company": company_info.get("company_name", "Your Company"),
                "report_date": datetime.utcnow().isoformat(),
                "period": analysis["period"],

                "executive_summary": {
                    "monthly_break_even": break_even["monthly"],
                    "annual_break_even": break_even["annual"],
                    "current_gross_margin": analysis["profitability"]["gross_margin_pct"],
                    "margin_health": margin_health,
                    "margin_message": margin_message,
                    "cash_position": round(cash_balance, 2),
                    "total_profit_leaks": len(profit_leaks),
                    "annual_leak_potential": round(sum(l["annual_impact"] for l in profit_leaks), 2)
                },

                "break_even_analysis": {
                    "your_break_even": break_even,
                    "scenarios": analysis["break_even"]["scenarios"],
                    "insight": f"You need ${break_even['monthly']:,.0f}/month in revenue just to cover overhead. Every dollar below this is a loss."
                },

                "overhead_breakdown": {
                    "monthly_total": analysis["overhead"]["monthly_average"],
                    "by_category": {
                        k: round(v / analysis["period"]["months"], 2)
                        for k, v in analysis["overhead"]["by_category"].items()
                    },
                    "transaction_count": analysis["overhead"]["transaction_count"]
                },

                "job_cost_breakdown": {
                    "monthly_total": analysis["job_costs"]["monthly_average"],
                    "by_category": {
                        k: round(v / analysis["period"]["months"], 2)
                        for k, v in analysis["job_costs"]["by_category"].items()
                    },
                    "transaction_count": analysis["job_costs"]["transaction_count"]
                },

                "profit_leaks": profit_leaks[:5],  # Top 5 leaks

                "next_steps": [
                    "Review the top profit leaks and their recommendations",
                    "Compare your break-even to your average monthly revenue",
                    "Schedule a 90-day Profit Leak Proofing engagement to fix these issues"
                ],

                "classification_confidence": analysis["confidence"],

                "needs_review": {
                    "count": analysis["mixed_expenses"]["count"],
                    "total": analysis["mixed_expenses"]["total"],
                    "note": analysis["mixed_expenses"]["note"]
                }
            }
        }
    except ValueError as e:
        raise HTTPException(400, f"QBO Error: {str(e)}")
    except Exception as e:
        raise HTTPException(500, f"Failed to generate profit leak report: {str(e)}")


def _get_leak_recommendation(category: str, pct_of_revenue: float) -> str:
    """Get recommendation for a profit leak category."""
    recommendations = {
        "professional_fees": "Review if all legal/accounting services are necessary. Consider fixed-fee arrangements.",
        "marketing": "Audit marketing spend ROI. Focus on channels with proven lead generation.",
        "insurance": "Shop insurance annually. Bundle policies. Review coverage for unnecessary riders.",
        "utilities": "Audit utility usage. Consider energy efficiency upgrades. Negotiate rates.",
        "rent": "If lease is ending, negotiate or consider relocation. Sublease unused space.",
        "office": "Review subscriptions and supplies. Eliminate unused services.",
        "admin_payroll": "Audit admin roles. Consider automation for repetitive tasks.",
        "other_overhead": "Review and categorize these expenses. Many may be reducible.",
        "depreciation": "This is non-cash. Focus on other categories for immediate savings.",
    }
    return recommendations.get(category, "Review this category for potential savings opportunities.")

# ============================================================
# VALUATION API
# ============================================================

@app.get("/api/valuation/snapshot")
async def get_valuation_snapshot(tenant_id: str = Depends(get_current_tenant_id)):
    """
    Get the latest valuation snapshot for a tenant
    
    Returns the most recent valuation calculation with TTM financials,
    tier assessment, and confidence scoring.
    """
    try:
        # Get latest snapshot
        result = supabase.table("valuation_snapshots")\
            .select("*")\
            .eq("tenant_id", tenant_id)\
            .order("as_of_date", desc=True)\
            .order("created_at", desc=True)\
            .limit(1)\
            .execute()
        
        if not result.data:
            return {
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "No valuation snapshot found for this tenant"
                }
            }
        
        snapshot = result.data[0]
        
        # Get driver scores for this snapshot
        driver_scores_result = supabase.table("driver_scores")\
            .select("*")\
            .eq("valuation_snapshot_id", snapshot["id"])\
            .execute()
        
        # Build drivers summary from driver scores
        # Convert from 0-100 scale to 0-5 scale for API response
        drivers_summary = {}
        for driver in driver_scores_result.data:
            score_value = driver["score"] / 20.0 if driver["score"] <= 100 else 5.0
            drivers_summary[driver["driver_key"]] = round(score_value, 2)
        
        # If no drivers linked, try to get from drivers_json
        if not drivers_summary and snapshot.get("drivers_json"):
            drivers_summary = snapshot["drivers_json"]
        
        # Calculate value delta from previous snapshot if available
        prev_result = supabase.table("valuation_snapshots")\
            .select("ev_low, ev_high")\
            .eq("tenant_id", tenant_id)\
            .lt("as_of_date", snapshot["as_of_date"])\
            .order("as_of_date", desc=True)\
            .limit(1)\
            .execute()
        
        value_delta = None
        if prev_result.data:
            prev_ev_avg = (float(prev_result.data[0]["ev_low"]) + float(prev_result.data[0]["ev_high"])) / 2
            curr_ev_avg = (float(snapshot["ev_low"]) + float(snapshot["ev_high"])) / 2
            delta = curr_ev_avg - prev_ev_avg
            pct_change = (delta / prev_ev_avg * 100) if prev_ev_avg > 0 else 0
            value_delta = {
                "from_previous": round(delta, 2),
                "percentage_change": round(pct_change, 2)
            }
        
        # Build automation flags
        automation_flags = {
            "requires_review": snapshot.get("review_required", False),
            "high_confidence": snapshot.get("confidence_score", 0) >= 80,
            "tier_change": False  # TODO: Compare with previous snapshot tier
        }
        
        snapshot_data = {
            "id": snapshot["id"],
            "tenant_id": snapshot["tenant_id"],
            "as_of_date": snapshot["as_of_date"],
            "ttm_revenue": float(snapshot["ttm_revenue"]),
            "ttm_sde": float(snapshot["ttm_sde"]),
            "ttm_ebitda": float(snapshot["ttm_ebitda"]),
            "tier": snapshot["tier"],
            "multiple_low": float(snapshot["multiple_low"]),
            "multiple_high": float(snapshot["multiple_high"]),
            "ev_low": float(snapshot["ev_low"]),
            "ev_high": float(snapshot["ev_high"]),
            "confidence_score": snapshot["confidence_score"],
            "drivers_summary": drivers_summary,
            "created_at": snapshot["created_at"],
            "updated_at": snapshot["updated_at"]
        }
        
        if value_delta:
            snapshot_data["value_delta"] = value_delta
        snapshot_data["automation_flags"] = automation_flags
        
        return {
            "success": True,
            "data": {
                "snapshot": snapshot_data
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"Failed to retrieve valuation snapshot: {str(e)}"
                }
            }
        )

@app.post("/api/valuation/snapshot")
async def create_valuation_snapshot(
    tenant_id: str = Depends(get_current_tenant_id),
    request_body: dict = Body(default={})
):
    """
    Trigger recalculation and create a new valuation snapshot
    
    Request body:
        as_of_date: Date for snapshot (ISO format YYYY-MM-DD). Defaults to today.
        force_recalculation: Force recalculation even if snapshot exists for date (default: False)
        include_projections: Include future projections in calculation (default: True)
    
    Returns:
        Created snapshot with processing metadata
    """
    from datetime import date
    
    try:
        # Parse request body parameters
        as_of_date = request_body.get("as_of_date")
        force_recalculation = request_body.get("force_recalculation", False)
        include_projections = request_body.get("include_projections", True)
        
        # Parse as_of_date or use today
        if as_of_date:
            snapshot_date = date.fromisoformat(as_of_date)
        else:
            snapshot_date = date.today()
        
        # Use ValuationEngine to calculate valuation
        from src.services.valuation.engine import ValuationEngine
        import time
        
        start_time = time.time()
        
        try:
            engine = ValuationEngine(tenant_id)
            snapshot_data = engine.create_valuation_snapshot(
                as_of_date=snapshot_date,
                force_recalculation=force_recalculation
            )
            
            # Insert snapshot into database
            result = supabase.table("valuation_snapshots")\
                .insert(snapshot_data)\
                .execute()
            
            if not result.data:
                raise HTTPException(
                    status_code=500,
                    detail={
                        "success": False,
                        "error": {
                            "code": "DATABASE_ERROR",
                            "message": "Failed to save valuation snapshot"
                        }
                    }
                )
            
            snapshot = result.data[0]
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            return {
                "success": True,
                "data": {
                    "snapshot": {
                        "id": snapshot["id"],
                        "tenant_id": snapshot["tenant_id"],
                        "as_of_date": snapshot["as_of_date"],
                        "ttm_revenue": float(snapshot["ttm_revenue"]),
                        "ttm_sde": float(snapshot["ttm_sde"]),
                        "ttm_ebitda": float(snapshot["ttm_ebitda"]),
                        "tier": snapshot["tier"],
                        "multiple_low": float(snapshot["multiple_low"]),
                        "multiple_high": float(snapshot["multiple_high"]),
                        "ev_low": float(snapshot["ev_low"]),
                        "ev_high": float(snapshot["ev_high"]),
                        "confidence_score": snapshot["confidence_score"],
                        "drivers_json": snapshot.get("drivers_json", {}),
                        "created_at": snapshot["created_at"],
                        "updated_at": snapshot["updated_at"]
                    },
                    "processing_time_ms": processing_time_ms,
                    "data_sources_used": ["books_os", "driver_scores", "market_data"]
                }
            }
        except ValueError as e:
            # ValuationEngine raises ValueError for business logic errors
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": str(e)
                    }
                }
            )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": f"Invalid date format: {str(e)}"
                }
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"Failed to create valuation snapshot: {str(e)}"
                }
            }
        )

@app.get("/api/valuation/snapshots")
async def get_valuation_snapshots(
    tenant_id: str = Depends(get_current_tenant_id),
    limit: int = 12,
    page: int = 1
):
    """
    Get historical valuation snapshots for timeline
    
    Args:
        tenant_id: Tenant UUID
        limit: Number of snapshots per page (default: 12, max: 100)
        page: Page number (default: 1)
    
    Returns:
        List of historical snapshots with pagination
    """
    try:
        limit = min(limit, 100)  # Cap at 100
        offset = (page - 1) * limit
        
        result = supabase.table("valuation_snapshots")\
            .select("*")\
            .eq("tenant_id", tenant_id)\
            .order("as_of_date", desc=True)\
            .order("created_at", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        
        # Get total count for pagination
        count_result = supabase.table("valuation_snapshots")\
            .select("id", count="exact")\
            .eq("tenant_id", tenant_id)\
            .execute()
        
        total = count_result.count if hasattr(count_result, 'count') else len(result.data)
        total_pages = (total + limit - 1) // limit if total > 0 else 1
        
        snapshots = []
        for snap in result.data:
            snapshots.append({
                "id": snap["id"],
                "tenant_id": snap["tenant_id"],
                "as_of_date": snap["as_of_date"],
                "ttm_revenue": float(snap["ttm_revenue"]),
                "ttm_sde": float(snap["ttm_sde"]),
                "ttm_ebitda": float(snap["ttm_ebitda"]),
                "tier": snap["tier"],
                "multiple_low": float(snap["multiple_low"]),
                "multiple_high": float(snap["multiple_high"]),
                "ev_low": float(snap["ev_low"]),
                "ev_high": float(snap["ev_high"]),
                "confidence_score": snap["confidence_score"],
                "created_at": snap["created_at"],
                "updated_at": snap["updated_at"]
            })
        
        return {
            "success": True,
            "data": {
                "snapshots": snapshots,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "pages": total_pages
                }
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"Failed to retrieve valuation snapshots: {str(e)}"
                }
            }
        )

@app.get("/api/valuation/drivers")
async def get_driver_scores(
    tenant_id: str = Depends(get_current_tenant_id),
    as_of_date: str = None,
    driver_key: str = None,
    include_evidence: bool = False
):
    """
    Get driver scores for a tenant
    
    Args:
        tenant_id: Tenant UUID
        as_of_date: Specific date (ISO format YYYY-MM-DD). Defaults to latest.
        driver_key: Filter by specific driver key
        include_evidence: Include supporting evidence details
    
    Returns:
        Driver scores with overall assessment
    """
    from datetime import date
    
    try:
        query = supabase.table("driver_scores")\
            .select("*")\
            .eq("tenant_id", tenant_id)
        
        # Filter by date if provided
        if as_of_date:
            query = query.eq("as_of_date", as_of_date)
        else:
            # Get latest date for this tenant
            latest_date_result = supabase.table("driver_scores")\
                .select("as_of_date")\
                .eq("tenant_id", tenant_id)\
                .order("as_of_date", desc=True)\
                .limit(1)\
                .execute()
            
            if latest_date_result.data:
                query = query.eq("as_of_date", latest_date_result.data[0]["as_of_date"])
            else:
                return {
                    "success": True,
                    "data": {
                        "scores": [],
                        "overall_score": 0,
                        "tier_impact": None
                    }
                }
        
        # Filter by driver if provided
        if driver_key:
            query = query.eq("driver_key", driver_key)
        
        query = query.order("driver_key")
        
        result = query.execute()
        
        if not result.data:
            return {
                "success": True,
                "data": {
                    "scores": [],
                    "overall_score": 0,
                    "tier_impact": None
                }
            }
        
        # Process scores
        scores = []
        total_score = 0
        count = 0
        
        for driver in result.data:
            # Driver scores are stored as 0-100 in DB, convert to 0-5 scale for API
            # Assuming score of 0-100 maps to 0-5 (divide by 20)
            score_value = driver["score"] / 20.0 if driver["score"] <= 100 else 5.0
            
            score_data = {
                "id": driver["id"],
                "tenant_id": driver["tenant_id"],
                "as_of_date": driver["as_of_date"],
                "driver_key": driver["driver_key"],
                "score": round(score_value, 2),
                "max_score": 5.0,  # Matador uses 1-5 scale
                "confidence": driver["confidence"],
                "computed_by": driver["computed_by"],
                "created_at": driver["created_at"]
            }
            
            # Include evidence if requested
            if include_evidence and driver.get("evidence_refs"):
                score_data["evidence_refs"] = driver["evidence_refs"]
            
            # Include additional details if available
            if driver.get("impact_on_multiple"):
                score_data["impact_on_multiple"] = float(driver["impact_on_multiple"])
            
            # Calculate improvement potential (max score - current score)
            score_data["improvement_potential"] = round(5.0 - score_value, 1)
            
            scores.append(score_data)
            total_score += score_value
            count += 1
        
        # Calculate overall score (average)
        overall_score = round(total_score / count, 2) if count > 0 else 0
        
        # Determine tier impact based on overall score
        if overall_score < 3.0:
            tier_impact = "below_avg"
        elif overall_score < 4.0:
            tier_impact = "avg"
        else:
            tier_impact = "above_avg"
        
        return {
            "success": True,
            "data": {
                "scores": scores,
                "overall_score": overall_score,
                "tier_impact": tier_impact
            }
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": f"Invalid date format: {str(e)}"
                }
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"Failed to retrieve driver scores: {str(e)}"
                }
            }
        )


@app.post("/api/valuation/simulate")
async def simulate_valuation(
    tenant_id: str = Depends(get_current_tenant_id),
    request_body: dict = Body(...)
):
    """
    Simulate valuation under "what-if" levers.

    Body:
      { levers: { recurring_revenue_delta, margin_delta, owner_hours_delta, productivity_delta } }

    Response:
      { projected_ebitda, projected_multiple, projected_ev_low, projected_ev_high }
    """
    try:
        levers = request_body.get("levers") or {}
        rr_delta = float(levers.get("recurring_revenue_delta", 0.0))  # fraction
        margin_delta = float(levers.get("margin_delta", 0.0))  # fraction points
        owner_hours_delta = float(levers.get("owner_hours_delta", 0.0))  # hours (new - current)
        prod_delta = float(levers.get("productivity_delta", 0.0))  # fraction

        # Load latest snapshot as baseline
        snap_res = supabase.table("valuation_snapshots")\
            .select("ttm_revenue, ttm_ebitda, multiple_low, multiple_high, tier")\
            .eq("tenant_id", tenant_id)\
            .order("as_of_date", desc=True)\
            .order("created_at", desc=True)\
            .limit(1)\
            .execute()

        if not snap_res.data:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {"code": "NOT_FOUND", "message": "No valuation snapshot found to simulate from"}
                }
            )

        snap = snap_res.data[0]
        base_revenue = float(snap.get("ttm_revenue") or 0)
        base_ebitda = float(snap.get("ttm_ebitda") or 0)
        base_multiple_low = float(snap.get("multiple_low") or 0)
        base_multiple_high = float(snap.get("multiple_high") or 0)
        base_tier = snap.get("tier") or "below_avg"

        # --- First-pass projection model ---
        # Revenue lever scales revenue
        projected_revenue = max(0.0, base_revenue * (1.0 + rr_delta))

        # Margin lever adjusts EBITDA margin directly
        base_margin = (base_ebitda / base_revenue) if base_revenue > 0 else 0.0
        projected_margin = max(-1.0, min(1.0, base_margin + margin_delta))

        # Productivity lever: partial flow-through into margin (assumption)
        projected_margin = max(-1.0, min(1.0, projected_margin + (0.35 * prod_delta)))

        projected_ebitda = round(projected_revenue * projected_margin, 2)

        # Multiple: baseline average ± adjustments
        base_multiple_avg = (
            (base_multiple_low + base_multiple_high) / 2.0
            if (base_multiple_low and base_multiple_high)
            else 0.0
        )

        # Owner hours reduction improves multiple (assume 40hr baseline if unknown)
        assumed_current_owner_hours = 40.0
        owner_improvement = 0.0
        if owner_hours_delta < 0:
            owner_improvement = min(1.0, (-owner_hours_delta) / assumed_current_owner_hours)

        multiple_uplift = (0.6 * owner_improvement) + (0.3 * max(0.0, prod_delta))
        multiple_penalty = 0.4 * max(0.0, -prod_delta)
        projected_multiple = round(max(1.5, base_multiple_avg + multiple_uplift - multiple_penalty), 2)

        # Keep a reasonable spread around multiple for range
        spread = max(
            0.25,
            (base_multiple_high - base_multiple_low) / 2.0
            if base_multiple_high > base_multiple_low
            else 0.35
        )
        projected_multiple_low = max(1.0, projected_multiple - spread)
        projected_multiple_high = projected_multiple + spread

        # EV range uses EBITDA if positive; otherwise fall back to tier multiples
        from src.services.valuation.engine import ValuationEngine
        engine = ValuationEngine(tenant_id)

        if projected_ebitda > 0:
            projected_ev_low = round(projected_ebitda * projected_multiple_low, 2)
            projected_ev_high = round(projected_ebitda * projected_multiple_high, 2)
        else:
            applied = engine.apply_multiples(sde=0.0, ebitda=projected_ebitda, tier=base_tier)
            projected_ev_low = float(applied["ev_low"])
            projected_ev_high = float(applied["ev_high"])

        return {
            "projected_ebitda": projected_ebitda,
            "projected_multiple": projected_multiple,
            "projected_ev_low": projected_ev_low,
            "projected_ev_high": projected_ev_high
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"Failed to simulate valuation: {str(e)}"
                }
            }
        )


@app.get("/api/valuation/exit-readiness")
async def get_exit_readiness(tenant_id: str = Depends(get_current_tenant_id)):
    """
    Exit readiness snapshot (first-pass).

    Response shape is optimized for the frontend ExitReadiness component.
    """
    try:
        items = [
            ("financial_statements", "Financial statements (3-5 years)"),
            ("tax_returns", "Tax returns"),
            ("ar_ap_aging", "AR/AP aging reports"),
            ("asset_list", "Asset list"),
            ("org_chart", "Org chart"),
            ("kpi_dashboard", "KPI dashboard"),
            ("safety_insurance", "Safety/insurance docs"),
        ]

        # Pull doc registry from DB (uploaded docs)
        docs_res = supabase.table("exit_readiness_documents")\
            .select("id, checklist_key, storage_bucket, storage_path, file_name, content_type, size_bytes, created_at")\
            .eq("tenant_id", tenant_id)\
            .order("created_at", desc=True)\
            .execute()

        uploaded_keys = set()
        files_by_key: dict[str, list[dict]] = {}
        for row in (docs_res.data or []):
            key = row.get("checklist_key")
            if not key:
                continue
            uploaded_keys.add(key)

            bucket = row.get("storage_bucket") or "deal-room"
            path = row.get("storage_path")
            signed_url = None
            if path:
                try:
                    signed = supabase.storage.from_(bucket).create_signed_url(path, 60 * 60)
                    # python client may return dict-like or object-like responses
                    signed_url = signed.get("signedURL") if isinstance(signed, dict) else getattr(signed, "signedURL", None)
                except Exception:
                    signed_url = None

            files_by_key.setdefault(key, []).append({
                "id": row.get("id"),
                "file_name": row.get("file_name"),
                "content_type": row.get("content_type"),
                "size_bytes": row.get("size_bytes"),
                "created_at": row.get("created_at"),
                "storage_bucket": bucket,
                "storage_path": path,
                "signed_url": signed_url
            })

        checklist = []
        uploaded_count = 0
        for key, label in items:
            uploaded = key in uploaded_keys
            if uploaded:
                uploaded_count += 1
            checklist.append({"key": key, "label": label, "uploaded": uploaded})

        completeness_pct = round((uploaded_count / len(items)) * 100) if items else 0

        # Simple readiness scoring: completeness is the main driver for now.
        readiness_score = int(completeness_pct)
        if readiness_score >= 80:
            status = "green"
        elif readiness_score >= 50:
            status = "yellow"
        else:
            status = "red"

        return {
            "readiness_score": readiness_score,
            "status": status,
            "completeness_pct": completeness_pct,
            "checklist": checklist,
            "files_by_key": files_by_key
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"Failed to retrieve exit readiness: {str(e)}"
                }
            }
        )


@app.post("/api/valuation/exit-readiness/upload")
async def upload_exit_readiness_documents(
    tenant_id: str = Depends(get_current_tenant_id),
    checklist_key: str = Form(...),
    files: list[UploadFile] = File(...)
):
    """
    Upload due diligence documents to Supabase Storage and register them in DB.

    Multipart form:
      - checklist_key: string
      - files: one or more files
    """
    try:
        if not files:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": {"code": "VALIDATION_ERROR", "message": "No files provided"}
                }
            )

        bucket = "deal-room"

        # Best-effort ensure bucket exists (requires service key privileges)
        try:
            supabase.storage.create_bucket(bucket, options={"public": False})
        except Exception:
            pass

        uploaded = []
        for f in files:
            content = await f.read()
            if content is None:
                content = b""

            safe_name = (f.filename or "document").replace("/", "_")
            timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
            storage_path = f"{tenant_id}/exit-readiness/{checklist_key}/{timestamp}_{safe_name}"

            # Upload into Supabase Storage
            supabase.storage.from_(bucket).upload(
                storage_path,
                content,
                file_options={
                    "content-type": f.content_type or "application/octet-stream",
                    "upsert": True
                }
            )

            # Register in DB
            supabase.table("exit_readiness_documents").insert({
                "tenant_id": tenant_id,
                "checklist_key": checklist_key,
                "storage_bucket": bucket,
                "storage_path": storage_path,
                "file_name": f.filename or safe_name,
                "content_type": f.content_type,
                "size_bytes": len(content)
            }).execute()

            uploaded.append({
                "file_name": f.filename or safe_name,
                "storage_bucket": bucket,
                "storage_path": storage_path
            })

        return {"success": True, "uploaded": uploaded}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"Failed to upload exit readiness documents: {str(e)}"
                }
            }
        )


@app.delete("/api/valuation/exit-readiness/files/{doc_id}")
async def delete_exit_readiness_document(
    doc_id: str,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Delete a single uploaded document (storage object + DB metadata)."""
    try:
        row_res = supabase.table("exit_readiness_documents")\
            .select("id, tenant_id, storage_bucket, storage_path")\
            .eq("id", doc_id)\
            .limit(1)\
            .execute()

        if not row_res.data:
            raise HTTPException(
                status_code=404,
                detail={"success": False, "error": {"code": "NOT_FOUND", "message": "Document not found"}}
            )

        row = row_res.data[0]
        if row.get("tenant_id") != tenant_id:
            raise HTTPException(
                status_code=403,
                detail={"success": False, "error": {"code": "FORBIDDEN", "message": "Not allowed"}}
            )

        bucket = row.get("storage_bucket") or "deal-room"
        path = row.get("storage_path")
        if path:
            try:
                supabase.storage.from_(bucket).remove([path])
            except Exception:
                # continue to delete metadata even if storage removal fails (idempotency / drift)
                pass

        supabase.table("exit_readiness_documents")\
            .delete()\
            .eq("id", doc_id)\
            .eq("tenant_id", tenant_id)\
            .execute()

        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {"code": "INTERNAL_ERROR", "message": f"Failed to delete document: {str(e)}"}
            }
        )

@app.get("/api/valuation/roadmap")
async def get_valuation_roadmap(tenant_id: str = Depends(get_current_tenant_id)):
    """
    Get prioritized valuation roadmap items for the tenant.
    """
    try:
        res = supabase.table("roadmap_items")\
            .select("id, driver_key, title, description, expected_impact_ev, effort_level, status, category, completed_at, created_at, updated_at")\
            .eq("tenant_id", tenant_id)\
            .order("expected_impact_ev", desc=True)\
            .order("priority")\
            .order("created_at", desc=True)\
            .execute()

        items = []
        for row in (res.data or []):
            items.append({
                "id": row.get("id"),
                "driver_key": row.get("driver_key"),
                "title": row.get("title"),
                "description": row.get("description"),
                "expected_impact_ev": float(row.get("expected_impact_ev") or 0),
                "effort_level": row.get("effort_level"),
                "status": row.get("status"),
                "category": row.get("category"),
                "completed_at": row.get("completed_at"),
                "created_at": row.get("created_at"),
                "updated_at": row.get("updated_at"),
            })

        # Spec Jam due (quarterly): due if no completed "Spec Jam" since start of current calendar quarter (UTC)
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        quarter_start_month = ((now.month - 1) // 3) * 3 + 1  # 1,4,7,10
        quarter_start = datetime(now.year, quarter_start_month, 1, tzinfo=timezone.utc)

        spec_jam_done_this_quarter = False
        for it in items:
            if (it.get("category") == "strategic") and ("spec jam" in (it.get("title") or "").lower()):
                ca = it.get("completed_at")
                if ca:
                    try:
                        dt = datetime.fromisoformat(str(ca).replace("Z", "+00:00"))
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=timezone.utc)
                        if dt >= quarter_start:
                            spec_jam_done_this_quarter = True
                            break
                    except Exception:
                        pass

        spec_jam_due = not spec_jam_done_this_quarter

        return {
            "success": True,
            "data": {
                "items": items,
                "spec_jam_due": spec_jam_due
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {"code": "INTERNAL_ERROR", "message": f"Failed to retrieve roadmap: {str(e)}"}
            }
        )


@app.patch("/api/valuation/roadmap/{item_id}")
async def update_valuation_roadmap_item(
    item_id: str,
    tenant_id: str = Depends(get_current_tenant_id),
    request_body: dict = Body(...)
):
    """
    Update roadmap item status.
    Body: { status: 'pending' | 'in_progress' | 'completed' }
    """
    try:
        status = request_body.get("status")
        if status not in ("pending", "in_progress", "completed"):
            raise HTTPException(
                status_code=400,
                detail={"success": False, "error": {"code": "VALIDATION_ERROR", "message": "Invalid status"}}
            )

        patch = {"status": status, "updated_at": datetime.utcnow().isoformat()}
        if status == "completed":
            patch["completed_at"] = datetime.utcnow().isoformat()

        res = supabase.table("roadmap_items")\
            .update(patch)\
            .eq("id", item_id)\
            .eq("tenant_id", tenant_id)\
            .execute()

        if not res.data:
            raise HTTPException(
                status_code=404,
                detail={"success": False, "error": {"code": "NOT_FOUND", "message": "Roadmap item not found"}}
            )

        return {"success": True, "data": {"item": res.data[0]}}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": {"code": "INTERNAL_ERROR", "message": f"Failed to update roadmap item: {str(e)}"}}
        )


# ============================================================
# VALUATION SHOCK REPORT API
# ============================================================

@app.post("/api/valuation/shock-report")
async def generate_shock_report(
    tenant_id: str = Depends(get_current_tenant_id),
    request_body: dict = Body(default={})
):
    """
    Generate a Valuation Shock Report showing the gap between
    owner expectations and buyer reality.

    This is the core conversion flow:
    1. Pulls QBO data
    2. Calculates reported vs defensible EBITDA
    3. Applies tier-based multiple penalties
    4. Shows the "shock" value gap
    5. Teases value unlocks (paid feature)

    Request body (optional):
        reported_revenue: Owner's stated revenue (defaults to QBO TTM)
        reported_ebitda: Owner's stated EBITDA (defaults to QBO calculated)
        expected_multiple: Owner's expected multiple (default: 5.0)
        owner_compensation: Owner's annual compensation (for add-back analysis)
        claimed_addbacks: List of claimed add-backs for analysis

    Returns:
        Complete shock report with gap analysis and recovery roadmap
    """
    import time
    from src.services.valuation.shock_report import ShockReportEngine

    try:
        start_time = time.time()

        # Parse optional overrides from request body
        overrides = {}
        if request_body.get("reported_revenue"):
            overrides["reported_revenue"] = float(request_body["reported_revenue"])
        if request_body.get("reported_ebitda"):
            overrides["reported_ebitda"] = float(request_body["reported_ebitda"])
        if request_body.get("expected_multiple"):
            overrides["expected_multiple"] = float(request_body["expected_multiple"])
        if request_body.get("owner_compensation"):
            overrides["owner_compensation"] = float(request_body["owner_compensation"])
        if request_body.get("claimed_addbacks"):
            overrides["claimed_addbacks"] = request_body["claimed_addbacks"]

        # Generate the shock report
        engine = ShockReportEngine()
        report = engine.generate_shock_report(tenant_id, **overrides)

        processing_time_ms = int((time.time() - start_time) * 1000)

        # Track analytics event
        try:
            supabase.table("shock_report_analytics").insert({
                "tenant_id": tenant_id,
                "shock_report_id": report.get("report_id"),
                "event_type": "report_generated"
            }).execute()
        except Exception:
            pass  # Don't fail on analytics

        return {
            "success": True,
            "data": {
                "report": report,
                "processing_time_ms": processing_time_ms
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": str(e)
                }
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"Failed to generate shock report: {str(e)}"
                }
            }
        )


@app.get("/api/valuation/shock-report/latest")
async def get_latest_shock_report(tenant_id: str = Depends(get_current_tenant_id)):
    """
    Get the most recent shock report for this tenant.

    Returns the full report with all adjustments, penalties, and value unlocks.
    """
    try:
        # Get latest shock report
        result = supabase.table("valuation_shock_reports")\
            .select("*")\
            .eq("tenant_id", tenant_id)\
            .order("generated_at", desc=True)\
            .limit(1)\
            .execute()

        if not result.data:
            return {
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "No shock report found. Generate one first."
                }
            }

        report = result.data[0]

        # Get related adjustments
        adjustments_result = supabase.table("ebitda_adjustments")\
            .select("*")\
            .eq("shock_report_id", report["id"])\
            .order("amount", desc=True)\
            .execute()

        # Get related penalties
        penalties_result = supabase.table("multiple_penalties")\
            .select("*")\
            .eq("shock_report_id", report["id"])\
            .order("penalty_amount")\
            .execute()

        # Get value unlocks
        unlocks_result = supabase.table("value_unlocks")\
            .select("*")\
            .eq("shock_report_id", report["id"])\
            .order("priority_rank")\
            .execute()

        # Track view event
        try:
            supabase.table("shock_report_analytics").insert({
                "tenant_id": tenant_id,
                "shock_report_id": report["id"],
                "event_type": "report_viewed"
            }).execute()
        except Exception:
            pass

        # Format response
        return {
            "success": True,
            "data": {
                "report": {
                    "id": report["id"],
                    "generated_at": report["generated_at"],

                    # Owner's view (the dream)
                    "owner_view": {
                        "revenue": float(report.get("reported_revenue") or 0),
                        "ebitda": float(report.get("reported_ebitda") or 0),
                        "owner_comp": float(report.get("reported_owner_comp") or 0),
                        "addbacks": float(report.get("reported_addbacks") or 0),
                        "expected_multiple": float(report.get("expected_multiple") or 5.0),
                        "expected_valuation": float(report.get("expected_valuation") or 0)
                    },

                    # Buyer's view (the reality)
                    "buyer_view": {
                        "defensible_ebitda": float(report.get("defensible_ebitda") or 0),
                        "defensible_sde": float(report.get("defensible_sde") or 0),
                        "multiple_low": float(report.get("buyer_multiple_low") or 2.5),
                        "multiple_high": float(report.get("buyer_multiple_high") or 3.5),
                        "valuation_low": float(report.get("buyer_valuation_low") or 0),
                        "valuation_high": float(report.get("buyer_valuation_high") or 0)
                    },

                    # The gap (the shock)
                    "gap_analysis": {
                        "ebitda_haircut": float(report.get("ebitda_haircut") or 0),
                        "multiple_penalty": float(report.get("multiple_penalty") or 0),
                        "value_gap": float(report.get("value_gap") or 0),
                        "value_gap_percentage": float(report.get("value_gap_percentage") or 0)
                    },

                    # Tier and confidence
                    "tier": report.get("tier") or "below_avg",
                    "confidence_score": report.get("confidence_score") or 0,

                    # Data quality
                    "data_quality": {
                        "qbo_data_range_start": report.get("qbo_data_range_start"),
                        "qbo_data_range_end": report.get("qbo_data_range_end"),
                        "transaction_count": report.get("transaction_count") or 0,
                        "invoice_count": report.get("invoice_count") or 0,
                        "expense_count": report.get("expense_count") or 0
                    },

                    # Recovery potential
                    "total_recoverable_value": float(report.get("total_recoverable_value") or 0)
                },

                # Detailed breakdowns
                "ebitda_adjustments": [
                    {
                        "id": adj["id"],
                        "type": adj["adjustment_type"],
                        "category": adj["category"],
                        "description": adj["description"],
                        "amount": float(adj["amount"]),
                        "accepted_amount": float(adj.get("accepted_amount") or 0),
                        "buyer_concern": adj.get("buyer_concern"),
                        "rejection_reason": adj.get("rejection_reason"),
                        "is_recoverable": adj.get("is_recoverable", True),
                        "remediation_action": adj.get("remediation_action"),
                        "remediation_effort": adj.get("remediation_effort"),
                        "remediation_impact": float(adj.get("remediation_impact") or 0)
                    }
                    for adj in (adjustments_result.data or [])
                ],

                "multiple_penalties": [
                    {
                        "id": pen["id"],
                        "driver_key": pen["driver_key"],
                        "penalty_amount": float(pen["penalty_amount"]),
                        "driver_score": pen.get("driver_score"),
                        "reason": pen["reason"],
                        "buyer_concern": pen.get("buyer_concern"),
                        "due_diligence_flag": pen.get("due_diligence_flag"),
                        "remediation_action": pen["remediation_action"],
                        "remediation_timeline": pen.get("remediation_timeline"),
                        "remediation_effort": pen.get("remediation_effort"),
                        "multiple_recovery": float(pen.get("multiple_recovery") or 0)
                    }
                    for pen in (penalties_result.data or [])
                ],

                "value_unlocks": [
                    {
                        "id": unlock["id"],
                        "priority_rank": unlock["priority_rank"],
                        "title": unlock["title"],
                        "description": unlock.get("description"),
                        "action_type": unlock["action_type"],
                        "ebitda_impact": float(unlock.get("ebitda_impact") or 0),
                        "multiple_impact": float(unlock.get("multiple_impact") or 0),
                        "ev_impact": float(unlock["ev_impact"]),
                        "effort_level": unlock.get("effort_level"),
                        "timeline": unlock.get("timeline"),
                        "is_locked": unlock.get("is_locked", True),
                        "is_preview": unlock.get("is_preview", False)
                    }
                    for unlock in (unlocks_result.data or [])
                ]
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"Failed to retrieve shock report: {str(e)}"
                }
            }
        )


@app.get("/api/valuation/shock-report/pdf")
async def generate_shock_report_pdf(
    tenant_id: str = Depends(get_current_tenant_id)
):
    """
    Generate a PDF version of the latest shock report.

    Returns the PDF file as a downloadable response.
    """
    from fastapi.responses import Response
    from src.services.valuation.pdf_generator import generate_shock_report_pdf as gen_pdf
    from src.services.valuation.shock_report import ShockReportEngine

    try:
        # Get tenant info for company name
        tenant_result = supabase.table("tenants")\
            .select("name")\
            .eq("id", tenant_id)\
            .limit(1)\
            .execute()

        company_name = tenant_result.data[0]["name"] if tenant_result.data else "Your Company"

        # Generate fresh shock report
        engine = ShockReportEngine()
        report = engine.generate_shock_report(tenant_id)

        # Generate PDF
        pdf_bytes = gen_pdf(report, company_name)

        # Return PDF as downloadable file
        filename = f"shock_report_{datetime.now().strftime('%Y%m%d')}.pdf"

        # Track PDF download analytics
        try:
            supabase.table("shock_report_analytics").insert({
                "tenant_id": tenant_id,
                "event_type": "pdf_downloaded"
            }).execute()
        except Exception:
            pass

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "PDF_GENERATION_ERROR",
                    "message": f"Failed to generate PDF: {str(e)}"
                }
            }
        )


@app.post("/api/valuation/shock-report/{report_id}/analytics")
async def track_shock_report_analytics(
    report_id: str,
    tenant_id: str = Depends(get_current_tenant_id),
    request_body: dict = Body(...)
):
    """
    Track analytics events for shock report engagement.

    Request body:
        event_type: One of:
            - 'section_expanded' (section_name required)
            - 'pdf_downloaded'
            - 'share_clicked'
            - 'trial_cta_clicked'
            - 'trial_started'
            - 'paid_converted'
        section_name: Optional section identifier
        time_on_page: Optional seconds spent on page
        scroll_depth: Optional percentage scrolled
    """
    try:
        event_type = request_body.get("event_type")
        valid_events = [
            "report_viewed", "section_expanded", "pdf_downloaded",
            "share_clicked", "trial_cta_clicked", "trial_started", "paid_converted"
        ]

        if event_type not in valid_events:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": f"Invalid event_type. Must be one of: {', '.join(valid_events)}"
                    }
                }
            )

        # Verify report belongs to tenant
        report_check = supabase.table("valuation_shock_reports")\
            .select("id")\
            .eq("id", report_id)\
            .eq("tenant_id", tenant_id)\
            .limit(1)\
            .execute()

        if not report_check.data:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Shock report not found"
                    }
                }
            )

        # Insert analytics event
        supabase.table("shock_report_analytics").insert({
            "tenant_id": tenant_id,
            "shock_report_id": report_id,
            "event_type": event_type,
            "section_name": request_body.get("section_name"),
            "time_on_page": request_body.get("time_on_page"),
            "scroll_depth": request_body.get("scroll_depth")
        }).execute()

        # Update report flags based on event
        if event_type == "pdf_downloaded":
            supabase.table("valuation_shock_reports")\
                .update({"pdf_downloaded": True})\
                .eq("id", report_id)\
                .execute()
        elif event_type == "trial_started":
            supabase.table("valuation_shock_reports")\
                .update({"trial_started": True})\
                .eq("id", report_id)\
                .execute()

        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"Failed to track analytics: {str(e)}"
                }
            }
        )


@app.get("/api/valuation/shock-reports")
async def list_shock_reports(
    tenant_id: str = Depends(get_current_tenant_id),
    limit: int = 10,
    page: int = 1
):
    """
    List all shock reports for this tenant with pagination.
    """
    try:
        limit = min(limit, 50)
        offset = (page - 1) * limit

        result = supabase.table("valuation_shock_reports")\
            .select("id, generated_at, tier, value_gap, value_gap_percentage, confidence_score, total_recoverable_value")\
            .eq("tenant_id", tenant_id)\
            .order("generated_at", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()

        # Get total count
        count_result = supabase.table("valuation_shock_reports")\
            .select("id", count="exact")\
            .eq("tenant_id", tenant_id)\
            .execute()

        total = count_result.count if hasattr(count_result, 'count') else len(result.data)
        total_pages = (total + limit - 1) // limit if total > 0 else 1

        reports = []
        for r in (result.data or []):
            reports.append({
                "id": r["id"],
                "generated_at": r["generated_at"],
                "tier": r.get("tier"),
                "value_gap": float(r.get("value_gap") or 0),
                "value_gap_percentage": float(r.get("value_gap_percentage") or 0),
                "confidence_score": r.get("confidence_score"),
                "total_recoverable_value": float(r.get("total_recoverable_value") or 0)
            })

        return {
            "success": True,
            "data": {
                "reports": reports,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "pages": total_pages
                }
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"Failed to list shock reports: {str(e)}"
                }
            }
        )


# ============================================================
# CONTACT / SUPPORT
# ============================================================

@app.post("/api/contact")
async def send_contact_message(
    subject: str = Body(...),
    message: str = Body(...),
    from_email: str = Body(...)
):
    """Send a support contact message via Resend"""
    resend_api_key = os.getenv("RESEND_API_KEY")
    from_address = os.getenv("FROM_EMAIL", "noreply@crewcfo.com")

    if not resend_api_key:
        raise HTTPException(
            status_code=500,
            detail="Email service not configured"
        )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {resend_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "from": from_address,
                    "to": ["support@crewcfo.com"],
                    "subject": f"[CrewCFO Support] {subject}",
                    "html": f"""
                        <h2>New Support Request</h2>
                        <p><strong>From:</strong> {from_email}</p>
                        <p><strong>Subject:</strong> {subject}</p>
                        <hr>
                        <p>{message.replace(chr(10), '<br>')}</p>
                    """,
                    "reply_to": from_email
                }
            )

            if response.status_code not in [200, 201]:
                error_detail = response.json() if response.content else {}
                logger.error(f"Resend API error: {response.status_code} - {error_detail}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to send email: {error_detail.get('message', 'Unknown error')}"
                )

            result = response.json()
            logger.info(f"Support email sent successfully: {result.get('id')}")
            return {
                "success": True,
                "message": "Your message has been sent. We'll get back to you soon!",
                "email_id": result.get("id")
            }
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to connect to email service: {str(e)}"
        )


# ============================================================
# DEMO MODE ENDPOINTS
# ============================================================
# These endpoints provide realistic demo data for showcasing
# all dashboard features without requiring QuickBooks connection.
# Demo Company: Apex Roofing Solutions ($3.5M revenue)
# ============================================================

DEMO_TENANT_ID = "demo-0000-0000-0000-000000000001"


@app.get("/api/demo/dashboard")
async def get_demo_dashboard():
    """
    Demo dashboard data for Apex Roofing Solutions.
    Shows overview metrics, trends, and KPIs.
    """
    from datetime import datetime, timedelta

    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    # $3.5M annual revenue with seasonal patterns
    monthly_data = []
    base_revenue = 291667
    seasonal_pattern = [0.70, 0.75, 0.95, 1.15, 1.25, 1.20, 1.10, 1.05, 1.10, 1.05, 0.85, 0.85]

    for i in range(12):
        month_date = start_date + timedelta(days=30 * i)
        revenue = base_revenue * seasonal_pattern[i]
        expenses = revenue * 0.78  # 22% gross margin (problematic)
        profit = revenue - expenses

        monthly_data.append({
            "month": month_date.strftime("%Y-%m"),
            "revenue": round(revenue),
            "expenses": round(expenses),
            "profit": round(profit),
            "gross_margin": 0.22,
            "job_count": int(revenue / 18000)  # ~$18K avg job
        })

    return {
        "success": True,
        "data": {
            "company": {
                "name": "Apex Roofing Solutions",
                "industry": "Roofing Contractor",
                "location": "Dallas, TX",
                "employees": 12,
                "years_in_business": 8
            },
            "summary": {
                "ttm_revenue": 3500000,
                "ttm_expenses": 2730000,
                "ttm_profit": 245000,
                "gross_margin": 0.22,
                "net_margin": 0.07,
                "job_count": 195,
                "avg_job_size": 17949
            },
            "kpis": {
                "days_receivable": 47,
                "days_payable": 28,
                "current_ratio": 1.3,
                "quick_ratio": 0.9
            },
            "monthly_data": monthly_data,
            "alerts": [
                {"type": "warning", "message": "Gross margin 22% below industry average (28-35%)"},
                {"type": "warning", "message": "AR days at 47 - target is <35 days"},
                {"type": "info", "message": "Revenue up 8% vs prior year"}
            ]
        },
        "demo": True
    }


@app.get("/api/demo/finance")
async def get_demo_finance():
    """
    Demo finance dashboard with P&L, cash flow, AR/AP aging.
    """
    from datetime import datetime, timedelta

    return {
        "success": True,
        "data": {
            "income_statement": {
                "period": "TTM",
                "revenue": {
                    "roofing_services": 2450000,
                    "commercial_roofing": 875000,
                    "repairs_maintenance": 175000,
                    "total": 3500000
                },
                "cost_of_goods_sold": {
                    "materials": 1225000,  # 35% - high
                    "direct_labor": 630000,  # 18%
                    "subcontractors": 280000,  # 8%
                    "equipment": 70000,  # 2%
                    "disposal": 70000,  # 2%
                    "total": 2275000  # 65% COGS
                },
                "gross_profit": 1225000,
                "gross_margin": 0.35,
                "operating_expenses": {
                    "payroll_admin": 225000,  # Includes owner + spouse overpay
                    "insurance": 122500,
                    "rent": 70000,
                    "marketing": 70000,
                    "vehicles": 87500,  # Includes personal BMW
                    "professional_fees": 35000,
                    "office_software": 52500,
                    "utilities": 28000,
                    "entertainment": 12000,  # Country club
                    "depreciation": 42000,
                    "other": 35000,
                    "total": 779500
                },
                "operating_income": 445500,
                "other_expenses": 200500,
                "net_income": 245000,
                "net_margin": 0.07
            },
            "cash_flow": {
                "starting_cash": 125000,
                "operating_cash_flow": 285000,
                "investing_cash_flow": -45000,
                "financing_cash_flow": -180000,
                "ending_cash": 185000,
                "runway_weeks": 14
            },
            "ar_aging": {
                "current": 185000,
                "1_30_days": 95000,
                "31_60_days": 45000,
                "61_90_days": 28000,
                "over_90_days": 12000,
                "total": 365000,
                "days_outstanding": 47
            },
            "ap_aging": {
                "current": 78000,
                "1_30_days": 42000,
                "31_60_days": 15000,
                "over_60_days": 5000,
                "total": 140000,
                "days_outstanding": 28
            },
            "job_profitability": [
                {"job": "Smith Residence - Full Replacement", "revenue": 24500, "cost": 17150, "margin": 0.30},
                {"job": "Riverside PM - Bldg A", "revenue": 67000, "cost": 46900, "margin": 0.30},
                {"job": "Johnson Residence - Repair", "revenue": 4200, "cost": 3570, "margin": 0.15},
                {"job": "Summit Builders - Phase 2", "revenue": 145000, "cost": 116000, "margin": 0.20},
                {"job": "Garcia Residence - Storm", "revenue": 18500, "cost": 12950, "margin": 0.30}
            ]
        },
        "demo": True
    }


@app.get("/api/demo/shock-report")
async def get_demo_shock_report():
    """
    Demo valuation shock report showing expected vs actual valuation gap.
    This is the core conversion tool.
    """
    return {
        "success": True,
        "data": {
            "company": "Apex Roofing Solutions",
            "generated_at": datetime.now().isoformat(),

            # What owner expects
            "owner_view": {
                "revenue": 3500000,
                "ebitda": 350000,
                "expected_multiple": 10.0,
                "expected_valuation": 3500000,
                "addbacks_claimed": {
                    "owner_salary": 180000,
                    "spouse_salary": 45000,
                    "personal_vehicle": 18000,
                    "entertainment": 12000,
                    "one_time_legal": 25000,
                    "total": 280000
                }
            },

            # What buyer sees
            "buyer_view": {
                "defensible_ebitda": 245000,
                "defensible_sde": 395000,
                "multiple_low": 3.0,
                "multiple_high": 4.0,
                "valuation_low": 735000,
                "valuation_high": 980000,
                "accepted_addbacks": {
                    "owner_salary_portion": 60000,
                    "spouse_salary_portion": 15000,
                    "personal_vehicle": 0,
                    "entertainment": 0,
                    "one_time_legal": 25000,
                    "total": 100000
                },
                "rejected_addbacks": {
                    "owner_salary_excess": 60000,
                    "spouse_salary_excess": 30000,
                    "personal_vehicle": 18000,
                    "entertainment": 12000,
                    "total": 120000
                }
            },

            # The shock
            "gap": {
                "ebitda_haircut": 105000,
                "multiple_penalty": 6.5,
                "value_gap": 2520000,
                "value_gap_percentage": 72
            },

            # Multiple penalties explained
            "multiple_penalties": [
                {
                    "driver": "management_independence",
                    "score": 25,
                    "penalty": -1.5,
                    "reason": "Owner IS the business",
                    "buyer_concern": "Key person risk - owner handles all sales and estimates",
                    "fix": "Hire operations manager; document all processes"
                },
                {
                    "driver": "recurring_revenue",
                    "score": 15,
                    "penalty": -1.0,
                    "reason": "Zero recurring revenue",
                    "buyer_concern": "100% project-based, unpredictable cash flow",
                    "fix": "Launch maintenance contract program"
                },
                {
                    "driver": "financial_records",
                    "score": 55,
                    "penalty": -0.5,
                    "reason": "Messy books",
                    "buyer_concern": "Personal expenses mixed, delayed monthly close",
                    "fix": "Clean up chart of accounts; 5-day close process"
                },
                {
                    "driver": "customer_diversity",
                    "score": 45,
                    "penalty": -0.5,
                    "reason": "Customer concentration",
                    "buyer_concern": "Top 3 customers = 42% of revenue",
                    "fix": "Diversify customer base; no customer >15%"
                }
            ],

            # Value unlocks
            "value_unlocks": [
                {"priority": 1, "title": "Hire Operations Manager", "ev_impact": 350000, "effort": "high", "timeline": "6-12 months"},
                {"priority": 2, "title": "Launch Maintenance Contracts", "ev_impact": 280000, "effort": "medium", "timeline": "3-6 months"},
                {"priority": 3, "title": "Clean Up Personal Expenses", "ev_impact": 175000, "effort": "low", "timeline": "1-3 months"},
                {"priority": 4, "title": "Diversify Customer Base", "ev_impact": 150000, "effort": "high", "timeline": "12+ months"},
                {"priority": 5, "title": "Document All SOPs", "ev_impact": 125000, "effort": "medium", "timeline": "3-6 months"}
            ],

            "total_recoverable_value": 1080000,
            "tier": "below_avg",
            "confidence_score": 78
        },
        "demo": True
    }


@app.get("/api/demo/simulator")
async def get_demo_simulator():
    """
    Demo scenario simulator showing what-if analysis.
    """
    return {
        "success": True,
        "data": {
            "current_state": {
                "revenue": 3500000,
                "ebitda": 245000,
                "multiple": 3.5,
                "valuation": 857500,
                "gross_margin": 0.22,
                "recurring_revenue_pct": 0,
                "owner_dependency_score": 25
            },
            "scenarios": [
                {
                    "name": "Price Increase 5%",
                    "changes": {"revenue": 3675000, "ebitda": 332500, "gross_margin": 0.26},
                    "impact": {"ebitda_delta": 87500, "valuation_delta": 306250},
                    "effort": "low",
                    "timeline": "Immediate"
                },
                {
                    "name": "Launch Maintenance Program",
                    "changes": {"recurring_revenue_pct": 0.08, "revenue": 3570000},
                    "impact": {"multiple_delta": 0.75, "valuation_delta": 280000},
                    "effort": "medium",
                    "timeline": "6-12 months"
                },
                {
                    "name": "Hire Ops Manager",
                    "changes": {"owner_dependency_score": 65, "ebitda": 215000},
                    "impact": {"multiple_delta": 1.0, "valuation_delta": 285000},
                    "effort": "high",
                    "timeline": "6-12 months"
                },
                {
                    "name": "Clean Up Expenses",
                    "changes": {"ebitda": 305000},
                    "impact": {"ebitda_delta": 60000, "valuation_delta": 210000},
                    "effort": "low",
                    "timeline": "1-3 months"
                },
                {
                    "name": "Full Value Optimization",
                    "changes": {
                        "revenue": 3850000,
                        "ebitda": 462000,
                        "gross_margin": 0.30,
                        "recurring_revenue_pct": 0.12,
                        "owner_dependency_score": 70
                    },
                    "impact": {
                        "multiple_delta": 2.5,
                        "valuation_delta": 1925000,
                        "new_valuation": 2772000
                    },
                    "effort": "high",
                    "timeline": "18-24 months"
                }
            ],
            "industry_benchmarks": {
                "gross_margin": {"industry_avg": 0.28, "top_quartile": 0.35},
                "net_margin": {"industry_avg": 0.10, "top_quartile": 0.15},
                "recurring_revenue": {"industry_avg": 0.05, "top_quartile": 0.15},
                "ebitda_multiple": {"industry_avg": 4.5, "top_quartile": 6.5}
            }
        },
        "demo": True
    }


@app.get("/api/demo/exit-readiness")
async def get_demo_exit_readiness():
    """
    Demo exit readiness checklist and CIM preparation status.
    """
    return {
        "success": True,
        "data": {
            "readiness_score": 45,
            "status": "In Progress",
            "checklist": [
                {"key": "financial_statements", "label": "Financial Statements", "status": "complete", "docs": 3},
                {"key": "tax_returns", "label": "Tax Returns", "status": "complete", "docs": 3},
                {"key": "ar_ap_aging", "label": "AR/AP Aging Reports", "status": "complete", "docs": 2},
                {"key": "asset_list", "label": "Asset List", "status": "partial", "docs": 1},
                {"key": "org_chart", "label": "Organization Chart", "status": "missing", "docs": 0},
                {"key": "kpi_dashboard", "label": "KPI Dashboard", "status": "missing", "docs": 0},
                {"key": "safety_insurance", "label": "Safety & Insurance", "status": "partial", "docs": 2}
            ],
            "deal_room_items": {
                "uploaded": 11,
                "total_required": 20,
                "missing_critical": ["org_chart", "kpi_dashboard", "customer_contracts"]
            },
            "buyer_attractiveness": {
                "score": 45,
                "strengths": [
                    "Strong Texas market presence",
                    "8 years operating history",
                    "Clean safety record"
                ],
                "weaknesses": [
                    "High owner dependency",
                    "No recurring revenue",
                    "Customer concentration risk"
                ],
                "pe_interest_level": "Low-Medium",
                "likely_buyer_type": "Strategic acquirer or local competitor"
            },
            "timeline_to_ready": {
                "current_state": "Not ready for market",
                "estimated_prep_time": "12-18 months",
                "key_milestones": [
                    {"milestone": "Clean financial records", "target": "3 months"},
                    {"milestone": "Hire operations manager", "target": "6 months"},
                    {"milestone": "Launch maintenance program", "target": "9 months"},
                    {"milestone": "Complete CIM", "target": "12 months"}
                ]
            }
        },
        "demo": True
    }


@app.get("/api/demo/roadmap")
async def get_demo_roadmap():
    """
    Demo strategic roadmap with prioritized action items.
    """
    return {
        "success": True,
        "data": {
            "total_ev_opportunity": 1080000,
            "items_count": 9,
            "items_by_priority": {
                "critical": 2,
                "high": 4,
                "medium": 3
            },
            "items": [
                {
                    "id": "1",
                    "title": "Hire Operations Manager",
                    "description": "Recruit and onboard an operations manager to handle day-to-day decisions",
                    "driver": "management_independence",
                    "category": "strategic",
                    "priority": "critical",
                    "status": "pending",
                    "ev_impact": 350000,
                    "effort": "high",
                    "timeline": "6-12 months",
                    "due_date": "2025-06-30"
                },
                {
                    "id": "2",
                    "title": "Launch Maintenance Contract Program",
                    "description": "Create annual roof maintenance contracts ($350-500/year residential)",
                    "driver": "recurring_revenue",
                    "category": "strategic",
                    "priority": "critical",
                    "status": "pending",
                    "ev_impact": 280000,
                    "effort": "medium",
                    "timeline": "3-6 months",
                    "due_date": "2025-04-30"
                },
                {
                    "id": "3",
                    "title": "Clean Up Personal Expenses",
                    "description": "Remove all personal expenses from P&L and transfer to owner distributions",
                    "driver": "financial_records",
                    "category": "monthly_close",
                    "priority": "high",
                    "status": "in_progress",
                    "ev_impact": 175000,
                    "effort": "low",
                    "timeline": "1-3 months",
                    "due_date": "2025-02-28"
                },
                {
                    "id": "4",
                    "title": "Document All SOPs",
                    "description": "Create written Standard Operating Procedures for all key processes",
                    "driver": "management_independence",
                    "category": "strategic",
                    "priority": "high",
                    "status": "in_progress",
                    "ev_impact": 125000,
                    "effort": "medium",
                    "timeline": "3-6 months",
                    "due_date": "2025-03-31"
                },
                {
                    "id": "5",
                    "title": "Reduce Builder Concentration",
                    "description": "Target: No single customer >15% of revenue",
                    "driver": "customer_diversity",
                    "category": "quarterly_review",
                    "priority": "high",
                    "status": "in_progress",
                    "ev_impact": 150000,
                    "effort": "high",
                    "timeline": "12+ months",
                    "due_date": "2025-12-31"
                },
                {
                    "id": "6",
                    "title": "Implement 5-Day Close Process",
                    "description": "Close books within 5 business days of month-end",
                    "driver": "financial_records",
                    "category": "monthly_close",
                    "priority": "high",
                    "status": "pending",
                    "ev_impact": 50000,
                    "effort": "medium",
                    "timeline": "1-3 months",
                    "due_date": "2025-02-28"
                },
                {
                    "id": "7",
                    "title": "Implement Job Costing System",
                    "description": "Track actual vs. estimated costs per job with QuickBooks integration",
                    "driver": "operational_systems",
                    "category": "strategic",
                    "priority": "medium",
                    "status": "pending",
                    "ev_impact": 75000,
                    "effort": "medium",
                    "timeline": "3-6 months",
                    "due_date": "2025-04-30"
                },
                {
                    "id": "8",
                    "title": "Implement Extended Warranty Program",
                    "description": "Offer 10-year extended labor warranty for premium pricing",
                    "driver": "recurring_revenue",
                    "category": "strategic",
                    "priority": "medium",
                    "status": "pending",
                    "ev_impact": 85000,
                    "effort": "low",
                    "timeline": "1-3 months",
                    "due_date": "2025-03-31"
                },
                {
                    "id": "9",
                    "title": "Digitize Safety Checklists",
                    "description": "Replace paper safety checklists with digital forms",
                    "driver": "operational_systems",
                    "category": "compliance",
                    "priority": "medium",
                    "status": "pending",
                    "ev_impact": 25000,
                    "effort": "low",
                    "timeline": "1 month",
                    "due_date": "2025-02-15"
                }
            ],
            "progress": {
                "completed": 0,
                "in_progress": 3,
                "pending": 6,
                "ev_realized": 0,
                "ev_in_progress": 450000
            }
        },
        "demo": True
    }


@app.get("/api/demo/profit-leaks")
async def get_demo_profit_leaks():
    """
    Demo profit leaks with specific fix recommendations and $ impact.
    Based on industry research: avg margin 25-35%, net 6-12%.
    Demo company has 22% gross margin (problematic) and 7% net margin.
    """
    return {
        "success": True,
        "data": {
            "company": "Apex Roofing Solutions",
            "period": "TTM",
            "summary": {
                "total_leaks_identified": 5,
                "total_annual_impact": 165000,
                "current_gross_margin": 0.22,
                "target_gross_margin": 0.30,
                "current_net_margin": 0.07,
                "target_net_margin": 0.12
            },
            "leaks": [
                {
                    "id": 1,
                    "title": "Owner Compensation Above Market",
                    "category": "Personal Expenses",
                    "annual_impact": 60000,
                    "description": "Owner salary of $180K exceeds market rate for GM role ($120K)",
                    "evidence": [
                        "BLS data shows GM median salary $110-130K in Texas",
                        "Excess $60K reduces defensible EBITDA"
                    ],
                    "fix": "Document market-rate salary; treat excess as owner distribution",
                    "effort": "low",
                    "priority": "high"
                },
                {
                    "id": 2,
                    "title": "Related Party Salary",
                    "category": "Personal Expenses",
                    "annual_impact": 30000,
                    "description": "Spouse on payroll at $45K with unclear job duties",
                    "evidence": [
                        "No job description on file",
                        "Part-time admin work valued at $15K market rate"
                    ],
                    "fix": "Document job duties or adjust to market rate; $30K excess to distribution",
                    "effort": "low",
                    "priority": "high"
                },
                {
                    "id": 3,
                    "title": "Personal Vehicle Expense",
                    "category": "Personal Expenses",
                    "annual_impact": 18000,
                    "description": "Personal BMW X5 fully expensed through company",
                    "evidence": [
                        "No mileage log for business use",
                        "Vehicle used primarily for personal transportation"
                    ],
                    "fix": "Remove from business expenses; pay personally or implement mileage log",
                    "effort": "low",
                    "priority": "medium"
                },
                {
                    "id": 4,
                    "title": "Entertainment/Country Club",
                    "category": "Discretionary",
                    "annual_impact": 12000,
                    "description": "Country club membership with no documented business purpose",
                    "evidence": [
                        "No client entertainment log",
                        "Appears to be personal lifestyle expense"
                    ],
                    "fix": "Remove from business expenses",
                    "effort": "low",
                    "priority": "medium"
                },
                {
                    "id": 5,
                    "title": "Underpricing Jobs",
                    "category": "Pricing",
                    "annual_impact": 45000,
                    "description": "Gross margin 22% vs industry target 28-30%",
                    "evidence": [
                        "Material costs 35% of revenue vs 30% benchmark",
                        "Labor at 18% vs 15% benchmark",
                        "5% price increase would add $175K revenue"
                    ],
                    "fix": "Implement 5% price increase; review material supplier contracts",
                    "effort": "medium",
                    "priority": "high"
                }
            ],
            "industry_benchmarks": {
                "gross_margin": {"you": 0.22, "avg": 0.28, "top": 0.35},
                "net_margin": {"you": 0.07, "avg": 0.10, "top": 0.15},
                "materials_pct": {"you": 0.35, "avg": 0.30, "target": 0.28},
                "labor_pct": {"you": 0.18, "avg": 0.15, "target": 0.14},
                "overhead_pct": {"you": 0.25, "avg": 0.22, "target": 0.20}
            },
            "fix_priority_order": [
                "1. Clean personal expenses (Quick win: $120K impact, low effort)",
                "2. Price increase 5% (Medium effort: $175K revenue impact)",
                "3. Review material supplier contracts (Medium effort: reduce COGS)",
                "4. Implement labor tracking (High effort: improve crew efficiency)"
            ]
        },
        "demo": True
    }


# ============================================================
# P&L ANALYTICS ENDPOINTS (Real QuickBooks Data)
# ============================================================

from src.services.finance.pnl_analytics import PnLAnalyticsService, analyze_quickbooks_pnl


@app.get("/api/analytics/pnl")
async def get_pnl_analytics(
    tenant_id: str = Depends(get_current_tenant_id),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    accounting_method: Optional[str] = "Accrual"
):
    """
    Get P&L analytics with break-even, EBITDA/SDE, and profit leak detection.

    Uses real QuickBooks data when connected, falls back to demo data otherwise.
    """
    try:
        # Check if tenant has active QBO connection
        integration = supabase.table("tenant_integrations")\
            .select("id, is_active")\
            .eq("tenant_id", tenant_id)\
            .eq("provider", "quickbooks")\
            .eq("is_active", True)\
            .execute()

        if integration.data:
            # Use QBO client to get real P&L
            from src.services.qbo.client import QBOClient
            qbo = QBOClient(tenant_id)

            # Get overhead analysis which includes P&L data
            overhead_data = qbo.get_overhead_analysis(start_date, end_date)

            # Transform QBO data to P&L format
            pnl_service = PnLAnalyticsService()

            # Use ACTUAL P&L data from QBO Report - NEVER fabricate
            actual_pnl = overhead_data.get("actual_pnl", {})

            # Get values - use actual P&L data from QBO
            revenue = actual_pnl.get("income")
            cogs = actual_pnl.get("cogs")
            gross_profit = actual_pnl.get("gross_profit")
            expenses = actual_pnl.get("expenses")
            net_income = actual_pnl.get("net_income")

            # Build report structure with ACTUAL data - 0 if None for calculations
            report_data = {
                "start_date": overhead_data["period"]["start"],
                "end_date": overhead_data["period"]["end"],
                "summary": {
                    "total_income": revenue if revenue is not None else 0,
                    "total_cogs": cogs if cogs is not None else 0,
                    "gross_profit": gross_profit if gross_profit is not None else 0,
                    "total_expenses": expenses if expenses is not None else 0,
                    "net_income": net_income if net_income is not None else 0
                },
                "metrics": {},
                # Include actual P&L breakdown from QBO
                "actual_data": actual_pnl
            }

            # Add overhead items as metrics
            for category, amount in overhead_data["overhead"]["by_category"].items():
                report_data["metrics"][f"Expenses.{category}"] = amount

            for category, amount in overhead_data["job_costs"]["by_category"].items():
                report_data["metrics"][f"Cost of Goods Sold.{category}"] = amount

            analytics = pnl_service.analyze_pnl(report_data)

            return {
                "success": True,
                "data": analytics,
                "source": "quickbooks",
                "tenant_id": tenant_id
            }

        else:
            # Return demo data if not connected
            return await get_demo_pnl_analytics()

    except Exception as e:
        # Fallback to demo on error
        print(f"P&L Analytics error: {e}")
        return await get_demo_pnl_analytics()


@app.get("/api/analytics/pnl/demo")
async def get_demo_pnl_analytics():
    """
    Demo P&L analytics for Apex Roofing Solutions.
    """
    pnl_service = PnLAnalyticsService()

    # Demo data matching Apex Roofing profile
    demo_report = {
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "summary": {
            "total_income": 3500000,
            "total_cogs": 2275000,
            "gross_profit": 1225000,
            "total_expenses": 779500,
            "net_income": 245000
        },
        "metrics": {
            "Income.Roofing Services": 2450000,
            "Income.Commercial": 875000,
            "Income.Repairs": 175000,
            "Cost of Goods Sold.Materials": 1225000,
            "Cost of Goods Sold.Direct Labor": 630000,
            "Cost of Goods Sold.Subcontractors": 280000,
            "Cost of Goods Sold.Equipment": 70000,
            "Cost of Goods Sold.Disposal": 70000,
            "Expenses.Payroll Admin": 225000,
            "Expenses.Insurance": 122500,
            "Expenses.Rent": 70000,
            "Expenses.Marketing": 70000,
            "Expenses.Vehicles": 87500,
            "Expenses.Professional Fees": 35000,
            "Expenses.Office Software": 52500,
            "Expenses.Utilities": 28000,
            "Expenses.Entertainment": 12000,
            "Expenses.Depreciation": 42000,
            "Expenses.Other": 35000,
            "Expenses.Interest": 0
        }
    }

    analytics = pnl_service.analyze_pnl(demo_report)

    # Add EBITDA/SDE with owner addbacks
    ebitda_sde = pnl_service.calculate_ebitda_sde(
        net_income=245000,
        interest=0,
        depreciation=42000,
        owner_compensation=180000,  # Owner salary to add back
        owner_benefits=25000,  # Health insurance, etc
        non_recurring=25000  # One-time legal fees
    )

    analytics["ebitda_sde"] = ebitda_sde

    return {
        "success": True,
        "data": analytics,
        "source": "demo",
        "company": "Apex Roofing Solutions"
    }


@app.get("/api/analytics/break-even")
async def get_break_even_analysis(
    tenant_id: str = Depends(get_current_tenant_id)
):
    """
    Get break-even analysis with scenario modeling.
    """
    try:
        integration = supabase.table("tenant_integrations")\
            .select("id, is_active")\
            .eq("tenant_id", tenant_id)\
            .eq("provider", "quickbooks")\
            .eq("is_active", True)\
            .execute()

        if integration.data:
            from src.services.qbo.client import QBOClient
            qbo = QBOClient(tenant_id)

            overhead_data = qbo.get_overhead_analysis()

            return {
                "success": True,
                "data": {
                    "overhead": overhead_data["overhead"],
                    "gross_margin": overhead_data["profitability"],
                    "break_even": overhead_data["break_even"]
                },
                "source": "quickbooks"
            }

        else:
            # Demo break-even
            pnl_service = PnLAnalyticsService()
            break_even = pnl_service.calculate_break_even(
                total_overhead=779500,  # Annual overhead
                gross_margin_pct=0.35  # 35% gross margin
            )

            return {
                "success": True,
                "data": {
                    "overhead": {
                        "total": 779500,
                        "monthly_average": 64958
                    },
                    "gross_margin": {
                        "current": 0.35,
                        "target": 0.35
                    },
                    "break_even": break_even
                },
                "source": "demo"
            }

    except Exception as e:
        raise HTTPException(500, f"Break-even analysis failed: {str(e)}")


@app.get("/api/analytics/valuation")
async def get_valuation_metrics(
    tenant_id: str = Depends(get_current_tenant_id),
    owner_compensation: float = 0,
    owner_benefits: float = 0,
    non_recurring: float = 0
):
    """
    Get EBITDA/SDE valuation metrics with add-back adjustments.
    """
    try:
        integration = supabase.table("tenant_integrations")\
            .select("id, is_active")\
            .eq("tenant_id", tenant_id)\
            .eq("provider", "quickbooks")\
            .eq("is_active", True)\
            .execute()

        pnl_service = PnLAnalyticsService()

        if integration.data:
            from src.services.qbo.client import QBOClient
            qbo = QBOClient(tenant_id)

            overhead_data = qbo.get_overhead_analysis()
            net_income = overhead_data["revenue"]["total"] - \
                         overhead_data["job_costs"]["total"] - \
                         overhead_data["overhead"]["total"]

            # Get interest/depreciation from expense breakdown
            interest = 0
            depreciation = 0
            for category, amount in overhead_data["overhead"]["by_category"].items():
                if "interest" in category.lower():
                    interest += amount
                if "depreciation" in category.lower() or "amortization" in category.lower():
                    depreciation += amount

            valuation = pnl_service.calculate_ebitda_sde(
                net_income=net_income,
                interest=interest,
                depreciation=depreciation,
                owner_compensation=owner_compensation,
                owner_benefits=owner_benefits,
                non_recurring=non_recurring
            )

            return {
                "success": True,
                "data": {
                    "net_income": net_income,
                    **valuation
                },
                "source": "quickbooks"
            }

        else:
            # Demo valuation
            valuation = pnl_service.calculate_ebitda_sde(
                net_income=245000,
                interest=0,
                depreciation=42000,
                owner_compensation=owner_compensation or 180000,
                owner_benefits=owner_benefits or 25000,
                non_recurring=non_recurring or 25000
            )

            return {
                "success": True,
                "data": {
                    "net_income": 245000,
                    **valuation
                },
                "source": "demo"
            }

    except Exception as e:
        raise HTTPException(500, f"Valuation calculation failed: {str(e)}")


@app.get("/api/analytics/profit-leaks")
async def get_profit_leaks(
    tenant_id: str = Depends(get_current_tenant_id)
):
    """
    Detect profit leaks by analyzing expense ratios vs industry benchmarks.
    """
    try:
        integration = supabase.table("tenant_integrations")\
            .select("id, is_active")\
            .eq("tenant_id", tenant_id)\
            .eq("provider", "quickbooks")\
            .eq("is_active", True)\
            .execute()

        pnl_service = PnLAnalyticsService()

        if integration.data:
            from src.services.qbo.client import QBOClient
            qbo = QBOClient(tenant_id)

            overhead_data = qbo.get_overhead_analysis()
            revenue = overhead_data["revenue"]["total"]

            pnl_data = {
                "overhead_items": overhead_data["overhead"]["by_category"],
                "cogs_items": overhead_data["job_costs"]["by_category"]
            }

            profit_leaks = pnl_service.detect_profit_leaks(pnl_data, revenue)

            return {
                "success": True,
                "data": {
                    "profit_leaks": profit_leaks,
                    "total_potential_savings": sum(
                        leak.get("potential_savings", 0)
                        for leak in profit_leaks
                        if leak.get("potential_savings")
                    ),
                    "leak_count": len(profit_leaks)
                },
                "source": "quickbooks"
            }

        else:
            # Demo profit leaks
            demo_pnl = {
                "overhead_items": {
                    "Payroll Admin": 225000,
                    "Marketing": 70000,
                    "Telephone": 49000,  # High
                    "Vehicles": 87500,
                    "Entertainment": 12000
                }
            }

            profit_leaks = pnl_service.detect_profit_leaks(demo_pnl, 3500000)

            return {
                "success": True,
                "data": {
                    "profit_leaks": profit_leaks,
                    "total_potential_savings": sum(
                        leak.get("potential_savings", 0)
                        for leak in profit_leaks
                        if leak.get("potential_savings")
                    ),
                    "leak_count": len(profit_leaks)
                },
                "source": "demo"
            }

    except Exception as e:
        raise HTTPException(500, f"Profit leak detection failed: {str(e)}")


# ============================================================
# FRIDAY PAYDAY - COLLECTIONS AUTOMATION
# ============================================================

from src.services.friday_payday import (
    FridayPaydaySync,
    FridayPaydayAnalytics,
    DunningEngine,
    TemplateService,
    FridayEmailService,
    PayerType,
    InvoiceStatus,
    SequenceStatus,
)

# Initialize Friday Payday services
fp_sync = FridayPaydaySync(supabase)
fp_analytics = FridayPaydayAnalytics(supabase)
fp_dunning = DunningEngine()
fp_templates = TemplateService()
fp_friday_email = FridayEmailService()


@app.get("/api/friday-payday/invoices")
async def fp_get_invoices(
    tenant_id: str = Depends(get_current_tenant_id),
    status: Optional[str] = None,
    payer_type: Optional[str] = None,
    page: int = 1,
    per_page: int = 50
):
    """Get Friday Payday invoices with filtering and pagination."""
    try:
        status_enum = InvoiceStatus(status) if status else None
        payer_type_enum = PayerType(payer_type) if payer_type else None

        invoices, total = await fp_sync.get_invoices(
            tenant_id=tenant_id,
            status=status_enum,
            payer_type=payer_type_enum,
            page=page,
            per_page=per_page
        )

        return {
            "success": True,
            "data": {
                "invoices": invoices,
                "total": total,
                "page": page,
                "per_page": per_page,
                "has_more": (page * per_page) < total
            }
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to get invoices: {str(e)}")


@app.get("/api/friday-payday/invoices/{invoice_id}")
async def fp_get_invoice(
    invoice_id: str,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Get a single Friday Payday invoice with full details."""
    try:
        invoice = await fp_sync.get_invoice_by_id(tenant_id, invoice_id)
        if not invoice:
            raise HTTPException(404, "Invoice not found")

        return {"success": True, "data": invoice}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to get invoice: {str(e)}")


@app.patch("/api/friday-payday/invoices/{invoice_id}")
async def fp_update_invoice(
    invoice_id: str,
    updates: Dict[str, Any] = Body(...),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Update a Friday Payday invoice (classification, status, etc.)."""
    try:
        # Validate payer_type if provided
        if "payer_type" in updates:
            updates["payer_type"] = PayerType(updates["payer_type"]).value

        invoice = await fp_sync.update_invoice(tenant_id, invoice_id, updates)
        if not invoice:
            raise HTTPException(404, "Invoice not found")

        return {"success": True, "data": invoice}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to update invoice: {str(e)}")


@app.post("/api/friday-payday/invoices/{invoice_id}/pause")
async def fp_pause_sequence(
    invoice_id: str,
    reason: Optional[str] = Body(None, embed=True),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Pause the dunning sequence for an invoice."""
    try:
        success = await fp_sync.pause_sequence(tenant_id, invoice_id, reason)
        if not success:
            raise HTTPException(404, "Invoice not found")

        return {"success": True, "message": "Sequence paused"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to pause sequence: {str(e)}")


@app.post("/api/friday-payday/invoices/{invoice_id}/resume")
async def fp_resume_sequence(
    invoice_id: str,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Resume the dunning sequence for an invoice."""
    try:
        success = await fp_sync.resume_sequence(tenant_id, invoice_id)
        if not success:
            raise HTTPException(404, "Invoice not found")

        return {"success": True, "message": "Sequence resumed"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to resume sequence: {str(e)}")


@app.get("/api/friday-payday/analytics/aging")
async def fp_get_ar_aging(
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Get AR aging summary."""
    try:
        aging = await fp_analytics.get_ar_aging(tenant_id)
        return {
            "success": True,
            "data": {
                "as_of_date": aging.as_of_date.isoformat(),
                "buckets": [
                    {
                        "bucket": b.bucket,
                        "amount": float(b.amount),
                        "count": b.count,
                        "percentage": float(b.percentage)
                    }
                    for b in aging.buckets
                ],
                "total_ar": float(aging.total_ar),
                "total_invoices": aging.total_invoices,
                "dso": float(aging.dso) if aging.dso else None
            }
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to get AR aging: {str(e)}")


@app.get("/api/friday-payday/analytics/dso")
async def fp_get_dso(
    tenant_id: str = Depends(get_current_tenant_id),
    days: int = 90
):
    """Get DSO trend data."""
    try:
        dso = await fp_analytics.calculate_dso(tenant_id, days)
        trend = await fp_analytics.get_dso_trend(tenant_id, days)

        return {
            "success": True,
            "data": {
                "current_dso": float(dso) if dso else None,
                "industry_benchmark": 83,
                "trend": [
                    {
                        "date": t.date.isoformat(),
                        "dso": float(t.dso),
                        "benchmark": float(t.industry_benchmark)
                    }
                    for t in trend
                ]
            }
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to get DSO: {str(e)}")


@app.get("/api/friday-payday/analytics/collected")
async def fp_get_collected(
    tenant_id: str = Depends(get_current_tenant_id),
    days: int = 7
):
    """Get collection metrics for a period."""
    try:
        metrics = await fp_analytics.get_collection_metrics(tenant_id, days)

        return {
            "success": True,
            "data": {
                "period_start": metrics.period_start.isoformat(),
                "period_end": metrics.period_end.isoformat(),
                "amount_collected": float(metrics.amount_collected),
                "invoices_paid": metrics.invoices_paid,
                "reminders_sent": metrics.reminders_sent,
                "reminders_opened": metrics.reminders_opened,
                "reminders_clicked": metrics.reminders_clicked,
                "open_rate": round(
                    metrics.reminders_opened / metrics.reminders_sent * 100, 1
                ) if metrics.reminders_sent > 0 else 0,
                "click_rate": round(
                    metrics.reminders_clicked / metrics.reminders_sent * 100, 1
                ) if metrics.reminders_sent > 0 else 0
            }
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to get collection metrics: {str(e)}")


@app.get("/api/friday-payday/summary")
async def fp_get_friday_summary(
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Get the Friday Payday weekly summary."""
    try:
        summary = await fp_analytics.get_friday_summary(tenant_id)

        return {
            "success": True,
            "data": {
                "week_start": summary.week_start.isoformat(),
                "week_end": summary.week_end.isoformat(),
                "amount_collected": float(summary.amount_collected),
                "invoices_paid": summary.invoices_paid,
                "vs_last_week": {
                    "amount": float(summary.vs_last_week_amount),
                    "percentage": float(summary.vs_last_week_pct)
                },
                "top_payments": summary.top_payments,
                "outstanding": {
                    "balance": float(summary.outstanding_balance),
                    "invoices": summary.outstanding_invoices
                },
                "current_dso": float(summary.current_dso)
            }
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to get Friday summary: {str(e)}")


@app.post("/api/friday-payday/sync")
async def fp_trigger_sync(
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Trigger a Friday Payday invoice sync from QBO data."""
    try:
        # Run sync synchronously to get results
        result = await fp_sync.sync_tenant(tenant_id)

        return {
            "success": True,
            "message": f"Synced {result.get('invoices_synced', 0)} invoices",
            "stats": result
        }
    except Exception as e:
        logger.error(f"Friday Payday sync failed for tenant {tenant_id}: {e}")
        raise HTTPException(500, f"Sync failed: {str(e)}")


@app.post("/api/friday-payday/process-dunning")
async def fp_process_dunning(
    background_tasks: BackgroundTasks,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Process dunning sequences for all overdue invoices."""
    try:
        # Run dunning in background
        async def run_dunning():
            await fp_dunning.process_tenant(tenant_id)

        background_tasks.add_task(run_dunning)

        return {
            "success": True,
            "message": "Dunning processing started in background"
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to start dunning: {str(e)}")


@app.get("/api/friday-payday/customers")
async def fp_get_customers(
    tenant_id: str = Depends(get_current_tenant_id),
    page: int = 1,
    per_page: int = 50
):
    """Get Friday Payday customers."""
    try:
        offset = (page - 1) * per_page

        result = supabase.table("fp_customers").select(
            "id, display_name, email, phone, customer_type, total_outstanding, is_suppressed"
        ).eq("tenant_id", tenant_id).order(
            "total_outstanding", desc=True
        ).range(offset, offset + per_page - 1).execute()

        count_result = supabase.table("fp_customers").select(
            "id", count="exact"
        ).eq("tenant_id", tenant_id).execute()

        return {
            "success": True,
            "data": {
                "customers": result.data or [],
                "total": count_result.count or 0,
                "page": page,
                "per_page": per_page
            }
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to get customers: {str(e)}")


@app.post("/api/friday-payday/customers/{customer_id}/suppress")
async def fp_suppress_customer(
    customer_id: str,
    reason: str = Body(..., embed=True),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Suppress communications for a customer."""
    try:
        from datetime import datetime

        result = supabase.table("fp_customers").update({
            "is_suppressed": True,
            "suppressed_reason": reason,
            "suppressed_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }).eq("tenant_id", tenant_id).eq("id", customer_id).execute()

        if not result.data:
            raise HTTPException(404, "Customer not found")

        return {"success": True, "message": "Customer suppressed"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to suppress customer: {str(e)}")


@app.get("/api/friday-payday/sequences")
async def fp_get_sequences(
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Get dunning sequences for a tenant."""
    try:
        result = supabase.table("fp_sequences").select(
            "*, fp_sequence_steps(*)"
        ).eq("tenant_id", tenant_id).order("payer_type").execute()

        return {"success": True, "data": result.data or []}
    except Exception as e:
        raise HTTPException(500, f"Failed to get sequences: {str(e)}")


@app.get("/api/friday-payday/templates")
async def fp_get_templates(
    tenant_id: str = Depends(get_current_tenant_id),
    channel: Optional[str] = None
):
    """Get message templates for a tenant."""
    try:
        templates = await fp_templates.get_templates(tenant_id, channel)
        return {"success": True, "data": templates}
    except Exception as e:
        raise HTTPException(500, f"Failed to get templates: {str(e)}")


@app.post("/api/friday-payday/templates")
async def fp_create_template(
    template: Dict[str, Any] = Body(...),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Create a new message template."""
    try:
        new_template = await fp_templates.create_template(tenant_id, template)
        return {"success": True, "data": new_template}
    except Exception as e:
        raise HTTPException(500, f"Failed to create template: {str(e)}")


@app.patch("/api/friday-payday/templates/{template_id}")
async def fp_update_template(
    template_id: str,
    updates: Dict[str, Any] = Body(...),
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Update a message template."""
    try:
        updated = await fp_templates.update_template(tenant_id, template_id, updates)
        if not updated:
            raise HTTPException(404, "Template not found")
        return {"success": True, "data": updated}
    except ValueError as e:
        raise HTTPException(400, str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to update template: {str(e)}")


@app.delete("/api/friday-payday/templates/{template_id}")
async def fp_delete_template(
    template_id: str,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Delete a message template."""
    try:
        success = await fp_templates.delete_template(tenant_id, template_id)
        if not success:
            raise HTTPException(404, "Template not found")
        return {"success": True, "message": "Template deleted"}
    except ValueError as e:
        raise HTTPException(400, str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to delete template: {str(e)}")


@app.post("/api/friday-payday/templates/seed")
async def fp_seed_templates(
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Seed default templates for a tenant."""
    try:
        count = await fp_templates.seed_default_templates(tenant_id)
        return {"success": True, "message": f"Created {count} default templates"}
    except Exception as e:
        raise HTTPException(500, f"Failed to seed templates: {str(e)}")


# Friday Summary Email Endpoints
@app.get("/api/friday-payday/summary/preview")
async def fp_preview_summary(
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Preview the Friday summary for a tenant."""
    try:
        summary = await fp_friday_email.generate_summary(tenant_id)

        # Get tenant info for email generation
        tenant_result = supabase.table("tenants").select(
            "name, fp_settings"
        ).eq("id", tenant_id).single().execute()

        tenant = tenant_result.data or {}
        fp_settings = tenant.get("fp_settings", {}) or {}

        html = fp_friday_email.generate_email_html(summary, {
            "name": tenant.get("name", "Your Company"),
            "brand_color": fp_settings.get("brand_color", "#1E40AF")
        })

        return {
            "success": True,
            "data": {
                "summary": {
                    "week_start": summary.week_start.isoformat(),
                    "week_end": summary.week_end.isoformat(),
                    "amount_collected": float(summary.amount_collected),
                    "invoices_paid": summary.invoices_paid,
                    "vs_last_week_pct": float(summary.vs_last_week_pct),
                    "outstanding_balance": float(summary.outstanding_balance),
                    "current_dso": float(summary.current_dso),
                    "top_payments": summary.top_payments
                },
                "html": html
            }
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to generate summary: {str(e)}")


@app.post("/api/friday-payday/summary/send")
async def fp_send_summary(
    background_tasks: BackgroundTasks,
    tenant_id: str = Depends(get_current_tenant_id)
):
    """Send the Friday summary email for a tenant."""
    try:
        async def send_email():
            await fp_friday_email.send_summary(tenant_id)

        background_tasks.add_task(send_email)

        return {"success": True, "message": "Friday summary email queued for sending"}
    except Exception as e:
        raise HTTPException(500, f"Failed to send summary: {str(e)}")


# Payment Portal (public endpoint - no auth required)
@app.get("/api/friday-payday/portal/{token}")
async def fp_payment_portal(token: str):
    """Get invoice details for payment portal (public)."""
    try:
        invoice = await fp_sync.get_invoice_by_payment_token(token)

        if not invoice:
            raise HTTPException(404, "Invoice not found or link expired")

        # Return only necessary fields for payment
        return {
            "success": True,
            "data": {
                "invoice_number": invoice.get("invoice_number"),
                "amount": float(invoice.get("amount", 0)),
                "balance": float(invoice.get("balance", 0)),
                "due_date": invoice.get("due_date"),
                "job_address": invoice.get("job_address"),
                "customer_name": invoice.get("fp_customers", {}).get("display_name"),
                "company_name": invoice.get("tenants", {}).get("name"),
                "brand_color": invoice.get("tenants", {}).get("fp_settings", {}).get("brand_color", "#1E40AF"),
                "logo_url": invoice.get("tenants", {}).get("fp_settings", {}).get("logo_url"),
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to load payment portal: {str(e)}")


# Demo data endpoint for Friday Payday
@app.get("/api/friday-payday/demo")
async def fp_demo_data():
    """Get demo data for Friday Payday (no auth required)."""
    from datetime import date, timedelta
    from decimal import Decimal

    today = date.today()

    demo_invoices = [
        {
            "id": "demo-inv-001",
            "invoice_number": "INV-2024-001",
            "customer_name": "Johnson Residence",
            "amount": 12500,
            "balance": 12500,
            "due_date": (today - timedelta(days=15)).isoformat(),
            "days_overdue": 15,
            "status": "overdue",
            "payer_type": "homeowner_direct",
            "sequence_status": "active",
            "job_address": "123 Oak Street, Dallas TX"
        },
        {
            "id": "demo-inv-002",
            "invoice_number": "INV-2024-002",
            "customer_name": "Smith Insurance Claim",
            "amount": 18750,
            "balance": 18750,
            "due_date": (today - timedelta(days=45)).isoformat(),
            "days_overdue": 45,
            "status": "overdue",
            "payer_type": "insurance_pending",
            "sequence_status": "active",
            "job_address": "456 Elm Avenue, Fort Worth TX"
        },
        {
            "id": "demo-inv-003",
            "invoice_number": "INV-2024-003",
            "customer_name": "Garcia Roofing",
            "amount": 8500,
            "balance": 4250,
            "due_date": (today - timedelta(days=7)).isoformat(),
            "days_overdue": 7,
            "status": "partial",
            "payer_type": "homeowner_direct",
            "sequence_status": "active",
            "job_address": "789 Pine Road, Arlington TX"
        },
        {
            "id": "demo-inv-004",
            "invoice_number": "INV-2024-004",
            "customer_name": "Williams Supplement",
            "amount": 3200,
            "balance": 3200,
            "due_date": (today - timedelta(days=30)).isoformat(),
            "days_overdue": 30,
            "status": "overdue",
            "payer_type": "supplement_pending",
            "sequence_status": "active",
            "job_address": "321 Maple Lane, Plano TX"
        },
        {
            "id": "demo-inv-005",
            "invoice_number": "INV-2024-005",
            "customer_name": "ABC Property Management",
            "amount": 45000,
            "balance": 45000,
            "due_date": (today + timedelta(days=15)).isoformat(),
            "days_overdue": 0,
            "status": "sent",
            "payer_type": "gc_commercial",
            "sequence_status": "not_started",
            "job_address": "500 Commerce Blvd, Dallas TX"
        }
    ]

    demo_aging = {
        "as_of_date": today.isoformat(),
        "buckets": [
            {"bucket": "current", "amount": 45000, "count": 1, "percentage": 53.25},
            {"bucket": "1-30", "amount": 16750, "count": 2, "percentage": 19.82},
            {"bucket": "31-60", "amount": 21950, "count": 2, "percentage": 25.98},
            {"bucket": "61-90", "amount": 0, "count": 0, "percentage": 0},
            {"bucket": "90+", "amount": 800, "count": 1, "percentage": 0.95}
        ],
        "total_ar": 84500,
        "total_invoices": 6,
        "dso": 42
    }

    demo_summary = {
        "week_start": (today - timedelta(days=7)).isoformat(),
        "week_end": today.isoformat(),
        "amount_collected": 14750,
        "invoices_paid": 4,
        "vs_last_week": {"amount": 3200, "percentage": 27.7},
        "top_payments": [
            {"amount": 8500, "customer_name": "Thompson Residence", "job_name": "Full Replacement"},
            {"amount": 3200, "customer_name": "Davis Insurance", "job_name": "Storm Damage Claim"},
            {"amount": 1800, "customer_name": "Miller Repair", "job_name": "Leak Repair"},
        ],
        "outstanding": {"balance": 84500, "invoices": 6},
        "current_dso": 42
    }

    return {
        "success": True,
        "data": {
            "invoices": demo_invoices,
            "aging": demo_aging,
            "summary": demo_summary
        },
        "source": "demo"
    }


# ============================================================
# SCHEDULED JOBS / CRON ENDPOINTS
# ============================================================

CRON_SECRET = os.getenv("CRON_SECRET", "")


def verify_cron_secret(x_cron_secret: str = Header(None)):
    """Verify the cron secret for scheduled job endpoints."""
    if not CRON_SECRET:
        # If no secret configured, allow (for development)
        return True
    if x_cron_secret != CRON_SECRET:
        raise HTTPException(401, "Invalid cron secret")
    return True


@app.post("/api/cron/process-dunning")
async def cron_process_dunning(
    _: bool = Depends(verify_cron_secret)
):
    """
    Process dunning for all tenants with Friday Payday enabled.
    Call this daily (e.g., 9am) to send overdue reminders.
    """
    try:
        # Get all tenants with Friday Payday enabled
        result = supabase.table("tenants").select(
            "id, name, fp_settings"
        ).execute()

        tenants = result.data or []
        results = {
            "processed": 0,
            "skipped": 0,
            "failed": 0,
            "details": []
        }

        for tenant in tenants:
            fp_settings = tenant.get("fp_settings", {}) or {}
            if not fp_settings.get("enabled", False):
                results["skipped"] += 1
                continue

            try:
                summary = await fp_dunning.process_tenant(tenant["id"])
                results["processed"] += 1
                results["details"].append({
                    "tenant_id": tenant["id"],
                    "tenant_name": tenant.get("name"),
                    "reminders_sent": summary.get("reminders_sent", 0),
                })
            except Exception as e:
                logger.error(f"Dunning failed for tenant {tenant['id']}: {e}")
                results["failed"] += 1
                results["details"].append({
                    "tenant_id": tenant["id"],
                    "error": str(e),
                })

        return {
            "success": True,
            "message": f"Processed {results['processed']} tenants",
            "results": results
        }

    except Exception as e:
        logger.error(f"Cron dunning failed: {e}")
        raise HTTPException(500, f"Failed to process dunning: {str(e)}")


@app.post("/api/cron/friday-summary")
async def cron_friday_summary(
    _: bool = Depends(verify_cron_secret)
):
    """
    Send Friday Payday weekly summary to all enabled tenants.
    Call this every Friday (e.g., 5pm) to send weekly summaries.
    """
    try:
        result = await fp_email.send_all_summaries()

        return {
            "success": True,
            "message": f"Sent {result.get('sent', 0)} summaries",
            "results": result
        }

    except Exception as e:
        logger.error(f"Cron Friday summary failed: {e}")
        raise HTTPException(500, f"Failed to send summaries: {str(e)}")


@app.post("/api/cron/sync-invoices")
async def cron_sync_invoices(
    _: bool = Depends(verify_cron_secret)
):
    """
    Sync invoices from QuickBooks for all connected tenants.
    Call this daily (e.g., 6am) to keep invoice data fresh.
    """
    try:
        # Get all tenants with QBO connected
        result = supabase.table("tenant_integrations").select(
            "tenant_id, tenants(name)"
        ).eq("provider", "quickbooks").eq("is_active", True).execute()

        integrations = result.data or []
        results = {
            "synced": 0,
            "failed": 0,
            "details": []
        }

        for integration in integrations:
            tenant_id = integration.get("tenant_id")
            tenant_name = integration.get("tenants", {}).get("name", "Unknown")

            try:
                sync_result = await fp_sync.sync_tenant(tenant_id)
                results["synced"] += 1
                results["details"].append({
                    "tenant_id": tenant_id,
                    "tenant_name": tenant_name,
                    "invoices_synced": sync_result.get("invoices_synced", 0),
                })
            except Exception as e:
                logger.error(f"Invoice sync failed for tenant {tenant_id}: {e}")
                results["failed"] += 1
                results["details"].append({
                    "tenant_id": tenant_id,
                    "error": str(e),
                })

        return {
            "success": True,
            "message": f"Synced {results['synced']} tenants",
            "results": results
        }

    except Exception as e:
        logger.error(f"Cron invoice sync failed: {e}")
        raise HTTPException(500, f"Failed to sync invoices: {str(e)}")


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
