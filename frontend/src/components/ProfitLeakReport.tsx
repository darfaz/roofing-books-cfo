import { useEffect, useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { supabase } from '../lib/supabase'
import { GlassCard, MetricCard } from './ui/GlassCard'
import { AnimatedCurrency, AnimatedPercentage } from './ui/AnimatedNumber'

interface OverheadAnalysis {
  period: {
    start: string
    end: string
    months: number
  }
  overhead: {
    total: number
    monthly_average: number
    by_category: Record<string, number>
    monthly_trend: Record<string, Record<string, number>>
    transaction_count: number
  }
  job_costs: {
    total: number
    monthly_average: number
    by_category: Record<string, number>
    transaction_count: number
  }
  revenue: {
    total: number
    monthly_average: number
  }
  profitability: {
    gross_margin: number
    gross_margin_pct: string
    gross_profit_monthly: number
  }
  break_even: {
    current_margin: {
      margin: number
      monthly: number
      annual: number
    }
    scenarios: Record<string, {
      margin: number
      monthly_break_even: number
      annual_break_even: number
      is_current: boolean
    }>
  }
  mixed_expenses: {
    total: number
    count: number
    note: string
  }
  confidence: {
    overhead_avg: number
    job_cost_avg: number
  }
}

const CATEGORY_LABELS: Record<string, { label: string; icon: string; color: string }> = {
  professional_fees: { label: 'Professional Fees', icon: '👔', color: 'text-blue-400' },
  marketing: { label: 'Marketing & Advertising', icon: '📢', color: 'text-purple-400' },
  office: { label: 'Office & Admin', icon: '🏢', color: 'text-slate-400' },
  utilities: { label: 'Utilities', icon: '⚡', color: 'text-yellow-400' },
  insurance: { label: 'Insurance', icon: '🛡️', color: 'text-green-400' },
  depreciation: { label: 'Depreciation', icon: '📉', color: 'text-gray-400' },
  payroll: { label: 'Payroll & Taxes', icon: '💵', color: 'text-emerald-400' },
  other_overhead: { label: 'Other Overhead', icon: '📋', color: 'text-slate-500' },
  materials: { label: 'Materials & Supplies', icon: '🧱', color: 'text-orange-400' },
  direct_labor: { label: 'Direct Labor', icon: '👷', color: 'text-blue-400' },
  equipment: { label: 'Equipment Rental', icon: '🚜', color: 'text-amber-400' },
  subcontractors: { label: 'Subcontractors', icon: '🤝', color: 'text-indigo-400' },
  disposal: { label: 'Disposal & Hauling', icon: '🚛', color: 'text-red-400' },
  permits: { label: 'Permits & Inspections', icon: '📜', color: 'text-cyan-400' },
  other_job_cost: { label: 'Other Job Costs', icon: '🔧', color: 'text-slate-500' },
}

const HEALTH_STATUS_CONFIG = {
  HEALTHY: { label: 'Healthy', color: 'emerald', icon: '✅', description: 'Your gross margin is strong' },
  NEEDS_ATTENTION: { label: 'Needs Attention', color: 'amber', icon: '⚠️', description: 'Margin is tight - review costs' },
  CRITICAL: { label: 'Critical', color: 'red', icon: '🚨', description: 'Urgent cost review needed' },
}

interface ProfitLeakReportProps {
  accessToken: string
  isDemoMode?: boolean
}

interface ProfitLeak {
  category: string
  issue: string
  current_ratio: number
  benchmark: number
  impact: string
  severity: 'high' | 'medium' | 'low'
  recommendation: string
}

export function ProfitLeakReport({ accessToken, isDemoMode = false }: ProfitLeakReportProps) {
  const [analysis, setAnalysis] = useState<OverheadAnalysis | null>(null)
  const [profitLeaks, setProfitLeaks] = useState<ProfitLeak[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [tenantId, setTenantId] = useState<string | null>(null)
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['summary', 'overhead', 'leaks']))

  const fetchAnalysis = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      // Demo mode - use simulated data
      if (isDemoMode) {
        // Use hardcoded demo data that matches the OverheadAnalysis format
        const demoAnalysis: OverheadAnalysis = {
          period: {
            start: '2024-12-01',
            end: '2025-11-30',
            months: 12,
          },
          overhead: {
            total: 546000,
            monthly_average: 45500,
            by_category: {
              payroll: 216000,
              insurance: 84000,
              office: 72000,
              professional_fees: 48000,
              marketing: 60000,
              utilities: 36000,
              other_overhead: 30000,
            },
            monthly_trend: {},
            transaction_count: 847,
          },
          job_costs: {
            total: 2730000,
            monthly_average: 227500,
            by_category: {
              materials: 1225000,
              direct_labor: 630000,
              subcontractors: 455000,
              equipment: 245000,
              disposal: 105000,
              permits: 70000,
            },
            transaction_count: 1523,
          },
          revenue: {
            total: 3500000,
            monthly_average: 291667,
          },
          profitability: {
            gross_margin: 0.22,
            gross_margin_pct: '22%',
            gross_profit_monthly: 64167,
          },
          break_even: {
            current_margin: {
              margin: 0.22,
              monthly: 206818,
              annual: 2481818,
            },
            scenarios: {
              '15%': { margin: 0.15, monthly_break_even: 303333, annual_break_even: 3640000, is_current: false },
              '20%': { margin: 0.20, monthly_break_even: 227500, annual_break_even: 2730000, is_current: false },
              '25%': { margin: 0.25, monthly_break_even: 182000, annual_break_even: 2184000, is_current: false },
              '30%': { margin: 0.30, monthly_break_even: 151667, annual_break_even: 1820000, is_current: false },
              '35%': { margin: 0.35, monthly_break_even: 130000, annual_break_even: 1560000, is_current: false },
            },
          },
          mixed_expenses: {
            total: 45000,
            count: 23,
            note: 'Personal expenses mixed with business',
          },
          confidence: {
            overhead_avg: 0.85,
            job_cost_avg: 0.92,
          },
        }
        setAnalysis(demoAnalysis)

        // Demo profit leaks data
        setProfitLeaks([
          {
            category: 'Gross Margin',
            issue: 'Gross margin is below the healthy threshold for roofing contractors',
            current_ratio: 0.22,
            benchmark: 0.35,
            impact: '13% below target',
            severity: 'high' as const,
            recommendation: 'Review pricing strategy and job costing. Consider increasing markup on materials and labor.',
          },
          {
            category: 'Marketing Spend',
            issue: 'Marketing costs are slightly elevated compared to industry average',
            current_ratio: 0.017,
            benchmark: 0.05,
            impact: 'Within acceptable range',
            severity: 'low' as const,
            recommendation: 'Monitor ROI on marketing channels. Focus on highest-converting lead sources.',
          },
        ])
        return
      }

      const { data: { user } } = await supabase.auth.getUser()
      const tid = user?.user_metadata?.tenant_id
      setTenantId(tid)

      if (!tid) {
        setError('No tenant found. Please log in again.')
        return
      }

      // Try the new P&L analytics endpoint first, fallback to overhead summary
      let response = await fetch(`/api/analytics/pnl?tenant_id=${tid}`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      })

      let result = await response.json()

      // If new endpoint succeeded, transform to OverheadAnalysis format
      if (response.ok && result.success && result.data) {
        const pnlData = result.data
        const analysis: OverheadAnalysis = {
          period: {
            start: pnlData.period?.start || '2024-01-01',
            end: pnlData.period?.end || '2024-12-31',
            months: 12,
          },
          overhead: {
            total: pnlData.expense_breakdown?.overhead?.total || 0,
            monthly_average: pnlData.monthly?.overhead || 0,
            by_category: pnlData.expense_breakdown?.overhead?.items || {},
            monthly_trend: {},
            transaction_count: 0,
          },
          job_costs: {
            total: pnlData.summary?.total_cogs || 0,
            monthly_average: (pnlData.summary?.total_cogs || 0) / 12,
            by_category: pnlData.expense_breakdown?.cogs?.items || {},
            transaction_count: 0,
          },
          revenue: {
            total: pnlData.summary?.total_revenue || 0,
            monthly_average: pnlData.monthly?.revenue || 0,
          },
          profitability: {
            gross_margin: (pnlData.summary?.gross_margin_pct || 0) / 100,
            gross_margin_pct: `${pnlData.summary?.gross_margin_pct || 0}%`,
            gross_profit_monthly: pnlData.monthly?.net_income || 0,
          },
          break_even: pnlData.break_even || {
            current_margin: { margin: 0, monthly: 0, annual: 0 },
            scenarios: {},
          },
          mixed_expenses: {
            total: 0,
            count: 0,
            note: '',
          },
          confidence: {
            overhead_avg: 0.9,
            job_cost_avg: 0.9,
          },
        }
        setAnalysis(analysis)

        // Also fetch profit leaks if available
        if (pnlData.profit_leaks) {
          setProfitLeaks(pnlData.profit_leaks)
        }
        return
      }

      // Fallback to old overhead summary endpoint
      response = await fetch(`/api/qbo/overhead/summary?tenant_id=${tid}`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      })

      result = await response.json()

      if (!response.ok) {
        throw new Error(result.detail || result.error?.message || 'Failed to fetch analysis')
      }

      setAnalysis(result.data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load profit leak report')
    } finally {
      setLoading(false)
    }
  }, [accessToken, isDemoMode])

  useEffect(() => {
    void fetchAnalysis()
  }, [fetchAnalysis])

  // Refetch when demo mode changes
  useEffect(() => {
    void fetchAnalysis()
  }, [isDemoMode]) // eslint-disable-line react-hooks/exhaustive-deps

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => {
      const next = new Set(prev)
      if (next.has(section)) {
        next.delete(section)
      } else {
        next.add(section)
      }
      return next
    })
  }

  const formatCurrency = (value: number): string =>
    new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value)

  const getHealthStatus = (grossMargin: number) => {
    if (grossMargin > 0.25) return HEALTH_STATUS_CONFIG.HEALTHY
    if (grossMargin > 0.15) return HEALTH_STATUS_CONFIG.NEEDS_ATTENTION
    return HEALTH_STATUS_CONFIG.CRITICAL
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
          Analyzing your expenses...
        </motion.div>
      </div>
    )
  }

  if (error && !isDemoMode) {
    const needsReconnect = error.toLowerCase().includes('reconnect') || error.toLowerCase().includes('expired')

    const handleReconnectQbo = () => {
      if (!tenantId) return
      const returnUrl = `${window.location.origin}${window.location.pathname}`
      window.location.href = `/auth/qbo/connect?tenant_id=${tenantId}&return_url=${encodeURIComponent(returnUrl)}`
    }

    return (
      <div className="space-y-4">
        <GlassCard variant="danger">
          <div className="flex items-center gap-3">
            <span className="text-2xl">⚠️</span>
            <div>
              <div className="font-semibold text-red-300">Error Loading Report</div>
              <div className="text-sm text-red-400/80">{error}</div>
            </div>
          </div>
          <div className="mt-4 flex gap-3 flex-wrap">
            {needsReconnect && tenantId ? (
              <motion.button
                onClick={handleReconnectQbo}
                className="bg-[#2CA01C] hover:bg-[#3AB82A] text-white font-medium px-4 py-2 rounded-lg text-sm transition flex items-center gap-2"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                </svg>
                Reconnect QuickBooks
              </motion.button>
            ) : (
              <motion.button
                onClick={() => void fetchAnalysis()}
                className="bg-red-500/20 hover:bg-red-500/30 text-red-300 px-4 py-2 rounded-lg text-sm transition"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                Try Again
              </motion.button>
            )}
            <motion.button
              onClick={() => window.location.reload()}
              className="bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 px-4 py-2 rounded-lg text-sm transition flex items-center gap-2"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              🔄 Reload Page
            </motion.button>
          </div>
        </GlassCard>
        <p className="text-center text-sm text-slate-500">
          No QuickBooks connected? Return to login and click "View Interactive Demo" to see sample data.
        </p>
      </div>
    )
  }

  if (!analysis) {
    return (
      <GlassCard padding="lg" className="text-center">
        <div className="text-5xl mb-4">📊</div>
        <h2 className="text-2xl font-bold mb-2">No Data Available</h2>
        <p className="text-slate-400">
          Connect QuickBooks and sync transactions to see your profit leak analysis.
        </p>
      </GlassCard>
    )
  }

  const healthStatus = getHealthStatus(analysis.profitability.gross_margin)

  return (
    <div className="space-y-6">
      {/* Demo Mode Banner */}
      {isDemoMode && (
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="bg-amber-500/20 border border-amber-500/50 text-amber-300 px-4 py-2 rounded-lg text-sm flex items-center gap-2"
        >
          <span className="text-lg">🎭</span>
          <span><strong>Demo Mode:</strong> Apex Roofing Solutions - $3.5M roofing contractor</span>
        </motion.div>
      )}

      {/* Hero Section - Break-Even */}
      <GlassCard padding="lg" glow>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center"
        >
          <div className="flex items-center justify-center gap-2 mb-2">
            <span className="text-2xl">{healthStatus.icon}</span>
            <span className={`text-${healthStatus.color}-400 font-semibold`}>
              {healthStatus.label}
            </span>
          </div>
          <h1 className="text-2xl font-bold text-slate-300 mb-1">Stop the Profit Leaks</h1>
          <p className="text-sm text-slate-500 mb-8">{healthStatus.description}</p>

          {/* The Big Number - Break-Even */}
          <div className="relative mb-8">
            <div className="text-sm text-slate-400 mb-2">Monthly Break-Even Point</div>
            <motion.div
              initial={{ scale: 0.5, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.2, duration: 0.5 }}
              className="text-5xl md:text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400"
            >
              <AnimatedCurrency value={analysis.break_even.current_margin.monthly} />
            </motion.div>
            <div className="text-sm text-slate-500 mt-2">
              in revenue to cover overhead at {analysis.profitability.gross_margin_pct} margin
            </div>
          </div>

          {/* Key Metrics Row */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-slate-800/50 rounded-xl p-4">
              <div className="text-xs text-slate-400 mb-1">Monthly Overhead</div>
              <div className="text-xl font-bold text-red-400">
                <AnimatedCurrency value={analysis.overhead.monthly_average} />
              </div>
            </div>
            <div className="bg-slate-800/50 rounded-xl p-4">
              <div className="text-xs text-slate-400 mb-1">Monthly Job Costs</div>
              <div className="text-xl font-bold text-amber-400">
                <AnimatedCurrency value={analysis.job_costs.monthly_average} />
              </div>
            </div>
            <div className="bg-slate-800/50 rounded-xl p-4">
              <div className="text-xs text-slate-400 mb-1">Gross Margin</div>
              <div className="text-xl font-bold text-emerald-400">
                <AnimatedPercentage value={analysis.profitability.gross_margin * 100} />
              </div>
            </div>
            <div className="bg-slate-800/50 rounded-xl p-4">
              <div className="text-xs text-slate-400 mb-1">Monthly Revenue</div>
              <div className="text-xl font-bold text-blue-400">
                <AnimatedCurrency value={analysis.revenue.monthly_average} />
              </div>
            </div>
          </div>
        </motion.div>
      </GlassCard>

      {/* Break-Even Scenarios */}
      <GlassCard padding="md">
        <div
          className="flex items-center justify-between cursor-pointer"
          onClick={() => toggleSection('scenarios')}
        >
          <div className="flex items-center gap-3">
            <span className="text-2xl">🎯</span>
            <div>
              <h3 className="font-semibold">Break-Even Scenarios</h3>
              <p className="text-sm text-slate-400">What if your margin changes?</p>
            </div>
          </div>
          <motion.span
            animate={{ rotate: expandedSections.has('scenarios') ? 180 : 0 }}
            className="text-slate-400"
          >
            ▼
          </motion.span>
        </div>

        <AnimatePresence>
          {expandedSections.has('scenarios') && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="overflow-hidden"
            >
              <div className="mt-4 pt-4 border-t border-slate-700">
                <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                  {Object.entries(analysis.break_even.scenarios).map(([label, scenario]) => (
                    <div
                      key={label}
                      className={`p-3 rounded-lg text-center ${
                        Math.abs(scenario.margin - analysis.profitability.gross_margin) < 0.05
                          ? 'bg-emerald-500/20 border border-emerald-500/50'
                          : 'bg-slate-800/50'
                      }`}
                    >
                      <div className="text-xs text-slate-400 mb-1">{label} Margin</div>
                      <div className="text-lg font-bold text-white">
                        {formatCurrency(scenario.monthly_break_even)}
                      </div>
                      <div className="text-xs text-slate-500">/month</div>
                    </div>
                  ))}
                </div>
                <p className="text-xs text-slate-500 mt-4 text-center">
                  Your current margin of {analysis.profitability.gross_margin_pct} is highlighted
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </GlassCard>

      {/* Overhead Breakdown */}
      <GlassCard padding="md">
        <div
          className="flex items-center justify-between cursor-pointer"
          onClick={() => toggleSection('overhead')}
        >
          <div className="flex items-center gap-3">
            <span className="text-2xl">🏢</span>
            <div>
              <h3 className="font-semibold">Overhead Breakdown</h3>
              <p className="text-sm text-slate-400">
                {formatCurrency(analysis.overhead.total)} total ({analysis.overhead.transaction_count} transactions)
              </p>
            </div>
          </div>
          <motion.span
            animate={{ rotate: expandedSections.has('overhead') ? 180 : 0 }}
            className="text-slate-400"
          >
            ▼
          </motion.span>
        </div>

        <AnimatePresence>
          {expandedSections.has('overhead') && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="overflow-hidden"
            >
              <div className="mt-4 pt-4 border-t border-slate-700 space-y-2">
                {Object.entries(analysis.overhead.by_category)
                  .sort(([, a], [, b]) => b - a)
                  .map(([category, amount]) => {
                    const meta = CATEGORY_LABELS[category] || { label: category, icon: '📋', color: 'text-slate-400' }
                    const percentage = (amount / analysis.overhead.total) * 100
                    return (
                      <div key={category} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                        <div className="flex items-center gap-3">
                          <span className="text-xl">{meta.icon}</span>
                          <div>
                            <div className="font-medium text-white">{meta.label}</div>
                            <div className="text-xs text-slate-500">{percentage.toFixed(1)}% of overhead</div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className={`font-bold ${meta.color}`}>{formatCurrency(amount)}</div>
                        </div>
                      </div>
                    )
                  })}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </GlassCard>

      {/* Job Costs Breakdown */}
      <GlassCard padding="md">
        <div
          className="flex items-center justify-between cursor-pointer"
          onClick={() => toggleSection('jobcosts')}
        >
          <div className="flex items-center gap-3">
            <span className="text-2xl">🔧</span>
            <div>
              <h3 className="font-semibold">Job Cost Breakdown</h3>
              <p className="text-sm text-slate-400">
                {formatCurrency(analysis.job_costs.total)} total ({analysis.job_costs.transaction_count} transactions)
              </p>
            </div>
          </div>
          <motion.span
            animate={{ rotate: expandedSections.has('jobcosts') ? 180 : 0 }}
            className="text-slate-400"
          >
            ▼
          </motion.span>
        </div>

        <AnimatePresence>
          {expandedSections.has('jobcosts') && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="overflow-hidden"
            >
              <div className="mt-4 pt-4 border-t border-slate-700 space-y-2">
                {Object.entries(analysis.job_costs.by_category)
                  .sort(([, a], [, b]) => b - a)
                  .map(([category, amount]) => {
                    const meta = CATEGORY_LABELS[category] || { label: category, icon: '🔧', color: 'text-slate-400' }
                    const percentage = (amount / analysis.job_costs.total) * 100
                    return (
                      <div key={category} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                        <div className="flex items-center gap-3">
                          <span className="text-xl">{meta.icon}</span>
                          <div>
                            <div className="font-medium text-white">{meta.label}</div>
                            <div className="text-xs text-slate-500">{percentage.toFixed(1)}% of job costs</div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className={`font-bold ${meta.color}`}>{formatCurrency(amount)}</div>
                        </div>
                      </div>
                    )
                  })}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </GlassCard>

      {/* Mixed Expenses - Needs Review */}
      {analysis.mixed_expenses.count > 0 && (
        <GlassCard padding="md" variant="warning">
          <div
            className="flex items-center justify-between cursor-pointer"
            onClick={() => toggleSection('mixed')}
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl">⚠️</span>
              <div>
                <h3 className="font-semibold text-amber-400">Expenses Needing Review</h3>
                <p className="text-sm text-slate-400">
                  {analysis.mixed_expenses.count} expenses totaling {formatCurrency(analysis.mixed_expenses.total)}
                </p>
              </div>
            </div>
            <motion.span
              animate={{ rotate: expandedSections.has('mixed') ? 180 : 0 }}
              className="text-slate-400"
            >
              ▼
            </motion.span>
          </div>

          <AnimatePresence>
            {expandedSections.has('mixed') && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="overflow-hidden"
              >
                <div className="mt-4 pt-4 border-t border-amber-500/30">
                  <p className="text-sm text-slate-400 mb-4">
                    These expenses couldn't be automatically classified as overhead or job costs.
                    Review them to improve your break-even accuracy.
                  </p>
                  <div className="bg-amber-950/30 rounded-lg p-4 text-center">
                    <div className="text-3xl font-bold text-amber-400 mb-1">
                      {formatCurrency(analysis.mixed_expenses.total)}
                    </div>
                    <div className="text-sm text-slate-400">
                      could be misclassified - review for accuracy
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </GlassCard>
      )}

      {/* Profit Leaks - Detected Issues */}
      {profitLeaks.length > 0 && (
        <GlassCard padding="md" variant="danger">
          <div
            className="flex items-center justify-between cursor-pointer"
            onClick={() => toggleSection('leaks')}
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl">🚨</span>
              <div>
                <h3 className="font-semibold text-red-400">Profit Leaks Detected</h3>
                <p className="text-sm text-slate-400">
                  {profitLeaks.length} issue{profitLeaks.length !== 1 ? 's' : ''} found compared to industry benchmarks
                </p>
              </div>
            </div>
            <motion.span
              animate={{ rotate: expandedSections.has('leaks') ? 180 : 0 }}
              className="text-slate-400"
            >
              ▼
            </motion.span>
          </div>

          <AnimatePresence>
            {expandedSections.has('leaks') && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="overflow-hidden"
              >
                <div className="mt-4 pt-4 border-t border-red-500/30 space-y-3">
                  {profitLeaks.map((leak, index) => {
                    const severityColors = {
                      high: 'bg-red-500/20 border-red-500/50 text-red-300',
                      medium: 'bg-amber-500/20 border-amber-500/50 text-amber-300',
                      low: 'bg-yellow-500/20 border-yellow-500/50 text-yellow-300',
                    }
                    const severityIcons = {
                      high: '🔴',
                      medium: '🟡',
                      low: '🟢',
                    }
                    return (
                      <div
                        key={index}
                        className={`p-4 rounded-lg border ${severityColors[leak.severity]}`}
                      >
                        <div className="flex items-start gap-3">
                          <span className="text-lg">{severityIcons[leak.severity]}</span>
                          <div className="flex-1">
                            <div className="flex items-center justify-between mb-1">
                              <span className="font-semibold">{leak.category}</span>
                              <span className="text-xs px-2 py-0.5 rounded bg-slate-800/50 text-slate-400 uppercase">
                                {leak.severity}
                              </span>
                            </div>
                            <p className="text-sm mb-2">{leak.issue}</p>
                            <div className="flex gap-4 text-xs text-slate-400 mb-2">
                              <span>Current: {(leak.current_ratio * 100).toFixed(1)}%</span>
                              <span>Benchmark: {(leak.benchmark * 100).toFixed(1)}%</span>
                              <span className="text-red-400 font-medium">{leak.impact}</span>
                            </div>
                            <p className="text-xs text-slate-300 bg-slate-800/50 rounded p-2">
                              💡 {leak.recommendation}
                            </p>
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </GlassCard>
      )}

      {/* Confidence Score Footer */}
      <div className="grid grid-cols-2 gap-4">
        <MetricCard
          label="Overhead Classification Confidence"
          value={`${(analysis.confidence.overhead_avg * 100).toFixed(0)}%`}
          icon="🎯"
        />
        <MetricCard
          label="Job Cost Classification Confidence"
          value={`${(analysis.confidence.job_cost_avg * 100).toFixed(0)}%`}
          icon="🎯"
        />
      </div>

      {/* Refresh Button */}
      <div className="text-center">
        <motion.button
          onClick={() => void fetchAnalysis()}
          className="text-sm text-slate-500 hover:text-slate-300 transition"
          whileHover={{ scale: 1.02 }}
        >
          Refresh Analysis
        </motion.button>
      </div>
    </div>
  )
}
