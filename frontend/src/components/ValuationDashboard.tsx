import { useEffect, useMemo, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { supabase } from '../lib/supabase'
import { ScenarioSimulator } from './ScenarioSimulator'
import { ExitReadiness } from './ExitReadiness'
import { ValuationRoadmap } from './ValuationRoadmap'
import { ShockReport } from './ShockReport'
import { ProfitLeakReport } from './ProfitLeakReport'
import { OwnerDashboard } from './OwnerDashboard'
import { FinanceDashboard } from './FinanceDashboard'
import { Tabs } from './ui/Tabs'
import { GlassCard } from './ui/GlassCard'
import { useDemoMode } from '../context/DemoContext'

interface ValuationSnapshot {
  id: string
  as_of_date: string
  ttm_revenue: number
  ttm_sde: number
  ttm_ebitda: number
  tier: 'below_avg' | 'avg' | 'above_avg'
  multiple_low: number
  multiple_high: number
  ev_low: number
  ev_high: number
  confidence_score: number
  created_at: string
  updated_at: string
}

// Data is fetched directly from Supabase

export function ValuationDashboard({ accessToken }: { accessToken: string }) {
  const [snapshot, setSnapshot] = useState<ValuationSnapshot | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'dashboard' | 'finance' | 'leaks' | 'shock' | 'scenario' | 'exit' | 'roadmap'>('dashboard')
  const [qboConnected, setQboConnected] = useState<boolean | null>(null)
  const [creatingSnapshot, setCreatingSnapshot] = useState(false)
  const { isDemoMode } = useDemoMode()

  useEffect(() => {
    void fetchValuationData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [accessToken, isDemoMode])

  const fetchValuationData = async () => {
    try {
      setLoading(true)
      setError(null)

      // In demo mode, fetch from demo API or use fallback data
      if (isDemoMode) {
        try {
          const response = await fetch('/api/demo/dashboard')
          if (response.ok) {
            const demoData = await response.json()
            const data = demoData.data || demoData
            setSnapshot({
              id: 'demo-snapshot',
              as_of_date: new Date().toISOString().split('T')[0],
              ttm_revenue: data.summary?.ttm_revenue || 3500000,
              ttm_sde: data.summary?.ttm_profit ? data.summary.ttm_profit * 1.4 : 350000,
              ttm_ebitda: data.summary?.ttm_profit || 245000,
              tier: 'below_avg',
              multiple_low: 2.5,
              multiple_high: 3.5,
              ev_low: (data.summary?.ttm_profit || 245000) * 2.5,
              ev_high: (data.summary?.ttm_profit || 245000) * 3.5,
              confidence_score: 72,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            })
          } else {
            throw new Error('Demo API not available')
          }
        } catch {
          // Fallback to hardcoded demo data
          setSnapshot({
            id: 'demo-snapshot',
            as_of_date: new Date().toISOString().split('T')[0],
            ttm_revenue: 3500000,
            ttm_sde: 350000,
            ttm_ebitda: 245000,
            tier: 'below_avg',
            multiple_low: 2.5,
            multiple_high: 3.5,
            ev_low: 612500,
            ev_high: 857500,
            confidence_score: 72,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          })
        }
        setQboConnected(true) // Simulate connected in demo
        setLoading(false)
        return
      }

      // Get user's tenant_id from session
      const { data: { user } } = await supabase.auth.getUser()
      const tenantId = user?.user_metadata?.tenant_id

      if (!tenantId) {
        setError('No tenant_id found in user metadata')
        return
      }

      // Check QBO connection status
      const { data: integrationData } = await supabase
        .from('tenant_integrations')
        .select('is_active')
        .eq('tenant_id', tenantId)
        .eq('provider', 'quickbooks')
        .single()

      setQboConnected(integrationData?.is_active === true)

      // Fetch latest snapshot directly from Supabase
      const { data: snapshotData, error: snapshotError } = await supabase
        .from('valuation_snapshots')
        .select('*')
        .eq('tenant_id', tenantId)
        .order('as_of_date', { ascending: false })
        .order('created_at', { ascending: false })
        .limit(1)
        .single()

      if (snapshotError && snapshotError.code !== 'PGRST116') {
        console.error('Snapshot error:', snapshotError)
      }
      if (snapshotData) setSnapshot(snapshotData)

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load valuation data')
    } finally {
      setLoading(false)
    }
  }

  const createValuationSnapshot = async () => {
    try {
      setCreatingSnapshot(true)
      setError(null)

      const response = await fetch('/api/valuation/snapshot', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      })

      const result = await response.json()

      if (!response.ok) {
        throw new Error(result.error?.message || 'Failed to create snapshot')
      }

      // Refresh data after creating snapshot
      await fetchValuationData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create valuation snapshot')
    } finally {
      setCreatingSnapshot(false)
    }
  }

  const formatDate = (dateString: string): string =>
    new Date(dateString).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })

  const getTierConfig = (tier: string) => {
    switch (tier) {
      case 'above_avg':
        return { label: 'Above Average', color: 'emerald', variant: 'success' as const }
      case 'avg':
        return { label: 'Average', color: 'blue', variant: 'info' as const }
      case 'below_avg':
        return { label: 'Below Average', color: 'amber', variant: 'warning' as const }
      default:
        return { label: tier, color: 'slate', variant: 'default' as const }
    }
  }

  const tabOptions = useMemo(
    () => [
      { key: 'dashboard' as const, label: 'Dashboard', icon: '📊' },
      { key: 'finance' as const, label: 'Finance', icon: '💵' },
      { key: 'leaks' as const, label: 'Profit Leaks', icon: '🔍' },
      { key: 'shock' as const, label: 'Shock Report', icon: '⚡' },
      { key: 'scenario' as const, label: 'Simulator', icon: '🎮' },
      { key: 'exit' as const, label: 'Exit Readiness', icon: '🚀' },
      { key: 'roadmap' as const, label: 'Roadmap', icon: '🗺️' },
    ],
    [],
  )

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white p-6">
        <div className="max-w-7xl mx-auto flex items-center justify-center h-64">
          <motion.div
            className="flex items-center gap-3 text-slate-400"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <motion.div
              className="w-6 h-6 border-2 border-emerald-500 border-t-transparent rounded-full"
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            />
            Loading valuation data...
          </motion.div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white p-6">
        <div className="max-w-7xl mx-auto">
          <GlassCard variant="danger">
            <div className="flex items-center gap-3">
              <span className="text-2xl">⚠️</span>
              <div>
                <div className="font-semibold text-red-300">Error Loading Data</div>
                <div className="text-sm text-red-400/80">{error}</div>
              </div>
            </div>
          </GlassCard>
        </div>
      </div>
    )
  }

  if (!snapshot) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white p-6">
        <div className="max-w-7xl mx-auto">
          <GlassCard padding="lg" className="text-center max-w-xl mx-auto">
            <div className="text-5xl mb-4">📊</div>
            <h2 className="text-2xl font-bold mb-2">Welcome to Your Dashboard</h2>

            {qboConnected ? (
              <>
                <p className="text-slate-400 mb-6">
                  QuickBooks is connected. Create your first valuation snapshot to see your business valuation.
                </p>
                {error && (
                  <div className="bg-red-500/20 border border-red-500/30 text-red-400 text-sm p-3 rounded-lg mb-4">
                    {error}
                  </div>
                )}
                <motion.button
                  onClick={() => void createValuationSnapshot()}
                  disabled={creatingSnapshot}
                  className="bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 text-black font-semibold px-6 py-3 rounded-lg transition"
                  whileHover={{ scale: creatingSnapshot ? 1 : 1.05 }}
                  whileTap={{ scale: creatingSnapshot ? 1 : 0.95 }}
                >
                  {creatingSnapshot ? (
                    <span className="flex items-center gap-2">
                      <div className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                      Creating Snapshot...
                    </span>
                  ) : (
                    'Create Valuation Snapshot'
                  )}
                </motion.button>
              </>
            ) : (
              <>
                <p className="text-slate-400 mb-6">
                  Connect your QuickBooks Online account to analyze your financials and get your business valuation.
                </p>
                <p className="text-sm text-slate-500">
                  Use the "Connect QuickBooks" button in the header to get started.
                </p>
              </>
            )}
          </GlassCard>
        </div>
      </div>
    )
  }

  const currentMultipleAvg = (snapshot.multiple_low + snapshot.multiple_high) / 2
  const tierConfig = getTierConfig(snapshot.tier)

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white">
      {/* Background decoration */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-1/2 -right-1/2 w-full h-full bg-emerald-500/5 rounded-full blur-3xl" />
        <div className="absolute -bottom-1/2 -left-1/2 w-full h-full bg-blue-500/5 rounded-full blur-3xl" />
      </div>

      <div className="relative p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Header */}
          <motion.div
            className="flex flex-col sm:flex-row sm:items-center justify-between gap-4"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
                Valuation Dashboard
              </h1>
              <p className="text-slate-400 mt-1">As of {formatDate(snapshot.as_of_date)}</p>
            </div>
            <div className="flex items-center gap-3">
              <GlassCard variant={tierConfig.variant} padding="sm" hover={false}>
                <div className="text-xs text-slate-400">Tier</div>
                <div className="font-semibold">{tierConfig.label}</div>
              </GlassCard>
              <motion.button
                onClick={() => void fetchValuationData()}
                className="bg-slate-800 hover:bg-slate-700 text-white font-medium px-4 py-2 rounded-lg transition border border-slate-700"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                Refresh
              </motion.button>
            </div>
          </motion.div>

          {/* Tabs */}
          <Tabs value={activeTab} onChange={setActiveTab} tabs={tabOptions} />

          <AnimatePresence mode="wait">
            {activeTab === 'dashboard' && (
              <motion.div
                key="dashboard"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <OwnerDashboard isDemoMode={isDemoMode} />
              </motion.div>
            )}
            {activeTab === 'finance' && (
              <motion.div
                key="finance"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <FinanceDashboard accessToken={accessToken} isDemoMode={isDemoMode} />
              </motion.div>
            )}
            {activeTab === 'leaks' && (
              <motion.div
                key="leaks"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <ProfitLeakReport accessToken={accessToken} isDemoMode={isDemoMode} />
              </motion.div>
            )}

            {activeTab === 'shock' && (
              <motion.div
                key="shock"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <ShockReport
                  accessToken={accessToken}
                  isDemoMode={isDemoMode}
                  onStartTrial={() => {
                    // TODO: Implement trial flow
                    console.log('Trial started')
                  }}
                />
              </motion.div>
            )}

            {activeTab === 'scenario' && (
              <motion.div
                key="scenario"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <ScenarioSimulator
                  accessToken={accessToken}
                  isDemoMode={isDemoMode}
                  currentEbitda={snapshot.ttm_ebitda}
                  currentMultiple={Number(currentMultipleAvg.toFixed(2))}
                  currentEvLow={snapshot.ev_low}
                  currentEvHigh={snapshot.ev_high}
                />
              </motion.div>
            )}

            {activeTab === 'exit' && (
              <motion.div
                key="exit"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <ExitReadiness accessToken={accessToken} isDemoMode={isDemoMode} />
              </motion.div>
            )}

            {activeTab === 'roadmap' && (
              <motion.div
                key="roadmap"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <ValuationRoadmap accessToken={accessToken} isDemoMode={isDemoMode} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}
