import { useEffect, useMemo, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { supabase } from '../lib/supabase'
import { ScenarioSimulator } from './ScenarioSimulator'
import { ExitReadiness } from './ExitReadiness'
import { ValuationRoadmap } from './ValuationRoadmap'
import { ShockReport } from './ShockReport'
import { OwnerDashboard } from './OwnerDashboard'
import { Tabs } from './ui/Tabs'
import { GaugeMeter } from './ui/GaugeMeter'
import { AnimatedCurrency, AnimatedPercentage } from './ui/AnimatedNumber'
import { RadarChart } from './ui/RadarChart'
import { GlassCard, MetricCard } from './ui/GlassCard'
import { DriverScoreCard } from './ui/DriverScoreCard'
import { Sparkline } from './ui/Sparkline'

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

interface DriverScore {
  id: string
  driver_key: string
  score: number
  confidence: number
  computed_by: string
  as_of_date: string
}

const DRIVER_LABELS: Record<string, { label: string; icon: string; description: string }> = {
  management_independence: {
    label: 'Management Independence',
    icon: '👔',
    description: 'Reduced owner dependency',
  },
  financial_records: {
    label: 'Financial Records',
    icon: '📊',
    description: 'Clean, organized books',
  },
  recurring_revenue: {
    label: 'Recurring Revenue',
    icon: '🔄',
    description: 'Predictable income streams',
  },
  operational_systems: {
    label: 'Operational Systems',
    icon: '⚙️',
    description: 'Systematized processes',
  },
  customer_diversity: {
    label: 'Customer Diversity',
    icon: '👥',
    description: 'Low concentration risk',
  },
  market_outlook: {
    label: 'Market Outlook',
    icon: '📈',
    description: 'Favorable market conditions',
  },
}

// Data is fetched directly from Supabase

export function ValuationDashboard({ accessToken }: { accessToken: string }) {
  const [snapshot, setSnapshot] = useState<ValuationSnapshot | null>(null)
  const [driverScores, setDriverScores] = useState<DriverScore[]>([])
  const [historicalSnapshots, setHistoricalSnapshots] = useState<ValuationSnapshot[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'dashboard' | 'overview' | 'shock' | 'scenario' | 'exit' | 'roadmap'>('dashboard')

  useEffect(() => {
    void fetchValuationData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [accessToken])

  const fetchValuationData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Get user's tenant_id from session
      const { data: { user } } = await supabase.auth.getUser()
      const tenantId = user?.user_metadata?.tenant_id

      if (!tenantId) {
        setError('No tenant_id found in user metadata')
        return
      }

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

      // Fetch driver scores
      const { data: driversData, error: driversError } = await supabase
        .from('driver_scores')
        .select('*')
        .eq('tenant_id', tenantId)
        .order('as_of_date', { ascending: false })

      if (driversError) console.error('Drivers error:', driversError)
      if (driversData) setDriverScores(driversData)

      // Fetch historical snapshots
      const { data: histData, error: histError } = await supabase
        .from('valuation_snapshots')
        .select('*')
        .eq('tenant_id', tenantId)
        .order('as_of_date', { ascending: false })
        .limit(12)

      if (histError) console.error('History error:', histError)
      if (histData) setHistoricalSnapshots(histData)

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load valuation data')
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (value: number): string =>
    new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value)

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

  // Driver scores are already 0-100 in database
  const scoreTo100 = (score: number) => Math.round(score)

  const tabOptions = useMemo(
    () => [
      { key: 'dashboard' as const, label: 'Dashboard', icon: '📊' },
      { key: 'overview' as const, label: 'Valuation', icon: '💰' },
      { key: 'shock' as const, label: 'Shock Report', icon: '⚡' },
      { key: 'scenario' as const, label: 'Simulator', icon: '🎮' },
      { key: 'exit' as const, label: 'Exit Readiness', icon: '🚀' },
      { key: 'roadmap' as const, label: 'Roadmap', icon: '🗺️' },
    ],
    [],
  )

  // Prepare radar chart data
  const radarData = useMemo(() => {
    return Object.entries(DRIVER_LABELS).map(([key, meta]) => {
      const score = driverScores.find((d) => d.driver_key === key)?.score ?? 0
      return {
        subject: meta.label.split(' ')[0],
        value: scoreTo100(score),
        fullMark: 100,
        icon: meta.icon,
      }
    })
  }, [driverScores])

  // Prepare sparkline data from historical snapshots
  const sparklineData = useMemo(() => {
    return historicalSnapshots
      .slice()
      .reverse()
      .map((snap) => ({
        value: (snap.ev_low + snap.ev_high) / 2,
        label: formatDate(snap.as_of_date),
      }))
  }, [historicalSnapshots])

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
          <GlassCard padding="lg" className="text-center">
            <div className="text-5xl mb-4">📊</div>
            <h2 className="text-2xl font-bold mb-2">No Valuation Snapshot Yet</h2>
            <p className="text-slate-400 mb-6">Create a snapshot via the API to populate the dashboard.</p>
            <motion.button
              onClick={() => void fetchValuationData()}
              className="bg-emerald-500 hover:bg-emerald-400 text-black font-semibold px-6 py-3 rounded-lg transition"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Refresh
            </motion.button>
          </GlassCard>
        </div>
      </div>
    )
  }

  const avgValue = (snapshot.ev_low + snapshot.ev_high) / 2
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
                <OwnerDashboard />
              </motion.div>
            )}
            {activeTab === 'overview' && (
              <motion.div
                key="overview"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-6"
              >
                {/* Main EV Display */}
                <GlassCard padding="lg" glow>
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
                    <div className="flex flex-col items-center">
                      <h2 className="text-xl font-semibold mb-6 text-slate-300">Enterprise Value</h2>
                      <GaugeMeter
                        value={avgValue}
                        min={snapshot.ev_low * 0.5}
                        max={snapshot.ev_high * 1.5}
                        label={`${formatCurrency(snapshot.ev_low)} - ${formatCurrency(snapshot.ev_high)}`}
                        formatValue={formatCurrency}
                        size="lg"
                      />
                    </div>

                    <div className="space-y-4">
                      {/* Key Metrics */}
                      <div className="grid grid-cols-2 gap-4">
                        <MetricCard
                          label="TTM Revenue"
                          value={<AnimatedCurrency value={snapshot.ttm_revenue} />}
                          icon="💰"
                        />
                        <MetricCard
                          label="TTM EBITDA"
                          value={<AnimatedCurrency value={snapshot.ttm_ebitda} />}
                          icon="📈"
                        />
                        <MetricCard
                          label="TTM SDE"
                          value={<AnimatedCurrency value={snapshot.ttm_sde} />}
                          icon="🎯"
                        />
                        <MetricCard
                          label="Multiple"
                          value={`${snapshot.multiple_low}x - ${snapshot.multiple_high}x`}
                          icon="✖️"
                        />
                      </div>

                      {/* Confidence */}
                      <GlassCard padding="sm">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm text-slate-400">Confidence Score</span>
                          <span className="font-bold text-emerald-400">
                            <AnimatedPercentage value={snapshot.confidence_score} />
                          </span>
                        </div>
                        <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                          <motion.div
                            className="h-full bg-gradient-to-r from-emerald-500 to-emerald-400 rounded-full"
                            initial={{ width: 0 }}
                            animate={{ width: `${snapshot.confidence_score}%` }}
                            transition={{ duration: 1, ease: 'easeOut' }}
                          />
                        </div>
                      </GlassCard>
                    </div>
                  </div>
                </GlassCard>

                {/* Driver Scores Section */}
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-semibold">Value Driver Scores</h2>
                    <span className="text-sm text-slate-400">6 key drivers analyzed</span>
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Radar Chart */}
                    <GlassCard className="lg:col-span-1" padding="md">
                      <h3 className="text-sm font-medium text-slate-400 mb-4 text-center">Driver Overview</h3>
                      <div className="h-64">
                        <RadarChart data={radarData} color="#10b981" />
                      </div>
                    </GlassCard>

                    {/* Driver Cards */}
                    <div className="lg:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {Object.entries(DRIVER_LABELS).map(([key, meta], index) => {
                        const score = driverScores.find((d) => d.driver_key === key)?.score ?? 0
                        return (
                          <DriverScoreCard
                            key={key}
                            icon={meta.icon}
                            label={meta.label}
                            description={meta.description}
                            score={scoreTo100(score)}
                            delay={index * 0.1}
                          />
                        )
                      })}
                    </div>
                  </div>
                </div>

                {/* Timeline / Historical Chart */}
                <GlassCard padding="lg">
                  <div className="flex items-center justify-between mb-6">
                    <div>
                      <h2 className="text-xl font-semibold">Valuation Timeline</h2>
                      <p className="text-sm text-slate-400 mt-1">Track your value growth over time</p>
                    </div>
                    {sparklineData.length > 1 && (
                      <div className="text-right">
                        <div className="text-sm text-slate-400">Latest</div>
                        <div className="text-lg font-bold text-emerald-400">
                          {formatCurrency(sparklineData[sparklineData.length - 1]?.value || 0)}
                        </div>
                      </div>
                    )}
                  </div>

                  {sparklineData.length > 0 ? (
                    <div className="h-48">
                      <Sparkline data={sparklineData} color="#10b981" height={192} />
                    </div>
                  ) : (
                    <div className="h-48 flex items-center justify-center text-slate-500">
                      No historical data available yet
                    </div>
                  )}

                  {/* Timeline dots */}
                  {sparklineData.length > 0 && (
                    <div className="flex justify-between mt-4 px-2">
                      {sparklineData.map((point, i) => (
                        <div key={i} className="text-center">
                          <div className="w-2 h-2 bg-emerald-500 rounded-full mx-auto mb-1" />
                          <div className="text-[10px] text-slate-500">{point.label}</div>
                        </div>
                      ))}
                    </div>
                  )}
                </GlassCard>
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
                <ExitReadiness accessToken={accessToken} />
              </motion.div>
            )}

            {activeTab === 'roadmap' && (
              <motion.div
                key="roadmap"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <ValuationRoadmap accessToken={accessToken} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}
