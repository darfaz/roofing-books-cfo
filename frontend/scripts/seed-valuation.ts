/**
 * Seed test data for the valuation module (Supabase).
 *
 * Loaded from ../.env via DOTENV_CONFIG_PATH (see package.json script).
 * Requires:
 *   - SUPABASE_URL
 *   - SUPABASE_SERVICE_KEY (service role key; required to bypass RLS)
 * Optional:
 *   - TENANT_ID (uuid). If omitted, uses the first tenant in `tenants`.
 */

import 'dotenv/config'
import { createClient } from '@supabase/supabase-js'

type Tier = 'below_avg' | 'avg' | 'above_avg'
type DriverKey =
  | 'management_independence'
  | 'financial_records'
  | 'recurring_revenue'
  | 'operational_systems'
  | 'customer_diversity'
  | 'market_outlook'

const SUPABASE_URL = process.env.SUPABASE_URL
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_KEY
const TENANT_ID = process.env.TENANT_ID

if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) {
  // eslint-disable-next-line no-console
  console.error('Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in environment (check DOTENV_CONFIG_PATH).')
  process.exit(1)
}

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY, {
  auth: { persistSession: false },
})

function isoDate(d: Date) {
  return d.toISOString().slice(0, 10)
}

async function resolveTenantId(): Promise<string> {
  if (TENANT_ID) return TENANT_ID
  const { data, error } = await supabase.from('tenants').select('id').order('created_at', { ascending: true }).limit(1)
  if (error) throw error
  const id = data?.[0]?.id
  if (!id) throw new Error('No tenants found. Set TENANT_ID env var.')
  return id
}

async function main() {
  const tenantId = await resolveTenantId()

  // Requested values (mapped to DB enums)
  const tier: Tier = 'avg' // user asked "average" (DB enum is 'avg')

  const today = new Date()
  const asOf = isoDate(today)

  const base = {
    ttm_revenue: 2_500_000,
    ttm_sde: 375_000,
    ttm_ebitda: 312_500,
    tier,
    multiple_low: 4.5,
    multiple_high: 5.0,
    ev_low: 1_406_250,
    ev_high: 1_562_500,
    confidence_score: 88,
    drivers_json: {},
    computed_by: 'seed',
    automation_tier: 'hybrid',
    human_reviewed: false,
    review_required: false,
  }

  // Re-runnable: delete snapshot for same day then insert
  await supabase.from('valuation_snapshots').delete().eq('tenant_id', tenantId).eq('as_of_date', asOf)
  const { data: insertedSnap, error: snapErr } = await supabase
    .from('valuation_snapshots')
    .insert({ tenant_id: tenantId, as_of_date: asOf, ...base })
    .select('id')
    .single()
  if (snapErr) throw snapErr

  const snapshotId = insertedSnap.id as string

  // Driver scores (note: DB key is 'financial_records', user provided 'financial_records_quality')
  const driverScores: Array<{ driver_key: DriverKey; score: number }> = [
    { driver_key: 'management_independence', score: 65 },
    { driver_key: 'financial_records', score: 78 },
    { driver_key: 'recurring_revenue', score: 42 },
    { driver_key: 'operational_systems', score: 55 },
    { driver_key: 'customer_diversity', score: 71 },
    { driver_key: 'market_outlook', score: 68 },
  ]

  const driverRows = driverScores.map((d) => ({
    tenant_id: tenantId,
    valuation_snapshot_id: snapshotId,
    as_of_date: asOf,
    driver_key: d.driver_key,
    score: d.score,
    weight: 1.0,
    evidence_refs: [],
    computed_by: 'seed',
    confidence: 85,
    automation_tier: 'hybrid',
    human_reviewed: false,
  }))

  // Unique constraint: (tenant_id, as_of_date, driver_key)
  const { error: driverErr } = await supabase.from('driver_scores').upsert(driverRows, {
    onConflict: 'tenant_id,as_of_date,driver_key',
  })
  if (driverErr) throw driverErr

  // Historical snapshots for timeline chart (3 months back)
  const history = [1, 2, 3].map((monthsBack) => {
    const d = new Date(today)
    d.setMonth(d.getMonth() - monthsBack)
    const dateStr = isoDate(d)
    const factor = 1 - monthsBack * 0.04 // small decline into the past
    const ttmRevenue = Math.round(base.ttm_revenue * factor)
    const ebitda = Math.round(base.ttm_ebitda * factor)
    const evLow = Math.round(ebitda * base.multiple_low)
    const evHigh = Math.round(ebitda * base.multiple_high)
    return {
      tenant_id: tenantId,
      as_of_date: dateStr,
      ...base,
      ttm_revenue: ttmRevenue,
      ttm_sde: Math.round(base.ttm_sde * factor),
      ttm_ebitda: ebitda,
      ev_low: evLow,
      ev_high: evHigh,
      computed_by: 'seed',
    }
  })

  for (const h of history) {
    await supabase.from('valuation_snapshots').delete().eq('tenant_id', tenantId).eq('as_of_date', h.as_of_date)
    const { error } = await supabase.from('valuation_snapshots').insert(h)
    if (error) throw error
  }

  // eslint-disable-next-line no-console
  console.log('Seeded valuation data:', { tenantId, snapshotId, asOf, history: history.map((h) => h.as_of_date) })
}

main().catch((e) => {
  // eslint-disable-next-line no-console
  console.error(e)
  process.exit(1)
})



