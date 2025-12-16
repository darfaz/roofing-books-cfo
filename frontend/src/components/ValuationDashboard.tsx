import { useEffect, useState } from 'react'

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
  score: number // 0-5 in current API implementation (converted)
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

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export function ValuationDashboard({ accessToken }: { accessToken: string }) {
  const [snapshot, setSnapshot] = useState<ValuationSnapshot | null>(null)
  const [driverScores, setDriverScores] = useState<DriverScore[]>([])
  const [historicalSnapshots, setHistoricalSnapshots] = useState<ValuationSnapshot[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    void fetchValuationData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [accessToken])

  const authHeaders = {
    Authorization: `Bearer ${accessToken}`,
  }

  const fetchValuationData = async () => {
    try {
      setLoading(true)
      setError(null)

      const snapshotRes = await fetch(`${API_BASE_URL}/api/valuation/snapshot`, {
        headers: authHeaders,
      })
      const snapshotJson = await snapshotRes.json()
      if (snapshotJson.success) setSnapshot(snapshotJson.data.snapshot)

      const driversRes = await fetch(`${API_BASE_URL}/api/valuation/drivers`, {
        headers: authHeaders,
      })
      const driversJson = await driversRes.json()
      if (driversJson.success) setDriverScores(driversJson.data.scores || [])

      const histRes = await fetch(`${API_BASE_URL}/api/valuation/snapshots?limit=12`, {
        headers: authHeaders,
      })
      const histJson = await histRes.json()
      if (histJson.success) setHistoricalSnapshots(histJson.data.snapshots || [])
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

  const getTierColor = (tier: string): string => {
    switch (tier) {
      case 'above_avg':
        return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30'
      case 'avg':
        return 'text-blue-400 bg-blue-500/10 border-blue-500/30'
      case 'below_avg':
        return 'text-amber-400 bg-amber-500/10 border-amber-500/30'
      default:
        return 'text-slate-400 bg-slate-500/10 border-slate-500/30'
    }
  }

  const getTierLabel = (tier: string): string => {
    switch (tier) {
      case 'above_avg':
        return 'Above Average'
      case 'avg':
        return 'Average'
      case 'below_avg':
        return 'Below Average'
      default:
        return tier
    }
  }

  const scoreTo100 = (score0to5: number) => Math.round((score0to5 / 5) * 100)

  const getScoreColor = (score100: number): string => {
    if (score100 >= 80) return 'text-emerald-400'
    if (score100 >= 60) return 'text-blue-400'
    if (score100 >= 40) return 'text-amber-400'
    return 'text-red-400'
  }

  const getScoreBg = (score100: number): string => {
    if (score100 >= 80) return 'bg-emerald-500/20'
    if (score100 >= 60) return 'bg-blue-500/20'
    if (score100 >= 40) return 'bg-amber-500/20'
    return 'bg-red-500/20'
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 text-white p-6">
        <div className="max-w-7xl mx-auto flex items-center justify-center h-64 text-slate-400">
          Loading valuation…
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-950 text-white p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-red-300">
            {error}
          </div>
        </div>
      </div>
    )
  }

  if (!snapshot) {
    return (
      <div className="min-h-screen bg-slate-950 text-white p-6">
        <div className="max-w-7xl mx-auto bg-slate-900 border border-slate-800 rounded-xl p-8 text-center">
          <h2 className="text-2xl font-bold mb-2">No valuation snapshot yet</h2>
          <p className="text-slate-400 mb-6">Create a snapshot via the API to populate the dashboard.</p>
          <button
            onClick={() => void fetchValuationData()}
            className="bg-emerald-500 hover:bg-emerald-400 text-black font-semibold px-6 py-3 rounded-lg transition"
          >
            Refresh
          </button>
        </div>
      </div>
    )
  }

  const avgValue = (snapshot.ev_low + snapshot.ev_high) / 2

  return (
    <div className="min-h-screen bg-slate-950 text-white p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Valuation Dashboard</h1>
            <p className="text-slate-400 mt-1">As of {formatDate(snapshot.as_of_date)}</p>
          </div>
          <div className="flex items-center gap-3">
            <div className={`px-4 py-2 rounded-lg border ${getTierColor(snapshot.tier)}`}>
              <div className="text-xs text-slate-400">Tier</div>
              <div className="font-semibold">{getTierLabel(snapshot.tier)}</div>
            </div>
            <button
              onClick={() => void fetchValuationData()}
              className="bg-slate-800 hover:bg-slate-700 text-white font-medium px-4 py-2 rounded-lg transition"
            >
              Refresh
            </button>
          </div>
        </div>

        {/* Valuation Meter */}
        <div className="bg-slate-900 rounded-xl p-8 border border-slate-800">
          <h2 className="text-xl font-semibold mb-6">Estimated Enterprise Value</h2>
          <div className="relative h-24 bg-slate-800 rounded-lg overflow-hidden mb-6">
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <div className="text-4xl font-bold">{formatCurrency(avgValue)}</div>
                <div className="text-sm text-slate-400 mt-1">
                  {formatCurrency(snapshot.ev_low)} - {formatCurrency(snapshot.ev_high)}
                </div>
              </div>
            </div>
            <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r from-amber-500 via-emerald-500 to-emerald-400 opacity-30" />
            <div className="absolute bottom-0 left-0 w-1 h-full bg-amber-400" />
            <div className="absolute bottom-0 right-0 w-1 h-full bg-emerald-400" />
            <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-1 h-full bg-white" />
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-slate-800 rounded-lg p-4">
              <div className="text-sm text-slate-400">TTM Revenue</div>
              <div className="text-xl font-bold">{formatCurrency(snapshot.ttm_revenue)}</div>
            </div>
            <div className="bg-slate-800 rounded-lg p-4">
              <div className="text-sm text-slate-400">TTM SDE</div>
              <div className="text-xl font-bold">{formatCurrency(snapshot.ttm_sde)}</div>
            </div>
            <div className="bg-slate-800 rounded-lg p-4">
              <div className="text-sm text-slate-400">TTM EBITDA</div>
              <div className="text-xl font-bold">{formatCurrency(snapshot.ttm_ebitda)}</div>
            </div>
            <div className="bg-slate-800 rounded-lg p-4">
              <div className="text-sm text-slate-400">Multiple Range</div>
              <div className="text-xl font-bold">
                {snapshot.multiple_low}x - {snapshot.multiple_high}x
              </div>
            </div>
          </div>

          <div className="mt-6 pt-6 border-t border-slate-800">
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm text-slate-400">Confidence</div>
              <div className={`font-semibold ${getScoreColor(snapshot.confidence_score)}`}>{snapshot.confidence_score}%</div>
            </div>
            <div className="w-full bg-slate-800 rounded-full h-2">
              <div className="h-2 rounded-full bg-emerald-500/20" style={{ width: `${snapshot.confidence_score}%` }} />
            </div>
          </div>
        </div>

        {/* Driver Scorecards */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Value Driver Scores</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(DRIVER_LABELS).map(([key, meta]) => {
              const score = driverScores.find((d) => d.driver_key === key)?.score ?? 0
              const score100 = scoreTo100(score)
              return (
                <div key={key} className="bg-slate-900 rounded-xl p-6 border border-slate-800">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <div className="text-3xl mb-2">{meta.icon}</div>
                      <h3 className="font-semibold text-lg">{meta.label}</h3>
                      <p className="text-sm text-slate-400">{meta.description}</p>
                    </div>
                    <div className={`text-2xl font-bold ${getScoreColor(score100)}`}>{score100}</div>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-3">
                    <div className={`h-3 rounded-full ${getScoreBg(score100)}`} style={{ width: `${score100}%` }} />
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Timeline */}
        <div className="bg-slate-900 rounded-xl p-8 border border-slate-800">
          <h2 className="text-xl font-semibold mb-6">Valuation Timeline</h2>
          {historicalSnapshots.length ? (
            <div className="h-64 flex items-end gap-2">
              {historicalSnapshots
                .slice()
                .reverse()
                .map((snap) => {
                  const v = (snap.ev_low + snap.ev_high) / 2
                  const max = Math.max(...historicalSnapshots.map((s) => (s.ev_low + s.ev_high) / 2))
                  const pct = max > 0 ? (v / max) * 100 : 0
                  return (
                    <div key={snap.id} className="flex-1 flex flex-col items-center">
                      <div
                        className="w-full rounded-t bg-emerald-500/20"
                        style={{ height: `${Math.max(8, pct)}%` }}
                        title={`${formatDate(snap.as_of_date)}: ${formatCurrency(v)}`}
                      />
                      <div className="text-[10px] text-slate-500 mt-2">{formatDate(snap.as_of_date)}</div>
                    </div>
                  )
                })}
            </div>
          ) : (
            <div className="text-slate-400 text-center py-10">No historical snapshots yet.</div>
          )}
        </div>
      </div>
    </div>
  )
}

