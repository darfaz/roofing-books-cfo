"""
Auth helpers (Supabase Auth JWT -> tenant context).

Recommended approach:
- Frontend authenticates with Supabase Auth and sends `Authorization: Bearer <access_token>`
- Backend derives `tenant_id` from the authenticated user's metadata (no tenant_id query params)
"""

import os
from fastapi import Header, HTTPException
from supabase import create_client, Client


def _get_supabase_anon_client() -> Client:
    url = os.getenv("SUPABASE_URL", "")
    anon_key = os.getenv("SUPABASE_ANON_KEY", "")
    if not url or not anon_key:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "SERVER_MISCONFIGURED",
                    "message": "Supabase anon credentials not configured (SUPABASE_URL / SUPABASE_ANON_KEY).",
                },
            },
        )
    return create_client(url, anon_key)


def get_current_tenant_id(authorization: str = Header(default="")) -> str:
    """
    Extract tenant_id from Supabase Auth JWT.

    Expects:
      Authorization: Bearer <access_token>

    Looks for tenant_id in:
      - user.user_metadata.tenant_id (preferred)
      - user.app_metadata.tenant_id (fallback)
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Missing or invalid Authorization header.",
                },
            },
        )

    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "error": {"code": "UNAUTHORIZED", "message": "Empty bearer token."},
            },
        )

    sb = _get_supabase_anon_client()
    try:
        user_resp = sb.auth.get_user(token)
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "error": {"code": "UNAUTHORIZED", "message": f"Invalid token: {str(e)}"},
            },
        )

    user = getattr(user_resp, "user", None)
    if not user:
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "error": {"code": "UNAUTHORIZED", "message": "Invalid token."},
            },
        )

    tenant_id = None
    user_meta = getattr(user, "user_metadata", None) or {}
    app_meta = getattr(user, "app_metadata", None) or {}
    tenant_id = user_meta.get("tenant_id") or app_meta.get("tenant_id")

    if not tenant_id:
        raise HTTPException(
            status_code=403,
            detail={
                "success": False,
                "error": {
                    "code": "FORBIDDEN",
                    "message": "User is missing tenant_id in Supabase user metadata.",
                },
            },
        )

    return tenant_id








