import { useEffect, useMemo, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { supabase } from '../lib/supabase'
import { GlassCard } from './ui/GlassCard'
import { AnimatedCurrency } from './ui/AnimatedNumber'

type RoadmapStatus = 'pending' | 'in_progress' | 'completed' | 'cancelled' | 'blocked'
type EffortLevel = 'low' | 'medium' | 'high'
type Category = 'weekly_ops' | 'monthly_close' | 'quarterly_review' | 'strategic' | 'compliance'

interface RoadmapItem {
  id: string
  tenant_id: string
  driver_key: string | null
  title: string
  description: string | null
  category: Category
  priority: 'low' | 'medium' | 'high' | 'critical'
  status: RoadmapStatus
  expected_impact_ev: number | null
  effort_level: EffortLevel
  estimated_hours: number | null
  due_date: string | null
  completed_at: string | null
  human_approval_required: boolean
  created_at: string
  updated_at: string
}

const DRIVER_META: Record<string, { label: string; icon: string }> = {
  management_independence: { label: 'Management Independence', icon: '👔' },
  financial_records: { label: 'Financial Records', icon: '📊' },
  recurring_revenue: { label: 'Recurring Revenue', icon: '🔄' },
  operational_systems: { label: 'Operational Systems', icon: '⚙️' },
  customer_diversity: { label: 'Customer Diversity', icon: '👥' },
  market_outlook: { label: 'Market Outlook', icon: '📈' },
  other: { label: 'Other', icon: '📋' },
}

const STATUS_CONFIG: Record<RoadmapStatus, { label: string; color: string; bg: string }> = {
  completed: { label: 'Completed', color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/30' },
  in_progress: { label: 'In Progress', color: 'text-blue-400', bg: 'bg-blue-500/10 border-blue-500/30' },
  pending: { label: 'Pending', color: 'text-slate-400', bg: 'bg-slate-500/10 border-slate-500/30' },
  blocked: { label: 'Blocked', color: 'text-red-400', bg: 'bg-red-500/10 border-red-500/30' },
  cancelled: { label: 'Cancelled', color: 'text-slate-500', bg: 'bg-slate-600/10 border-slate-600/30' },
}

const EFFORT_CONFIG: Record<EffortLevel, { label: string; color: string }> = {
  low: { label: 'Low', color: 'text-emerald-400' },
  medium: { label: 'Medium', color: 'text-amber-400' },
  high: { label: 'High', color: 'text-red-400' },
}

const PRIORITY_CONFIG: Record<string, { label: string; color: string }> = {
  critical: { label: 'Critical', color: 'text-red-400' },
  high: { label: 'High', color: 'text-amber-400' },
  medium: { label: 'Medium', color: 'text-blue-400' },
  low: { label: 'Low', color: 'text-slate-400' },
}

interface ValuationRoadmapProps {
  accessToken: string
  isDemoMode?: boolean
}

export function ValuationRoadmap({ accessToken, isDemoMode = false }: ValuationRoadmapProps) {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [items, setItems] = useState<RoadmapItem[]>([])
  const [updatingId, setUpdatingId] = useState<string | null>(null)
  const [filter, setFilter] = useState<'all' | 'pending' | 'in_progress' | 'completed'>('all')

  const fetchRoadmap = async () => {
    try {
      setLoading(true)
      setError(null)

      // Demo mode - fetch from demo endpoint
      if (isDemoMode) {
        const response = await fetch('/api/demo/roadmap')
        const result = await response.json()
        if (!response.ok) {
          throw new Error(result.detail || 'Failed to fetch demo data')
        }
        setItems(result)
        return
      }

      const { data: { user } } = await supabase.auth.getUser()
      const tenantId = user?.user_metadata?.tenant_id

      if (!tenantId) {
        setError('No tenant_id found in user metadata')
        return
      }

      const { data, error: fetchError } = await supabase
        .from('roadmap_items')
        .select('*')
        .eq('tenant_id', tenantId)
        .order('priority', { ascending: true })
        .order('expected_impact_ev', { ascending: false })

      if (fetchError) {
        console.error('Roadmap error:', fetchError)
        setError(fetchError.message)
      } else {
        setItems(data || [])
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load roadmap')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void fetchRoadmap()
  }, [accessToken])

  const updateStatus = async (id: string, status: RoadmapStatus) => {
    try {
      setUpdatingId(id)
      const updateData: Partial<RoadmapItem> = { status }
      if (status === 'completed') {
        updateData.completed_at = new Date().toISOString()
      }

      const { error: updateError } = await supabase
        .from('roadmap_items')
        .update(updateData)
        .eq('id', id)

      if (updateError) throw updateError
      await fetchRoadmap()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update status')
    } finally {
      setUpdatingId(null)
    }
  }

  const filteredItems = useMemo(() => {
    if (filter === 'all') return items
    return items.filter(item => item.status === filter)
  }, [items, filter])

  const nextActions = useMemo(() => {
    return items
      .filter(i => i.status === 'pending' || i.status === 'in_progress')
      .sort((a, b) => {
        // In progress first, then by impact
        if (a.status === 'in_progress' && b.status !== 'in_progress') return -1
        if (b.status === 'in_progress' && a.status !== 'in_progress') return 1
        return (b.expected_impact_ev || 0) - (a.expected_impact_ev || 0)
      })
      .slice(0, 3)
  }, [items])

  const grouped = useMemo(() => {
    const map = new Map<string, RoadmapItem[]>()
    for (const item of filteredItems) {
      const key = item.driver_key || 'other'
      if (!map.has(key)) map.set(key, [])
      map.get(key)!.push(item)
    }
    return map
  }, [filteredItems])

  const stats = useMemo(() => {
    const total = items.length
    const completed = items.filter(i => i.status === 'completed').length
    const inProgress = items.filter(i => i.status === 'in_progress').length
    const totalImpact = items.reduce((sum, i) => sum + (i.expected_impact_ev || 0), 0)
    const completedImpact = items
      .filter(i => i.status === 'completed')
      .reduce((sum, i) => sum + (i.expected_impact_ev || 0), 0)
    return { total, completed, inProgress, totalImpact, completedImpact }
  }, [items])

  // Check if quarterly spec jam is due (more than 90 days since last completed quarterly_review)
  const specJamDue = useMemo(() => {
    const quarterlyItems = items.filter(i => i.category === 'quarterly_review' && i.status === 'completed')
    if (quarterlyItems.length === 0) return true
    const lastCompleted = quarterlyItems
      .map(i => new Date(i.completed_at || i.updated_at))
      .sort((a, b) => b.getTime() - a.getTime())[0]
    const daysSince = (Date.now() - lastCompleted.getTime()) / (1000 * 60 * 60 * 24)
    return daysSince > 90
  }, [items])

  if (loading) {
    return (
      <GlassCard padding="lg">
        <div className="flex items-center gap-3 text-slate-400">
          <motion.div
            className="w-5 h-5 border-2 border-emerald-500 border-t-transparent rounded-full"
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          />
          Loading roadmap...
        </div>
      </GlassCard>
    )
  }

  if (error && items.length === 0) {
    return (
      <GlassCard variant="danger" padding="lg">
        <div className="flex items-center gap-3">
          <span className="text-2xl">⚠️</span>
          <div>
            <div className="font-semibold text-red-300">Error Loading Roadmap</div>
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
        className="flex flex-col sm:flex-row sm:items-center justify-between gap-4"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div>
          <h2 className="text-xl font-semibold">Valuation Roadmap</h2>
          <p className="text-slate-400 mt-1">Prioritized improvements to increase enterprise value</p>
        </div>
        <motion.button
          onClick={() => void fetchRoadmap()}
          className="bg-slate-800 hover:bg-slate-700 text-white font-medium px-4 py-2 rounded-lg transition border border-slate-700"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          Refresh
        </motion.button>
      </motion.div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <GlassCard padding="sm">
          <div className="text-sm text-slate-400">Total Items</div>
          <div className="text-2xl font-bold text-white">{stats.total}</div>
        </GlassCard>
        <GlassCard padding="sm" variant="success">
          <div className="text-sm text-slate-400">Completed</div>
          <div className="text-2xl font-bold text-emerald-400">{stats.completed}</div>
        </GlassCard>
        <GlassCard padding="sm" variant="info">
          <div className="text-sm text-slate-400">In Progress</div>
          <div className="text-2xl font-bold text-blue-400">{stats.inProgress}</div>
        </GlassCard>
        <GlassCard padding="sm">
          <div className="text-sm text-slate-400">Potential EV Impact</div>
          <div className="text-2xl font-bold text-white">
            <AnimatedCurrency value={stats.totalImpact - stats.completedImpact} />
          </div>
        </GlassCard>
      </div>

      {/* Spec Jam Reminder */}
      <AnimatePresence>
        {specJamDue && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <GlassCard variant="warning" padding="md">
              <div className="flex items-start gap-4">
                <span className="text-3xl">📅</span>
                <div>
                  <div className="font-semibold text-amber-300">Quarterly Spec Jam Due</div>
                  <div className="text-sm text-amber-200/80 mt-1">
                    Schedule a quarterly "Spec Jam" to refresh systems/process documentation and ensure the deal room stays buyer-ready.
                  </div>
                </div>
              </div>
            </GlassCard>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Next Actions */}
      {nextActions.length > 0 && (
        <div>
          <div className="text-sm text-slate-400 mb-3 flex items-center gap-2">
            <span className="text-lg">🎯</span> Next Actions
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {nextActions.map((item, index) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <GlassCard
                  padding="md"
                  glow={item.status === 'in_progress'}
                  variant={item.status === 'in_progress' ? 'info' : 'default'}
                >
                  <div className="flex items-start justify-between gap-3 mb-3">
                    <div className="text-2xl">{DRIVER_META[item.driver_key || 'other']?.icon || '📋'}</div>
                    <div className={`px-2 py-1 rounded text-xs border ${STATUS_CONFIG[item.status].bg}`}>
                      {STATUS_CONFIG[item.status].label}
                    </div>
                  </div>
                  <h3 className="font-semibold text-white mb-2">{item.title}</h3>
                  {item.description && (
                    <p className="text-sm text-slate-400 mb-3 line-clamp-2">{item.description}</p>
                  )}
                  <div className="flex items-center justify-between text-sm">
                    <div className="text-slate-400">
                      Impact: <span className="text-emerald-400 font-semibold">
                        +${((item.expected_impact_ev || 0) / 1000).toFixed(0)}K
                      </span>
                    </div>
                    <div className={EFFORT_CONFIG[item.effort_level]?.color || 'text-slate-400'}>
                      {EFFORT_CONFIG[item.effort_level]?.label || item.effort_level}
                    </div>
                  </div>
                  <div className="mt-4 flex gap-2">
                    {item.status === 'pending' && (
                      <motion.button
                        onClick={() => void updateStatus(item.id, 'in_progress')}
                        disabled={updatingId === item.id}
                        className="flex-1 bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 text-black font-semibold px-3 py-2 rounded-lg transition text-sm"
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        Start
                      </motion.button>
                    )}
                    {item.status === 'in_progress' && (
                      <motion.button
                        onClick={() => void updateStatus(item.id, 'completed')}
                        disabled={updatingId === item.id}
                        className="flex-1 bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 text-black font-semibold px-3 py-2 rounded-lg transition text-sm"
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        Complete
                      </motion.button>
                    )}
                  </div>
                </GlassCard>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Filter Tabs */}
      <div className="flex items-center gap-2">
        {(['all', 'pending', 'in_progress', 'completed'] as const).map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              filter === f
                ? 'bg-slate-800 text-white'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
            }`}
          >
            {f === 'all' ? 'All' : f === 'in_progress' ? 'In Progress' : f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {/* Grouped Items by Driver */}
      <div className="space-y-6">
        {Array.from(grouped.entries()).map(([driverKey, driverItems]) => (
          <motion.div
            key={driverKey}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <GlassCard padding="lg">
              <div className="flex items-center gap-3 mb-4">
                <span className="text-2xl">{DRIVER_META[driverKey]?.icon || '📋'}</span>
                <h3 className="text-lg font-semibold">{DRIVER_META[driverKey]?.label || 'Other'}</h3>
                <span className="text-sm text-slate-500">({driverItems.length})</span>
              </div>

              <div className="space-y-3">
                {driverItems.map((item) => (
                  <motion.div
                    key={item.id}
                    className="bg-slate-800/50 rounded-lg p-4 border border-slate-700/50"
                    whileHover={{ backgroundColor: 'rgba(51, 65, 85, 0.6)' }}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium text-white">{item.title}</span>
                          {item.human_approval_required && (
                            <span className="text-amber-400 text-xs" title="Requires human approval">
                              👤
                            </span>
                          )}
                        </div>
                        {item.description && (
                          <p className="text-sm text-slate-400 line-clamp-1">{item.description}</p>
                        )}
                        <div className="flex items-center gap-4 mt-2 text-sm">
                          <span className="text-slate-500">
                            Impact:{' '}
                            <span className="text-emerald-400 font-medium">
                              +${((item.expected_impact_ev || 0) / 1000).toFixed(0)}K
                            </span>
                          </span>
                          <span className={`${EFFORT_CONFIG[item.effort_level]?.color || 'text-slate-400'}`}>
                            {EFFORT_CONFIG[item.effort_level]?.label}
                          </span>
                          <span className={PRIORITY_CONFIG[item.priority]?.color || 'text-slate-400'}>
                            {PRIORITY_CONFIG[item.priority]?.label}
                          </span>
                        </div>
                      </div>

                      <div className="flex items-center gap-2 shrink-0">
                        <div className={`px-3 py-1 rounded-lg text-xs border ${STATUS_CONFIG[item.status].bg}`}>
                          {STATUS_CONFIG[item.status].label}
                        </div>
                        {item.status === 'pending' && (
                          <motion.button
                            onClick={() => void updateStatus(item.id, 'in_progress')}
                            disabled={updatingId === item.id}
                            className="bg-slate-700 hover:bg-slate-600 disabled:opacity-50 text-white text-sm font-medium px-3 py-1.5 rounded-lg transition"
                            whileTap={{ scale: 0.95 }}
                          >
                            Start
                          </motion.button>
                        )}
                        {item.status === 'in_progress' && (
                          <motion.button
                            onClick={() => void updateStatus(item.id, 'completed')}
                            disabled={updatingId === item.id}
                            className="bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 text-black text-sm font-medium px-3 py-1.5 rounded-lg transition"
                            whileTap={{ scale: 0.95 }}
                          >
                            Complete
                          </motion.button>
                        )}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </GlassCard>
          </motion.div>
        ))}

        {grouped.size === 0 && (
          <GlassCard padding="lg" className="text-center">
            <div className="text-4xl mb-4">📋</div>
            <h3 className="text-lg font-semibold mb-2">No Roadmap Items</h3>
            <p className="text-slate-400">Create roadmap items to track value-building improvements.</p>
          </GlassCard>
        )}
      </div>
    </div>
  )
}
