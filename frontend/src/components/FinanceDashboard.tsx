import { useEffect, useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import {
  Area,
  AreaChart,
  ResponsiveContainer,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  Cell,
} from 'recharts'
import { supabase } from '../lib/supabase'
import { GlassCard, MetricCard } from './ui/GlassCard'
import { AnimatedCurrency } from './ui/AnimatedNumber'

// Types
interface CashForecast {
  forecast_date: string
  scenario: string
  starting_cash: number
  ending_cash: number
  min_cash: number
  min_cash_week: number
  runway_weeks: number
  ar_total: number
  ap_total: number
  summary: {
    total_inflows: number
    total_outflows: number
    net_change: number
  }
  weekly_forecast: WeeklyForecast[]
}

interface WeeklyForecast {
  week_number: number
  week_start: string
  week_end: string
  starting_cash: number
  ending_cash: number
  net_cash_flow: number
  inflows: { collections: number; total: number }
  outflows: { ap_payments: number; recurring_expenses: number; total: number }
}

interface CashAlertStatus {
  status: 'healthy' | 'good' | 'caution' | 'critical'
  color: 'green' | 'yellow' | 'red'
  message: string
  runway_weeks: number
  current_cash: number
  min_projected_cash: number
  min_cash_week: number
  recommendations: string[]
}

interface APAging {
  aging: {
    current: number
    '1-30': number
    '31-60': number
    '61-90': number
    '90+': number
  }
  total: number
  overdue: number
  overdue_pct: number
}

interface BudgetVariance {
  period: string
  categories: {
    category: string
    budget: number
    actual: number
    variance: number
    variance_pct: number
    status: 'under' | 'over' | 'on_track'
  }[]
  totals: {
    budget: number
    actual: number
    variance: number
    variance_pct: number
  }
}

interface FinanceDashboardProps {
  accessToken: string
}

export function FinanceDashboard({ accessToken }: FinanceDashboardProps) {
  const [cashAlert, setCashAlert] = useState<CashAlertStatus | null>(null)
  const [allScenarios, setAllScenarios] = useState<{
    base: CashForecast
    optimistic: CashForecast
    pessimistic: CashForecast
  } | null>(null)
  const [apAging, setAPAging] = useState<APAging | null>(null)
  const [budgetVariance, setBudgetVariance] = useState<BudgetVariance | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    void fetchFinanceData()
  }, [])

  const fetchFinanceData = async () => {
    try {
      setLoading(true)
      setError(null)

      const { data: { user } } = await supabase.auth.getUser()
      const tenantId = user?.user_metadata?.tenant_id

      if (!tenantId) {
        setError('No tenant_id found')
        return
      }

      const headers = {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      }

      // Fetch all finance data in parallel
      const [alertRes, scenariosRes, apRes, budgetRes] = await Promise.all([
        fetch(`/api/finance/cash-forecast/alert?tenant_id=${tenantId}`, { headers }),
        fetch(`/api/finance/cash-forecast/all-scenarios?tenant_id=${tenantId}`, { headers }),
        fetch(`/api/finance/ap/aging?tenant_id=${tenantId}`, { headers }),
        fetch(`/api/finance/budget/variance?tenant_id=${tenantId}`, { headers }),
      ])

      if (alertRes.ok) {
        setCashAlert(await alertRes.json())
      }
      if (scenariosRes.ok) {
        setAllScenarios(await scenariosRes.json())
      }
      if (apRes.ok) {
        setAPAging(await apRes.json())
      }
      if (budgetRes.ok) {
        const data = await budgetRes.json()
        if (data.status !== 'no_budget') {
          setBudgetVariance(data)
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load finance data')
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

  // Prepare chart data for 13-week forecast
  const chartData = useMemo(() => {
    if (!allScenarios) return []

    return allScenarios.base.weekly_forecast.map((week, idx) => ({
      week: `W${week.week_number}`,
      base: week.ending_cash,
      optimistic: allScenarios.optimistic.weekly_forecast[idx]?.ending_cash || 0,
      pessimistic: allScenarios.pessimistic.weekly_forecast[idx]?.ending_cash || 0,
    }))
  }, [allScenarios])

  // AP Aging chart data
  const apChartData = useMemo(() => {
    if (!apAging) return []

    return [
      { name: 'Current', value: apAging.aging.current, color: '#10b981' },
      { name: '1-30', value: apAging.aging['1-30'], color: '#3b82f6' },
      { name: '31-60', value: apAging.aging['31-60'], color: '#f59e0b' },
      { name: '61-90', value: apAging.aging['61-90'], color: '#f97316' },
      { name: '90+', value: apAging.aging['90+'], color: '#ef4444' },
    ]
  }, [apAging])

  const getAlertVariant = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'good':
        return 'success'
      case 'caution':
        return 'warning'
      case 'critical':
        return 'danger'
      default:
        return 'default'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
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
          Loading finance data...
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
            <div className="font-semibold text-red-300">Error Loading Finance Data</div>
            <div className="text-sm text-red-400/80">{error}</div>
          </div>
        </div>
      </GlassCard>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        className="flex items-center justify-between"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div>
          <h2 className="text-2xl font-bold text-white">Finance Command Center</h2>
          <p className="text-slate-400 mt-1">Cash flow, AP, and budget tracking</p>
        </div>
        <motion.button
          onClick={() => void fetchFinanceData()}
          className="bg-slate-800 hover:bg-slate-700 text-white font-medium px-4 py-2 rounded-lg transition border border-slate-700"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          Refresh
        </motion.button>
      </motion.div>

      {/* Cash Position Alert */}
      {cashAlert && (
        <GlassCard variant={getAlertVariant(cashAlert.status)} glow padding="lg">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-4">
              <div className="text-4xl">
                {cashAlert.status === 'healthy' || cashAlert.status === 'good'
                  ? '💰'
                  : cashAlert.status === 'caution'
                    ? '⚠️'
                    : '🚨'}
              </div>
              <div>
                <div className="text-sm text-slate-400 uppercase tracking-wider">Cash Position</div>
                <div className="text-3xl font-bold text-white mt-1">
                  <AnimatedCurrency value={cashAlert.current_cash} />
                </div>
                <div className="text-sm text-slate-300 mt-2">{cashAlert.message}</div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm text-slate-400">Runway</div>
              <div className="text-2xl font-bold text-white">{cashAlert.runway_weeks} weeks</div>
            </div>
          </div>

          {cashAlert.recommendations.length > 0 && (
            <div className="mt-4 pt-4 border-t border-slate-700/50">
              <div className="text-sm text-slate-400 mb-2">Recommendations:</div>
              <ul className="space-y-1">
                {cashAlert.recommendations.map((rec, idx) => (
                  <li key={idx} className="text-sm text-slate-300 flex items-center gap-2">
                    <span className="text-emerald-400">•</span>
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </GlassCard>
      )}

      {/* Key Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard
          label="Current Cash"
          value={formatCurrency(cashAlert?.current_cash || 0)}
          icon="💵"
          variant="default"
        />
        <MetricCard
          label="Total AR"
          value={formatCurrency(allScenarios?.base.ar_total || 0)}
          icon="📥"
          subValue="Expected collections"
          variant="info"
        />
        <MetricCard
          label="Total AP"
          value={formatCurrency(apAging?.total || 0)}
          icon="📤"
          subValue={`${apAging?.overdue_pct.toFixed(0) || 0}% overdue`}
          variant={apAging && apAging.overdue_pct > 20 ? 'warning' : 'default'}
        />
        <MetricCard
          label="Net Position"
          value={formatCurrency(
            (allScenarios?.base.ar_total || 0) - (apAging?.total || 0)
          )}
          icon="📊"
          trend={(allScenarios?.base.ar_total || 0) > (apAging?.total || 0) ? 'up' : 'down'}
          variant={(allScenarios?.base.ar_total || 0) > (apAging?.total || 0) ? 'success' : 'warning'}
        />
      </div>

      {/* 13-Week Cash Forecast Chart */}
      {chartData.length > 0 && (
        <GlassCard padding="lg">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-white">13-Week Cash Forecast</h3>
              <p className="text-sm text-slate-400 mt-1">
                Projected cash balance with optimistic, base, and pessimistic scenarios
              </p>
            </div>
            <div className="flex items-center gap-4 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-emerald-500" />
                <span className="text-slate-400">Optimistic</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-blue-500" />
                <span className="text-slate-400">Base</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-amber-500" />
                <span className="text-slate-400">Pessimistic</span>
              </div>
            </div>
          </div>

          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="optimisticGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#10b981" stopOpacity={0.3} />
                    <stop offset="100%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="baseGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.3} />
                    <stop offset="100%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="pessimisticGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#f59e0b" stopOpacity={0.3} />
                    <stop offset="100%" stopColor="#f59e0b" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis
                  dataKey="week"
                  stroke="#64748b"
                  tick={{ fill: '#64748b', fontSize: 12 }}
                  axisLine={{ stroke: '#334155' }}
                />
                <YAxis
                  stroke="#64748b"
                  tick={{ fill: '#64748b', fontSize: 12 }}
                  axisLine={{ stroke: '#334155' }}
                  tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                    boxShadow: '0 10px 40px rgba(0,0,0,0.5)',
                  }}
                  labelStyle={{ color: '#94a3b8' }}
                  formatter={(value) => [formatCurrency(value as number), '']}
                />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="optimistic"
                  name="Optimistic"
                  stroke="#10b981"
                  strokeWidth={2}
                  fill="url(#optimisticGradient)"
                />
                <Area
                  type="monotone"
                  dataKey="base"
                  name="Base"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  fill="url(#baseGradient)"
                />
                <Area
                  type="monotone"
                  dataKey="pessimistic"
                  name="Pessimistic"
                  stroke="#f59e0b"
                  strokeWidth={2}
                  fill="url(#pessimisticGradient)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Min Cash Point Warning */}
          {allScenarios && allScenarios.base.min_cash < 25000 && (
            <div className="mt-4 p-3 bg-amber-950/30 border border-amber-500/30 rounded-lg">
              <div className="flex items-center gap-2 text-amber-400">
                <span>⚠️</span>
                <span className="text-sm">
                  Projected minimum cash of {formatCurrency(allScenarios.base.min_cash)} in week{' '}
                  {allScenarios.base.min_cash_week}
                </span>
              </div>
            </div>
          )}
        </GlassCard>
      )}

      {/* AP Aging and Budget Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* AP Aging Breakdown */}
        {apAging && (
          <GlassCard padding="lg">
            <h3 className="text-lg font-semibold text-white mb-4">AP Aging</h3>

            <div className="h-48 mb-4">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={apChartData} layout="vertical" margin={{ left: 0, right: 20 }}>
                  <XAxis
                    type="number"
                    stroke="#64748b"
                    tick={{ fill: '#64748b', fontSize: 12 }}
                    tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
                  />
                  <YAxis
                    type="category"
                    dataKey="name"
                    stroke="#64748b"
                    tick={{ fill: '#94a3b8', fontSize: 12 }}
                    width={60}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1e293b',
                      border: '1px solid #334155',
                      borderRadius: '8px',
                    }}
                    formatter={(value) => [formatCurrency(value as number), 'Amount']}
                  />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                    {apChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Total AP</span>
                <span className="text-white font-semibold">{formatCurrency(apAging.total)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Overdue</span>
                <span className="text-amber-400 font-semibold">
                  {formatCurrency(apAging.overdue)} ({apAging.overdue_pct.toFixed(0)}%)
                </span>
              </div>
            </div>
          </GlassCard>
        )}

        {/* Budget vs Actual */}
        <GlassCard padding="lg">
          <h3 className="text-lg font-semibold text-white mb-4">Budget vs Actual</h3>

          {budgetVariance ? (
            <div className="space-y-4">
              {budgetVariance.categories.slice(0, 5).map((cat) => (
                <div key={cat.category}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-slate-300 capitalize">
                      {cat.category.replace(/_/g, ' ')}
                    </span>
                    <span
                      className={
                        cat.status === 'over'
                          ? 'text-red-400'
                          : cat.status === 'under'
                            ? 'text-emerald-400'
                            : 'text-slate-400'
                      }
                    >
                      {cat.variance >= 0 ? '+' : ''}
                      {formatCurrency(cat.variance)} ({cat.variance_pct.toFixed(0)}%)
                    </span>
                  </div>
                  <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                    <motion.div
                      className={`h-full rounded-full ${
                        cat.status === 'over'
                          ? 'bg-red-500'
                          : cat.status === 'under'
                            ? 'bg-emerald-500'
                            : 'bg-blue-500'
                      }`}
                      initial={{ width: 0 }}
                      animate={{
                        width: `${Math.min(100, Math.abs((cat.actual / cat.budget) * 100))}%`,
                      }}
                      transition={{ duration: 0.8, ease: 'easeOut' }}
                    />
                  </div>
                  <div className="flex justify-between text-xs text-slate-500 mt-1">
                    <span>Actual: {formatCurrency(cat.actual)}</span>
                    <span>Budget: {formatCurrency(cat.budget)}</span>
                  </div>
                </div>
              ))}

              <div className="pt-4 border-t border-slate-700/50">
                <div className="flex justify-between">
                  <span className="text-slate-400">Total Variance</span>
                  <span
                    className={`font-semibold ${
                      budgetVariance.totals.variance > 0 ? 'text-red-400' : 'text-emerald-400'
                    }`}
                  >
                    {budgetVariance.totals.variance >= 0 ? '+' : ''}
                    {formatCurrency(budgetVariance.totals.variance)}
                  </span>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="text-4xl mb-3">📋</div>
              <p className="text-slate-400 text-sm">No budget set for this period</p>
              <p className="text-slate-500 text-xs mt-1">
                Create a budget via the API to track variance
              </p>
            </div>
          )}
        </GlassCard>
      </div>

      {/* Cash Flow Summary Cards */}
      {allScenarios && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <GlassCard variant="success" padding="md">
            <div className="text-sm text-slate-400 mb-1">Optimistic Scenario</div>
            <div className="text-2xl font-bold text-emerald-400">
              {formatCurrency(allScenarios.optimistic.ending_cash)}
            </div>
            <div className="text-sm text-slate-500 mt-1">
              {allScenarios.optimistic.runway_weeks}+ weeks runway
            </div>
          </GlassCard>

          <GlassCard variant="info" padding="md">
            <div className="text-sm text-slate-400 mb-1">Base Scenario</div>
            <div className="text-2xl font-bold text-blue-400">
              {formatCurrency(allScenarios.base.ending_cash)}
            </div>
            <div className="text-sm text-slate-500 mt-1">
              {allScenarios.base.runway_weeks} weeks runway
            </div>
          </GlassCard>

          <GlassCard variant="warning" padding="md">
            <div className="text-sm text-slate-400 mb-1">Pessimistic Scenario</div>
            <div className="text-2xl font-bold text-amber-400">
              {formatCurrency(allScenarios.pessimistic.ending_cash)}
            </div>
            <div className="text-sm text-slate-500 mt-1">
              {allScenarios.pessimistic.runway_weeks} weeks runway
            </div>
          </GlassCard>
        </div>
      )}
    </div>
  )
}
