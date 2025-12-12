-- Step 1: First, let's see what tenants exist
SELECT id, name, created_at 
FROM tenants 
ORDER BY created_at DESC;

-- Step 2: Check for any existing QBO integrations (without filtering by tenant_id)
SELECT 
    tenant_id,
    provider,
    realm_id,
    is_active,
    token_expires_at,
    created_at,
    updated_at,
    CASE 
        WHEN token_expires_at > NOW() THEN 'Valid'
        WHEN token_expires_at IS NULL THEN 'Unknown'
        ELSE 'Expired'
    END as token_status
FROM tenant_integrations
WHERE provider = 'quickbooks'
ORDER BY created_at DESC;

-- Step 3: If you know your tenant_id, use this query (replace with actual UUID):
-- SELECT 
--     tenant_id,
--     provider,
--     realm_id,
--     is_active,
--     token_expires_at,
--     created_at,
--     updated_at
-- FROM tenant_integrations
-- WHERE provider = 'quickbooks'
--   AND tenant_id = 'your-actual-uuid-here';

-- Step 4: To see full details including token presence (without showing actual tokens):
SELECT 
    ti.tenant_id,
    t.name as tenant_name,
    ti.provider,
    ti.realm_id,
    ti.is_active,
    CASE 
        WHEN ti.access_token IS NOT NULL THEN 'Present'
        ELSE 'Missing'
    END as access_token_status,
    CASE 
        WHEN ti.refresh_token IS NOT NULL THEN 'Present'
        ELSE 'Missing'
    END as refresh_token_status,
    ti.token_expires_at,
    CASE 
        WHEN ti.token_expires_at > NOW() THEN 'Valid'
        WHEN ti.token_expires_at IS NULL THEN 'Unknown'
        ELSE 'Expired'
    END as token_validity,
    ti.created_at,
    ti.updated_at
FROM tenant_integrations ti
LEFT JOIN tenants t ON ti.tenant_id = t.id
WHERE ti.provider = 'quickbooks'
ORDER BY ti.created_at DESC;

