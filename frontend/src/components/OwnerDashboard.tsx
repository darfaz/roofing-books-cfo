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

// Mock data for demo purposes
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

export function OwnerDashboard() {
  const [cash, setCash] = useState<CashPosition>(MOCK_DATA.cash)
  const [revenue, setRevenue] = useState<Revenue>(MOCK_DATA.revenue)
  const [arAging, setArAging] = useState<ARBucket>(MOCK_DATA.arAging)
  const [forecast, setForecast] = useState<ForecastWeek[]>(MOCK_DATA.forecast)
  const [jobs, setJobs] = useState<Job[]>(MOCK_DATA.jobs)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    void fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      const { data: { user } } = await supabase.auth.getUser()
      const tenantId = user?.user_metadata?.tenant_id

      if (!tenantId) {
        // Use mock data if no tenant
        setLoading(false)
        return
      }

      // Fetch cash position
      const { data: cashData } = await supabase
        .from('cash_positions')
        .select('*')
        .eq('tenant_id', tenantId)
        .order('position_date', { ascending: false })
        .limit(2)

      if (cashData && cashData.length > 0) {
        const current = cashData[0]
        const previous = cashData[1]
        const changeWow = previous
          ? (current.total_cash - previous.total_cash) / previous.total_cash
          : 0
        setCash({
          total_cash: current.total_cash,
          runway_weeks: current.runway_weeks || 12,
          change_wow: changeWow,
        })
      }

      // Fetch forecast
      const { data: forecastData } = await supabase
        .from('cash_forecast')
        .select('*')
        .eq('tenant_id', tenantId)
        .order('week_start_date', { ascending: true })
        .limit(13)

      if (forecastData && forecastData.length > 0) {
        setForecast(forecastData)
      }

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
      {/* Health Banner */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className={`p-5 rounded-xl border ${
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
          change={`${cash.change_wow >= 0 ? '+' : ''}${(cash.change_wow * 100).toFixed(0)}% WoW`}
          changeType={cash.change_wow >= 0 ? 'positive' : 'negative'}
          icon="💵"
        />
        <MetricCard
          label="Revenue MTD"
          value={formatCurrency(revenue.mtd)}
          change={`${(revenue.progress * 100).toFixed(0)}% of ${formatCurrency(revenue.target)} target`}
          changeType={revenue.progress >= 0.8 ? 'positive' : 'neutral'}
          icon="📈"
        />
        <MetricCard
          label="AR Outstanding"
          value={formatCurrency(totalAR)}
          change={`${formatCurrency(overdueAR)} overdue`}
          changeType={overdueAR > 0 ? 'negative' : 'positive'}
          icon="📋"
        />
        <MetricCard
          label="Backlog"
          value={formatCurrency(MOCK_DATA.backlog.amount)}
          change={`${MOCK_DATA.backlog.jobs} jobs scheduled`}
          changeType="neutral"
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
