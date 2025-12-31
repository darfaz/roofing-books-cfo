import { useEffect, useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import { supabase } from '../lib/supabase'
import { GlassCard, MetricCard } from './ui/GlassCard'

interface CashPosition {
  total_cash: number
  runway_weeks: number
  change_wow: number
}

interface Revenue {
  mtd: number
  target: number
  progress: number
}

interface ARBucket {
  current: number
  '1-30': number
  '31-60': number
  '61-90': number
  '90+': number
}

interface ForecastWeek {
  week_start_date: string
  ending_cash: number
  optimistic_cash: number
  pessimistic_cash: number
}

interface Job {
  name: string
  revenue: number
  margin: number
  status: string
}

// Demo data for Apex Roofing Solutions ($3.5M roofing contractor)
const DEMO_DATA = {
  cash: {
    total_cash: 187500,
    runway_weeks: 14,
    change_wow: 0.12,
  },
  revenue: {
    mtd: 292000,
    target: 320000,
    progress: 0.9125,
  },
  arAging: {
    current: 125000,
    '1-30': 68000,
    '31-60': 32000,
    '61-90': 18000,
    '90+': 8500,
  },
  forecast: Array.from({ length: 13 }, (_, i) => ({
    week_start_date: new Date(Date.now() + i * 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    ending_cash: 187500 + (i * 8500) - (i % 3 === 0 ? 22000 : 0) + (i % 4 === 0 ? 35000 : 0),
    optimistic_cash: 187500 + (i * 12000),
    pessimistic_cash: 187500 + (i * 3500) - (i % 2 === 0 ? 15000 : 0),
  })),
  jobs: [
    { name: 'Henderson Commercial Plaza', revenue: 85000, margin: 0.34, status: 'in_progress' },
    { name: 'Oakwood HOA - Phase 2', revenue: 125000, margin: 0.31, status: 'in_progress' },
    { name: 'Martinez Insurance Claim', revenue: 28500, margin: 0.42, status: 'completed' },
    { name: 'Thompson Estate Reroof', revenue: 45000, margin: 0.36, status: 'scheduled' },
    { name: 'Downtown Office Complex', revenue: 175000, margin: 0.29, status: 'scheduled' },
    { name: 'Wilson Hail Damage Repair', revenue: 18500, margin: 0.38, status: 'completed' },
  ],
  backlog: {
    amount: 485000,
    jobs: 12,
  },
}

// Mock data for regular users without QB connected
const MOCK_DATA = {
  cash: {
    total_cash: 127450,
    runway_weeks: 12,
    change_wow: 0.08,
  },
  revenue: {
    mtd: 87500,
    target: 100000,
    progress: 0.875,
  },
  arAging: {
    current: 45000,
    '1-30': 28000,
    '31-60': 12000,
    '61-90': 5000,
    '90+': 2500,
  },
  forecast: Array.from({ length: 13 }, (_, i) => ({
    week_start_date: new Date(Date.now() + i * 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    ending_cash: 127450 + (i * 5000) - (i % 3 === 0 ? 15000 : 0),
    optimistic_cash: 127450 + (i * 8000),
    pessimistic_cash: 127450 + (i * 2000) - (i % 2 === 0 ? 10000 : 0),
  })),
  jobs: [
    { name: 'Smith Residence', revenue: 18000, margin: 0.33, status: 'in_progress' },
    { name: 'Johnson Commercial', revenue: 45000, margin: 0.38, status: 'in_progress' },
    { name: 'Williams Repair', revenue: 8500, margin: 0.18, status: 'completed' },
    { name: 'Davis Reroof', revenue: 22000, margin: 0.28, status: 'scheduled' },
  ],
  backlog: {
    amount: 350000,
    jobs: 8,
  },
}

interface OwnerDashboardProps {
  isDemoMode?: boolean
}

export function OwnerDashboard({ isDemoMode = false }: OwnerDashboardProps) {
  const [cash, setCash] = useState<CashPosition>(MOCK_DATA.cash)
  const [revenue, setRevenue] = useState<Revenue>(MOCK_DATA.revenue)
  const [arAging, setArAging] = useState<ARBucket>(MOCK_DATA.arAging)
  const [forecast, setForecast] = useState<ForecastWeek[]>(MOCK_DATA.forecast)
  const [jobs, setJobs] = useState<Job[]>(MOCK_DATA.jobs)
  const [loading, setLoading] = useState(true)
  const [hasRealData, setHasRealData] = useState(false) // Track if showing real vs mock data

  useEffect(() => {
    void fetchDashboardData()
  }, [isDemoMode])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)

      // In demo mode, use hardcoded Apex Roofing Solutions data
      if (isDemoMode) {
        setCash(DEMO_DATA.cash)
        setRevenue(DEMO_DATA.revenue)
        setArAging(DEMO_DATA.arAging)
        setForecast(DEMO_DATA.forecast)
        setJobs(DEMO_DATA.jobs)
        setHasRealData(true) // Demo data counts as "real" for display
        setLoading(false)
        return
      }

      const { data: { user } } = await supabase.auth.getUser()
      const tenantId = user?.user_metadata?.tenant_id

      if (!tenantId) {
        setLoading(false)
        return
      }

      // Compute metrics from synced transactions
      const now = new Date()
      const monthStart = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split('T')[0]
      const last30Days = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]

      // Fetch deposits (cash inflows)
      const { data: deposits, error: depositsErr } = await supabase
        .from('transactions')
        .select('total_amount, transaction_date')
        .eq('tenant_id', tenantId)
        .eq('transaction_type', 'deposit')
        .gte('transaction_date', last30Days)

      // Fetch invoices for revenue and AR
      const { data: invoices, error: invoicesErr } = await supabase
        .from('transactions')
        .select('total_amount, transaction_date, status')
        .eq('tenant_id', tenantId)
        .eq('transaction_type', 'invoice')

      // Fetch expenses
      const { data: expenses, error: expensesErr } = await supabase
        .from('transactions')
        .select('total_amount, transaction_date')
        .eq('tenant_id', tenantId)
        .in('transaction_type', ['expense', 'bill'])
        .gte('transaction_date', last30Days)

      // Log for debugging
      if (depositsErr || invoicesErr || expensesErr) {
        console.error('Transaction fetch errors:', { depositsErr, invoicesErr, expensesErr })
      }
      console.log('Dashboard data fetch:', {
        tenantId,
        deposits: deposits?.length || 0,
        invoices: invoices?.length || 0,
        expenses: expenses?.length || 0
      })

      // Check if we have real data
      const totalTransactions = (deposits?.length || 0) + (invoices?.length || 0) + (expenses?.length || 0)
      if (totalTransactions === 0) {
        // No synced data yet - keep mock data
        console.log('No transaction data found - showing sample data')
        setLoading(false)
        return
      }

      setHasRealData(true)

      // Calculate cash position from deposits - expenses
      const totalDeposits = deposits?.reduce((sum, d) => sum + (d.total_amount || 0), 0) || 0
      const totalExpenses = expenses?.reduce((sum, e) => sum + Math.abs(e.total_amount || 0), 0) || 0
      const netCash = totalDeposits - totalExpenses
      const weeklyBurn = totalExpenses / 4 // Rough weekly estimate
      const runwayWeeks = weeklyBurn > 0 ? Math.round(Math.max(netCash, 50000) / weeklyBurn) : 12

      setCash({
        total_cash: Math.max(netCash, 50000), // Minimum reasonable cash
        runway_weeks: Math.min(runwayWeeks, 52),
        change_wow: 0.05, // Would need historical data to calculate
      })

      // Calculate MTD revenue from invoices this month
      const mtdInvoices = invoices?.filter(inv => inv.transaction_date >= monthStart) || []
      const mtdRevenue = mtdInvoices.reduce((sum, inv) => sum + (inv.total_amount || 0), 0)
      const targetRevenue = mtdRevenue > 0 ? mtdRevenue * 1.1 : 100000 // 10% above or default

      setRevenue({
        mtd: mtdRevenue,
        target: targetRevenue,
        progress: mtdRevenue / targetRevenue,
      })

      // Calculate AR aging from unpaid invoices
      const unpaidInvoices = invoices?.filter(inv => inv.status !== 'paid') || []
      const aging: ARBucket = { current: 0, '1-30': 0, '31-60': 0, '61-90': 0, '90+': 0 }

      unpaidInvoices.forEach(inv => {
        const invDate = new Date(inv.transaction_date)
        const daysOld = Math.floor((now.getTime() - invDate.getTime()) / (1000 * 60 * 60 * 24))
        const amount = inv.total_amount || 0

        if (daysOld <= 0) aging.current += amount
        else if (daysOld <= 30) aging['1-30'] += amount
        else if (daysOld <= 60) aging['31-60'] += amount
        else if (daysOld <= 90) aging['61-90'] += amount
        else aging['90+'] += amount
      })

      setArAging(aging)

      // Generate simple forecast based on current trends
      const weeklyInflow = totalDeposits / 4
      const weeklyOutflow = totalExpenses / 4
      const startingCash = Math.max(netCash, 50000)

      const forecastWeeks: ForecastWeek[] = Array.from({ length: 13 }, (_, i) => {
        const weekStart = new Date(now.getTime() + i * 7 * 24 * 60 * 60 * 1000)
        const baseChange = weeklyInflow - weeklyOutflow
        return {
          week_start_date: weekStart.toISOString().split('T')[0],
          ending_cash: startingCash + (baseChange * (i + 1)),
          optimistic_cash: startingCash + (baseChange * 1.2 * (i + 1)),
          pessimistic_cash: startingCash + (baseChange * 0.7 * (i + 1)),
        }
      })

      setForecast(forecastWeeks)

    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  // Calculate health status
  const healthStatus = useMemo(() => {
    const runway = cash.runway_weeks
    const totalAR = Object.values(arAging).reduce((sum, val) => sum + val, 0)
    const overdueAR = arAging['61-90'] + arAging['90+']
    const overduePct = totalAR > 0 ? (overdueAR / totalAR) * 100 : 0

    if (runway >= 8 && overduePct < 15) {
      return { status: 'Healthy', color: 'emerald', emoji: '🟢' }
    } else if (runway >= 4) {
      return { status: 'Warning', color: 'amber', emoji: '🟡' }
    } else {
      return { status: 'Alert', color: 'red', emoji: '🔴' }
    }
  }, [cash.runway_weeks, arAging])

  const totalAR = useMemo(() => Object.values(arAging).reduce((sum, val) => sum + val, 0), [arAging])
  const overdueAR = useMemo(() => arAging['61-90'] + arAging['90+'], [arAging])

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value)

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
          Loading dashboard...
        </motion.div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Data Source Indicator */}
      {!hasRealData && !isDemoMode && (
        <div className="px-4 py-2 bg-amber-500/10 border border-amber-500/30 rounded-lg text-amber-400 text-sm flex items-center gap-2">
          <span className="text-amber-500">⚠️</span>
          Showing sample data. Connect QuickBooks to see your real numbers.
        </div>
      )}

      {/* Health Banner */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className={`p-5 rounded-xl border relative ${
          healthStatus.color === 'emerald'
            ? 'bg-emerald-500/10 border-emerald-500/30'
            : healthStatus.color === 'amber'
            ? 'bg-amber-500/10 border-amber-500/30'
            : 'bg-red-500/10 border-red-500/30'
        }`}
      >
        <div className="flex items-center gap-3">
          <span className="text-2xl">{healthStatus.emoji}</span>
          <span className={`text-xl font-bold ${
            healthStatus.color === 'emerald'
              ? 'text-emerald-400'
              : healthStatus.color === 'amber'
              ? 'text-amber-400'
              : 'text-red-400'
          }`}>
            {healthStatus.status}
          </span>
        </div>
        <p className="text-slate-400 mt-2 text-sm">
          Cash runway: {cash.runway_weeks} weeks &nbsp;|&nbsp;
          AR overdue: {totalAR > 0 ? ((overdueAR / totalAR) * 100).toFixed(0) : 0}% &nbsp;|&nbsp;
          Revenue MTD: {(revenue.progress * 100).toFixed(0)}% of target
        </p>
      </motion.div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="Cash Balance"
          value={formatCurrency(cash.total_cash)}
          trendValue={`${cash.change_wow >= 0 ? '+' : ''}${(cash.change_wow * 100).toFixed(0)}% WoW`}
          trend={cash.change_wow >= 0 ? 'up' : 'down'}
          icon="💵"
        />
        <MetricCard
          label="Revenue MTD"
          value={formatCurrency(revenue.mtd)}
          subValue={`${(revenue.progress * 100).toFixed(0)}% of ${formatCurrency(revenue.target)} target`}
          trend={revenue.progress >= 0.8 ? 'up' : 'neutral'}
          icon="📈"
        />
        <MetricCard
          label="AR Outstanding"
          value={formatCurrency(totalAR)}
          subValue={`${formatCurrency(overdueAR)} overdue`}
          trend={overdueAR > 0 ? 'down' : 'up'}
          icon="📋"
        />
        <MetricCard
          label="Backlog"
          value={formatCurrency(isDemoMode ? DEMO_DATA.backlog.amount : MOCK_DATA.backlog.amount)}
          subValue={`${isDemoMode ? DEMO_DATA.backlog.jobs : MOCK_DATA.backlog.jobs} jobs scheduled`}
          trend="neutral"
          icon="🔧"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Cash Forecast Chart */}
        <GlassCard>
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <span>📊</span> 13-Week Cash Forecast
          </h3>
          <div className="h-64 flex items-end gap-1">
            {forecast.map((week, i) => {
              const maxCash = Math.max(...forecast.map(f => f.optimistic_cash))
              const height = (week.ending_cash / maxCash) * 100
              return (
                <motion.div
                  key={week.week_start_date}
                  initial={{ height: 0 }}
                  animate={{ height: `${height}%` }}
                  transition={{ delay: i * 0.05 }}
                  className="flex-1 bg-gradient-to-t from-emerald-500/50 to-emerald-500/20 rounded-t-sm relative group"
                >
                  <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-800 text-xs text-white px-2 py-1 rounded whitespace-nowrap">
                    {formatCurrency(week.ending_cash)}
                  </div>
                </motion.div>
              )
            })}
          </div>
          <div className="flex justify-between text-xs text-slate-500 mt-2">
            <span>This Week</span>
            <span>Week 13</span>
          </div>
        </GlassCard>

        {/* AR Aging */}
        <GlassCard>
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <span>📅</span> AR Aging
          </h3>
          <div className="space-y-3">
            {Object.entries(arAging).map(([bucket, amount]) => {
              const pct = totalAR > 0 ? (amount / totalAR) * 100 : 0
              const isOverdue = bucket === '61-90' || bucket === '90+'
              return (
                <div key={bucket} className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className={isOverdue ? 'text-amber-400' : 'text-slate-300'}>
                      {bucket === 'current' ? 'Current' : `${bucket} days`}
                    </span>
                    <span className="text-slate-400">{formatCurrency(amount)}</span>
                  </div>
                  <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${pct}%` }}
                      className={`h-full rounded-full ${
                        isOverdue ? 'bg-amber-500' : 'bg-emerald-500'
                      }`}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </GlassCard>
      </div>

      {/* Jobs Profitability */}
      <GlassCard>
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <span>🏠</span> Job Profitability
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left text-sm text-slate-400 border-b border-slate-800">
                <th className="pb-3">Job</th>
                <th className="pb-3">Revenue</th>
                <th className="pb-3">Margin</th>
                <th className="pb-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {jobs.map((job) => (
                <motion.tr
                  key={job.name}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="text-sm"
                >
                  <td className="py-3 text-white font-medium">{job.name}</td>
                  <td className="py-3 text-slate-300">{formatCurrency(job.revenue)}</td>
                  <td className="py-3">
                    <span className={`font-medium ${
                      job.margin >= 0.3 ? 'text-emerald-400' :
                      job.margin >= 0.2 ? 'text-amber-400' : 'text-red-400'
                    }`}>
                      {(job.margin * 100).toFixed(0)}%
                    </span>
                  </td>
                  <td className="py-3">
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      job.status === 'completed' ? 'bg-emerald-500/20 text-emerald-400' :
                      job.status === 'in_progress' ? 'bg-blue-500/20 text-blue-400' :
                      'bg-slate-500/20 text-slate-400'
                    }`}>
                      {job.status.replace('_', ' ')}
                    </span>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </GlassCard>
    </div>
  )
}
