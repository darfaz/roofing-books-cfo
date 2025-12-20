-- Quick check: Do you have tenants and QBO integrations?
-- Run this first to see the current state

-- 1. Check tenants
SELECT 'Tenants' as check_type, COUNT(*) as count FROM tenants
UNION ALL
-- 2. Check QBO integrations
SELECT 'QBO Integrations' as check_type, COUNT(*) as count 
FROM tenant_integrations 
WHERE provider = 'quickbooks' AND is_active = true;

-- 3. Detailed view
SELECT 
    t.id as tenant_id,
    t.name as tenant_name,
    CASE 
        WHEN ti.id IS NOT NULL THEN '✅ Connected'
        ELSE '❌ Not Connected'
    END as qbo_status,
    ti.realm_id,
    ti.is_active,
    ti.token_expires_at,
    ti.created_at as connected_at
FROM tenants t
LEFT JOIN tenant_integrations ti 
    ON t.id = ti.tenant_id 
    AND ti.provider = 'quickbooks'
ORDER BY t.created_at DESC;






