import { useEffect, useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { supabase } from '../lib/supabase'
import { GlassCard, MetricCard } from './ui/GlassCard'
import { AnimatedCurrency } from './ui/AnimatedNumber'

interface OwnerView {
  revenue: number
  ebitda: number
  owner_comp: number
  addbacks: number
  expected_multiple: number
  expected_valuation: number
}

interface BuyerView {
  defensible_ebitda: number
  defensible_sde: number
  multiple_low: number
  multiple_high: number
  valuation_low: number
  valuation_high: number
}

interface GapAnalysis {
  ebitda_haircut: number
  multiple_penalty: number
  value_gap: number
  value_gap_percentage: number
}

interface EbitdaAdjustment {
  id: string
  type: string
  category: 'accepted' | 'rejected' | 'partial' | 'needs_review'
  description: string
  amount: number
  accepted_amount: number
  buyer_concern: string | null
  rejection_reason: string | null
  is_recoverable: boolean
  remediation_action: string | null
  remediation_effort: string | null
  remediation_impact: number
}

interface MultiplePenalty {
  id: string
  driver_key: string
  penalty_amount: number
  driver_score: number | null
  reason: string
  buyer_concern: string | null
  due_diligence_flag: string | null
  remediation_action: string
  remediation_timeline: string | null
  remediation_effort: string | null
  multiple_recovery: number
}

interface ValueUnlock {
  id: string
  priority_rank: number
  title: string
  description: string | null
  action_type: string
  ebitda_impact: number
  multiple_impact: number
  ev_impact: number
  effort_level: string | null
  timeline: string | null
  is_locked: boolean
  is_preview: boolean
}

interface ShockReportData {
  report: {
    id: string
    generated_at: string
    owner_view: OwnerView
    buyer_view: BuyerView
    gap_analysis: GapAnalysis
    tier: 'below_avg' | 'avg' | 'above_avg'
    confidence_score: number
    data_quality: {
      qbo_data_range_start: string | null
      qbo_data_range_end: string | null
      transaction_count: number
      invoice_count: number
      expense_count: number
    }
    total_recoverable_value: number
  }
  ebitda_adjustments: EbitdaAdjustment[]
  multiple_penalties: MultiplePenalty[]
  value_unlocks: ValueUnlock[]
}

const DRIVER_LABELS: Record<string, { label: string; icon: string }> = {
  management_independence: { label: 'Management Independence', icon: '👔' },
  financial_records: { label: 'Financial Records', icon: '📊' },
  recurring_revenue: { label: 'Recurring Revenue', icon: '🔄' },
  operational_systems: { label: 'Operational Systems', icon: '⚙️' },
  customer_diversity: { label: 'Customer Diversity', icon: '👥' },
  market_outlook: { label: 'Market Outlook', icon: '📈' },
}

const CATEGORY_COLORS: Record<string, { bg: string; text: string; label: string }> = {
  accepted: { bg: 'bg-emerald-500/20', text: 'text-emerald-400', label: 'Buyer Accepts' },
  rejected: { bg: 'bg-red-500/20', text: 'text-red-400', label: 'Buyer Rejects' },
  partial: { bg: 'bg-amber-500/20', text: 'text-amber-400', label: 'Partial Accept' },
  needs_review: { bg: 'bg-blue-500/20', text: 'text-blue-400', label: 'Needs Review' },
}

const EFFORT_COLORS: Record<string, string> = {
  low: 'text-emerald-400',
  medium: 'text-amber-400',
  high: 'text-red-400',
}

interface ShockReportProps {
  accessToken: string
  isDemoMode?: boolean
  onStartTrial?: () => void
}

export function ShockReport({ accessToken, isDemoMode = false, onStartTrial }: ShockReportProps) {
  const [reportData, setReportData] = useState<ShockReportData | null>(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['gap']))

  const fetchLatestReport = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      // Demo mode - fetch from demo endpoint
      if (isDemoMode) {
        const response = await fetch('/api/demo/shock-report')
        const result = await response.json()
        if (!response.ok) {
          throw new Error(result.detail || 'Failed to fetch demo data')
        }
        setReportData(result)
        return
      }

      const { data: { user } } = await supabase.auth.getUser()
      const tenantId = user?.user_metadata?.tenant_id

      if (!tenantId) {
        setError('No tenant found. Please log in again.')
        return
      }

      const response = await fetch(`/api/valuation/shock-report/latest`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      })

      const result = await response.json()

      if (!response.ok) {
        if (result.error?.code === 'NOT_FOUND') {
          setReportData(null)
        } else {
          throw new Error(result.error?.message || 'Failed to fetch report')
        }
        return
      }

      if (result.success && result.data) {
        setReportData(result.data)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load shock report')
    } finally {
      setLoading(false)
    }
  }, [accessToken, isDemoMode])

  const generateReport = async () => {
    try {
      setGenerating(true)
      setError(null)

      const response = await fetch(`/api/valuation/shock-report`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
      })

      const result = await response.json()

      if (!response.ok) {
        throw new Error(result.error?.message || 'Failed to generate report')
      }

      // Refresh to get full report with related data
      await fetchLatestReport()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate shock report')
    } finally {
      setGenerating(false)
    }
  }

  const trackAnalytics = async (eventType: string, sectionName?: string) => {
    if (!reportData?.report.id) return

    try {
      await fetch(`/api/valuation/shock-report/${reportData.report.id}/analytics`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ event_type: eventType, section_name: sectionName }),
      })
    } catch {
      // Silent fail for analytics
    }
  }

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => {
      const next = new Set(prev)
      if (next.has(section)) {
        next.delete(section)
      } else {
        next.add(section)
        trackAnalytics('section_expanded', section)
      }
      return next
    })
  }

  useEffect(() => {
    void fetchLatestReport()
  }, [fetchLatestReport])

  const formatCurrency = (value: number): string =>
    new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value)

  const formatPercent = (value: number): string => `${value.toFixed(1)}%`

  const getTierConfig = (tier: string) => {
    switch (tier) {
      case 'above_avg':
        return { label: 'Above Average', color: 'emerald', multiple: '6.0x - 8.0x' }
      case 'avg':
        return { label: 'Average', color: 'blue', multiple: '4.0x - 5.5x' }
      case 'below_avg':
        return { label: 'Below Average', color: 'amber', multiple: '2.5x - 3.5x' }
      default:
        return { label: tier, color: 'slate', multiple: '2.5x - 3.5x' }
    }
  }

  if (loading) {
    return (
      <div className="min-h-[400px] flex items-center justify-center">
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
          Loading valuation shock report...
        </motion.div>
      </div>
    )
  }

  if (error) {
    return (
      <GlassCard variant="danger">
        <div className="flex items-center gap-3">
          <span className="text-2xl">⚠️</span>
          <div>
            <div className="font-semibold text-red-300">Error</div>
            <div className="text-sm text-red-400/80">{error}</div>
          </div>
        </div>
      </GlassCard>
    )
  }

  // No report - show generate CTA
  if (!reportData) {
    return (
      <GlassCard padding="lg" className="text-center">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <div className="text-6xl mb-6">💔</div>
          <h2 className="text-3xl font-bold mb-4 bg-gradient-to-r from-red-400 to-amber-400 bg-clip-text text-transparent">
            Are You Leaving Money on the Table?
          </h2>
          <p className="text-slate-400 mb-8 max-w-lg mx-auto">
            See the gap between what you think your business is worth and what buyers will actually pay.
            Our Valuation Shock Report analyzes your QuickBooks data to reveal the truth.
          </p>
          <motion.button
            onClick={() => void generateReport()}
            disabled={generating}
            className="bg-gradient-to-r from-emerald-500 to-emerald-400 hover:from-emerald-400 hover:to-emerald-300 text-black font-bold px-8 py-4 rounded-xl text-lg transition disabled:opacity-50"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {generating ? (
              <span className="flex items-center gap-2">
                <motion.span
                  className="w-5 h-5 border-2 border-black border-t-transparent rounded-full"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                />
                Analyzing Your Books...
              </span>
            ) : (
              'Generate My Shock Report'
            )}
          </motion.button>
          <p className="text-xs text-slate-500 mt-4">Takes about 30 seconds</p>
        </motion.div>
      </GlassCard>
    )
  }

  const { report, ebitda_adjustments, multiple_penalties, value_unlocks } = reportData
  const tierConfig = getTierConfig(report.tier)
  const buyerValuationMid = (report.buyer_view.valuation_low + report.buyer_view.valuation_high) / 2

  return (
    <div className="space-y-6">
      {/* Hero Section - The Shock */}
      <GlassCard padding="lg" glow variant="danger">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center"
        >
          <h1 className="text-2xl font-bold text-slate-300 mb-2">Valuation Shock Report</h1>
          <p className="text-sm text-slate-500 mb-8">
            Generated {new Date(report.generated_at).toLocaleDateString()}
          </p>

          {/* The Big Number */}
          <div className="relative">
            <motion.div
              initial={{ scale: 0.5, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.3, duration: 0.5 }}
              className="text-6xl md:text-7xl font-black text-red-500 mb-2"
            >
              -{formatPercent(report.gap_analysis.value_gap_percentage)}
            </motion.div>
            <div className="text-lg text-slate-400">Value Gap</div>
          </div>

          {/* Gap Breakdown */}
          <div className="grid grid-cols-2 gap-4 mt-8 max-w-2xl mx-auto">
            <div className="bg-slate-800/50 rounded-xl p-4">
              <div className="text-sm text-slate-400 mb-1">You Expect</div>
              <div className="text-2xl font-bold text-white">
                <AnimatedCurrency value={report.owner_view.expected_valuation} />
              </div>
              <div className="text-xs text-slate-500 mt-1">
                Based on {report.owner_view.expected_multiple}x multiple
              </div>
            </div>
            <div className="bg-red-950/30 border border-red-500/30 rounded-xl p-4">
              <div className="text-sm text-red-400 mb-1">Buyers Will Pay</div>
              <div className="text-2xl font-bold text-red-400">
                <AnimatedCurrency value={buyerValuationMid} />
              </div>
              <div className="text-xs text-slate-500 mt-1">
                {report.buyer_view.multiple_low}x - {report.buyer_view.multiple_high}x multiple
              </div>
            </div>
          </div>

          {/* The Dollar Gap */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="mt-8 bg-gradient-to-r from-red-950/50 to-amber-950/50 rounded-xl p-6 border border-red-500/20"
          >
            <div className="text-lg text-slate-400 mb-2">You&apos;re Leaving On The Table</div>
            <div className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-amber-400">
              <AnimatedCurrency value={report.gap_analysis.value_gap} />
            </div>
            <div className="text-sm text-slate-500 mt-2">
              But {formatCurrency(report.total_recoverable_value)} is recoverable
            </div>
          </motion.div>
        </motion.div>
      </GlassCard>

      {/* Your Tier Assessment */}
      <GlassCard padding="md">
        <div
          className="flex items-center justify-between cursor-pointer"
          onClick={() => toggleSection('tier')}
        >
          <div className="flex items-center gap-3">
            <span className="text-2xl">🏆</span>
            <div>
              <h3 className="font-semibold">Your Tier: {tierConfig.label}</h3>
              <p className="text-sm text-slate-400">Market multiple range: {tierConfig.multiple}</p>
            </div>
          </div>
          <motion.span
            animate={{ rotate: expandedSections.has('tier') ? 180 : 0 }}
            className="text-slate-400"
          >
            ▼
          </motion.span>
        </div>

        <AnimatePresence>
          {expandedSections.has('tier') && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="overflow-hidden"
            >
              <div className="mt-4 pt-4 border-t border-slate-700">
                <div className="grid grid-cols-3 gap-4 text-center">
                  {['below_avg', 'avg', 'above_avg'].map((t) => {
                    const config = getTierConfig(t)
                    const isActive = t === report.tier
                    return (
                      <div
                        key={t}
                        className={`p-4 rounded-lg ${
                          isActive
                            ? 'bg-emerald-500/20 border border-emerald-500/50'
                            : 'bg-slate-800/50'
                        }`}
                      >
                        <div className={`text-sm ${isActive ? 'text-emerald-400' : 'text-slate-400'}`}>
                          {config.label}
                        </div>
                        <div className={`text-lg font-bold ${isActive ? 'text-white' : 'text-slate-500'}`}>
                          {config.multiple}
                        </div>
                        {isActive && <div className="text-xs text-emerald-400 mt-1">← You are here</div>}
                      </div>
                    )
                  })}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </GlassCard>

      {/* EBITDA Haircut Section */}
      <GlassCard padding="md">
        <div
          className="flex items-center justify-between cursor-pointer"
          onClick={() => toggleSection('ebitda')}
        >
          <div className="flex items-center gap-3">
            <span className="text-2xl">✂️</span>
            <div>
              <h3 className="font-semibold">EBITDA Haircut</h3>
              <p className="text-sm text-slate-400">
                {formatCurrency(report.gap_analysis.ebitda_haircut)} in rejected add-backs
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="text-sm text-slate-400">Defensible EBITDA</div>
              <div className="font-bold text-emerald-400">
                {formatCurrency(report.buyer_view.defensible_ebitda)}
              </div>
            </div>
            <motion.span
              animate={{ rotate: expandedSections.has('ebitda') ? 180 : 0 }}
              className="text-slate-400"
            >
              ▼
            </motion.span>
          </div>
        </div>

        <AnimatePresence>
          {expandedSections.has('ebitda') && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="overflow-hidden"
            >
              <div className="mt-4 pt-4 border-t border-slate-700 space-y-3">
                {ebitda_adjustments.length === 0 ? (
                  <p className="text-slate-500 text-center py-4">No adjustments analyzed yet</p>
                ) : (
                  ebitda_adjustments.map((adj) => {
                    const catConfig = CATEGORY_COLORS[adj.category]
                    return (
                      <div
                        key={adj.id}
                        className="flex items-start justify-between p-3 bg-slate-800/50 rounded-lg"
                      >
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className={`text-xs px-2 py-0.5 rounded ${catConfig.bg} ${catConfig.text}`}>
                              {catConfig.label}
                            </span>
                            <span className="text-xs text-slate-500">{adj.type.replace('_', ' ')}</span>
                          </div>
                          <p className="text-sm text-white">{adj.description}</p>
                          {adj.buyer_concern && (
                            <p className="text-xs text-red-400/70 mt-1">⚠️ {adj.buyer_concern}</p>
                          )}
                          {adj.is_recoverable && adj.remediation_action && (
                            <p className="text-xs text-emerald-400/70 mt-1">
                              ✓ Fix: {adj.remediation_action}
                            </p>
                          )}
                        </div>
                        <div className="text-right ml-4">
                          <div className={`font-bold ${adj.category === 'rejected' ? 'text-red-400' : 'text-white'}`}>
                            {adj.category === 'rejected' ? '-' : ''}{formatCurrency(adj.amount)}
                          </div>
                          {adj.accepted_amount > 0 && adj.accepted_amount < adj.amount && (
                            <div className="text-xs text-emerald-400">
                              Accepted: {formatCurrency(adj.accepted_amount)}
                            </div>
                          )}
                        </div>
                      </div>
                    )
                  })
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </GlassCard>

      {/* Multiple Penalties Section */}
      <GlassCard padding="md">
        <div
          className="flex items-center justify-between cursor-pointer"
          onClick={() => toggleSection('multiple')}
        >
          <div className="flex items-center gap-3">
            <span className="text-2xl">📉</span>
            <div>
              <h3 className="font-semibold">Multiple Penalties</h3>
              <p className="text-sm text-slate-400">
                {report.gap_analysis.multiple_penalty.toFixed(1)}x reduction from baseline
              </p>
            </div>
          </div>
          <motion.span
            animate={{ rotate: expandedSections.has('multiple') ? 180 : 0 }}
            className="text-slate-400"
          >
            ▼
          </motion.span>
        </div>

        <AnimatePresence>
          {expandedSections.has('multiple') && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="overflow-hidden"
            >
              <div className="mt-4 pt-4 border-t border-slate-700 space-y-3">
                {multiple_penalties.length === 0 ? (
                  <p className="text-slate-500 text-center py-4">No penalties calculated yet</p>
                ) : (
                  multiple_penalties.map((pen) => {
                    const driverMeta = DRIVER_LABELS[pen.driver_key] || { label: pen.driver_key, icon: '❓' }
                    const effortColor = EFFORT_COLORS[pen.remediation_effort || 'medium'] || 'text-slate-400'
                    return (
                      <div
                        key={pen.id}
                        className="p-3 bg-slate-800/50 rounded-lg"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex items-start gap-3">
                            <span className="text-2xl">{driverMeta.icon}</span>
                            <div>
                              <div className="font-medium text-white">{driverMeta.label}</div>
                              <div className="text-sm text-red-400 mt-1">"{pen.reason}"</div>
                              {pen.buyer_concern && (
                                <div className="text-xs text-slate-400 mt-2">
                                  <span className="text-slate-500">Buyer concern:</span> {pen.buyer_concern}
                                </div>
                              )}
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-xl font-bold text-red-400">{pen.penalty_amount.toFixed(1)}x</div>
                            <div className="text-xs text-slate-500">penalty</div>
                          </div>
                        </div>
                        <div className="mt-3 pt-3 border-t border-slate-700/50 flex items-center justify-between">
                          <div className="text-xs">
                            <span className="text-slate-500">Fix: </span>
                            <span className="text-slate-300">{pen.remediation_action}</span>
                          </div>
                          <div className="flex items-center gap-3 text-xs">
                            <span className={effortColor}>{pen.remediation_effort} effort</span>
                            <span className="text-emerald-400">+{pen.multiple_recovery.toFixed(1)}x recovery</span>
                          </div>
                        </div>
                      </div>
                    )
                  })
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </GlassCard>

      {/* Value Unlocks Section - The Paywall Tease */}
      <GlassCard padding="md" variant="success" glow>
        <div
          className="flex items-center justify-between cursor-pointer"
          onClick={() => toggleSection('unlocks')}
        >
          <div className="flex items-center gap-3">
            <span className="text-2xl">🔓</span>
            <div>
              <h3 className="font-semibold text-emerald-400">Value Recovery Roadmap</h3>
              <p className="text-sm text-slate-400">
                {value_unlocks.length} actions to recover {formatCurrency(report.total_recoverable_value)}
              </p>
            </div>
          </div>
          <motion.span
            animate={{ rotate: expandedSections.has('unlocks') ? 180 : 0 }}
            className="text-slate-400"
          >
            ▼
          </motion.span>
        </div>

        <AnimatePresence>
          {expandedSections.has('unlocks') && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="overflow-hidden"
            >
              <div className="mt-4 pt-4 border-t border-emerald-500/30 space-y-3">
                {value_unlocks.slice(0, 3).map((unlock, idx) => (
                  <motion.div
                    key={unlock.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.1 }}
                    className={`p-4 rounded-lg ${
                      unlock.is_locked ? 'bg-slate-800/50' : 'bg-emerald-950/30 border border-emerald-500/30'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 bg-emerald-500/20 rounded-full flex items-center justify-center text-emerald-400 font-bold">
                          {unlock.priority_rank}
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-white">{unlock.title}</span>
                            {unlock.is_locked && <span className="text-xs">🔒</span>}
                          </div>
                          {unlock.is_preview && !unlock.is_locked && (
                            <p className="text-sm text-slate-400 mt-1">{unlock.description}</p>
                          )}
                          {unlock.is_locked && (
                            <p className="text-sm text-slate-500 mt-1 italic">
                              Unlock to see action details...
                            </p>
                          )}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-bold text-emerald-400">
                          +{formatCurrency(unlock.ev_impact)}
                        </div>
                        <div className="text-xs text-slate-500">EV impact</div>
                      </div>
                    </div>
                  </motion.div>
                ))}

                {value_unlocks.length > 3 && (
                  <div className="text-center text-sm text-slate-500 py-2">
                    + {value_unlocks.length - 3} more actions locked
                  </div>
                )}

                {/* CTA */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                  className="mt-6 pt-6 border-t border-emerald-500/30 text-center"
                >
                  <h4 className="text-lg font-semibold text-white mb-2">
                    Ready to Recover {formatCurrency(report.total_recoverable_value)}?
                  </h4>
                  <p className="text-sm text-slate-400 mb-4">
                    Start your 14-day free trial to unlock all value recovery actions
                  </p>
                  <motion.button
                    onClick={() => {
                      trackAnalytics('trial_cta_clicked')
                      onStartTrial?.()
                    }}
                    className="bg-gradient-to-r from-emerald-500 to-emerald-400 hover:from-emerald-400 hover:to-emerald-300 text-black font-bold px-8 py-3 rounded-xl transition"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    Start Free Trial
                  </motion.button>
                </motion.div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </GlassCard>

      {/* Data Quality Footer */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          label="Confidence Score"
          value={`${report.confidence_score}%`}
          icon="🎯"
        />
        <MetricCard
          label="Transactions Analyzed"
          value={report.data_quality.transaction_count.toLocaleString()}
          icon="📝"
        />
        <MetricCard
          label="Invoices"
          value={report.data_quality.invoice_count.toLocaleString()}
          icon="📄"
        />
        <MetricCard
          label="Expenses"
          value={report.data_quality.expense_count.toLocaleString()}
          icon="💳"
        />
      </div>

      {/* Regenerate Button */}
      <div className="text-center">
        <motion.button
          onClick={() => void generateReport()}
          disabled={generating}
          className="text-sm text-slate-500 hover:text-slate-300 transition"
          whileHover={{ scale: 1.02 }}
        >
          {generating ? 'Regenerating...' : 'Regenerate Report'}
        </motion.button>
      </div>
    </div>
  )
}
