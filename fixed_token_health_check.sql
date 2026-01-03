-- Fixed QuickBooks Integration Token Health Report
-- This correctly checks if tokens are expired

SELECT
    ti.tenant_id,
    t.name as tenant_name,
    ti.provider,
    ti.realm_id,
    ti.is_active,
    CASE 
        WHEN ti.access_token IS NOT NULL THEN '✅ Present'
        ELSE '❌ Missing'
    END as access_token_status,
    CASE 
        WHEN ti.refresh_token IS NOT NULL THEN '✅ Present'
        ELSE '❌ Missing'
    END as refresh_token_status,
    ti.token_expires_at,
    CASE 
        WHEN ti.token_expires_at IS NULL THEN '⚠️ Unknown'
        WHEN ti.token_expires_at > NOW() THEN '✅ Valid'
        ELSE '❌ Expired'
    END as token_validity,
    CASE 
        WHEN ti.token_expires_at IS NOT NULL 
        THEN EXTRACT(EPOCH FROM (ti.token_expires_at - NOW())) / 3600
        ELSE NULL
    END as hours_until_expiry,
    ti.created_at,
    ti.updated_at
FROM tenant_integrations ti
LEFT JOIN tenants t ON ti.tenant_id = t.id
WHERE ti.provider = 'quickbooks'
ORDER BY ti.created_at DESC;








