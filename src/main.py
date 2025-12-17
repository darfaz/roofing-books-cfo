"""
Roofing Books CFO - API Server
FastAPI application for bookkeeping automation
"""
import os
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Depends, Body, UploadFile, File, Form
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
    
    # Calculate token expiration
    expires_in = tokens.get("expires_in", 3600)  # Default to 1 hour if not provided
    token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
    
    # Store tokens in Supabase
    result = supabase.table("tenant_integrations").upsert({
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
# RUN SERVER
# ============================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=os.getenv("APP_ENV") == "development"
    )
