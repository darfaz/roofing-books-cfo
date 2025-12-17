import { useEffect, useMemo, useState } from 'react'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

type RoadmapStatus = 'pending' | 'in_progress' | 'completed'

type RoadmapItem = {
  id: string
  driver_key: string | null
  title: string
  description?: string | null
  expected_impact_ev: number
  effort_level?: 'low' | 'medium' | 'high' | null
  status: RoadmapStatus
}

type RoadmapResponse = {
  success: boolean
  data: { items: RoadmapItem[]; spec_jam_due: boolean }
}

const DRIVER_LABELS: Record<string, string> = {
  management_independence: 'Management Independence',
  financial_records: 'Financial Records',
  recurring_revenue: 'Recurring Revenue',
  operational_systems: 'Operational Systems',
  customer_diversity: 'Customer Diversity',
  market_outlook: 'Market Outlook',
}

const statusBadge = (status: RoadmapStatus): string => {
  switch (status) {
    case 'completed':
      return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30'
    case 'in_progress':
      return 'text-blue-400 bg-blue-500/10 border-blue-500/30'
    case 'pending':
    default:
      return 'text-slate-400 bg-slate-500/10 border-slate-500/30'
  }
}

const effortLabel = (e?: RoadmapItem['effort_level']) => {
  if (!e) return '—'
  if (e === 'low') return 'Low'
  if (e === 'medium') return 'Med'
  return 'High'
}

export function ValuationRoadmap({ accessToken }: { accessToken: string }) {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [items, setItems] = useState<RoadmapItem[]>([])
  const [specJamDue, setSpecJamDue] = useState(false)
  const [updatingId, setUpdatingId] = useState<string | null>(null)

  const authHeaders = useMemo(
    () => ({
      Authorization: `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    }),
    [accessToken],
  )

  const fetchRoadmap = async () => {
    const res = await fetch(`${API_BASE_URL}/api/valuation/roadmap`, { headers: authHeaders })
    const json = (await res.json()) as RoadmapResponse
    if (!json.success) throw new Error('Failed to load roadmap')
    setItems(json.data.items || [])
    setSpecJamDue(!!json.data.spec_jam_due)
  }

  useEffect(() => {
    void (async () => {
      try {
        setLoading(true)
        setError(null)
        await fetchRoadmap()
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Failed to load roadmap')
      } finally {
        setLoading(false)
      }
    })()
  }, [authHeaders])

  const formatCurrency = (value: number): string =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value)

  const nextTwo = useMemo(() => {
    const candidates = items.filter((i) => i.status === 'pending')
    candidates.sort((a, b) => (b.expected_impact_ev || 0) - (a.expected_impact_ev || 0))
    return candidates.slice(0, 2)
  }, [items])

  const grouped = useMemo(() => {
    const map = new Map<string, RoadmapItem[]>()
    for (const it of items) {
      const key = it.driver_key || 'other'
      if (!map.has(key)) map.set(key, [])
      map.get(key)!.push(it)
    }
    for (const [k, arr] of map) {
      arr.sort((a, b) => {
        const score = (x: RoadmapItem) => (x.status === 'in_progress' ? 2 : x.status === 'pending' ? 1 : 0)
        const s = score(b) - score(a)
        if (s !== 0) return s
        return (b.expected_impact_ev || 0) - (a.expected_impact_ev || 0)
      })
      map.set(k, arr)
    }
    return map
  }, [items])

  const patchStatus = async (id: string, status: RoadmapStatus) => {
    const res = await fetch(`${API_BASE_URL}/api/valuation/roadmap/${id}`, {
      method: 'PATCH',
      headers: authHeaders,
      body: JSON.stringify({ status }),
    })
    const json = await res.json()
    if (!res.ok || !json?.success) throw new Error(json?.detail?.error?.message || 'Failed to update status')
  }

  const actionButton = (args: { label: string; onClick: () => void; variant: 'primary' | 'secondary' | 'danger'; disabled?: boolean }) => {
    const base = 'text-sm font-medium px-3 py-1.5 rounded-lg transition disabled:opacity-60'
    const cls =
      args.variant === 'primary'
        ? 'bg-emerald-500 hover:bg-emerald-400 text-black'
        : args.variant === 'danger'
          ? 'bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 text-red-300'
          : 'bg-slate-800 hover:bg-slate-700 text-white'
    return (
      <button onClick={args.onClick} disabled={args.disabled} className={`${base} ${cls}`}>
        {args.label}
      </button>
    )
  }

  if (loading) {
    return (
      <div className="bg-slate-900 rounded-xl p-8 border border-slate-800">
        <div className="text-slate-400">Loading roadmap…</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-slate-900 rounded-xl p-8 border border-slate-800">
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-red-300 text-sm">{error}</div>
      </div>
    )
  }

  return (
    <div className="bg-slate-900 rounded-xl p-8 border border-slate-800">
      <div className="flex items-start justify-between gap-4 mb-6">
        <div>
          <h2 className="text-xl font-semibold">Valuation Roadmap</h2>
          <p className="text-slate-400 mt-1">Prioritized improvements to increase enterprise value.</p>
        </div>
        <button
          onClick={() => void fetchRoadmap()}
          className="bg-slate-800 hover:bg-slate-700 text-white font-medium px-4 py-2 rounded-lg transition"
        >
          Refresh
        </button>
      </div>

      {/* Next 2 Improvements */}
      <div className="mb-6">
        <div className="text-sm text-slate-400 mb-3">Next 2 Improvements</div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {nextTwo.length ? (
            nextTwo.map((it) => (
              <div key={it.id} className="bg-slate-800 rounded-xl p-6 border border-slate-700/60">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="font-semibold text-lg">{it.title}</div>
                    <div className="text-sm text-slate-400 mt-2">
                      Expected EV impact: <span className="text-slate-200 font-semibold">{formatCurrency(it.expected_impact_ev)}</span>
                    </div>
                    <div className="text-sm text-slate-400 mt-1">
                      Effort: <span className="text-slate-200 font-semibold">{effortLabel(it.effort_level)}</span>
                    </div>
                  </div>
                  <button
                    disabled={updatingId === it.id}
                    onClick={() => {
                      void (async () => {
                        try {
                          setUpdatingId(it.id)
                          await patchStatus(it.id, 'in_progress')
                          await fetchRoadmap()
                        } catch (e) {
                          setError(e instanceof Error ? e.message : 'Failed to start item')
                        } finally {
                          setUpdatingId(null)
                        }
                      })()
                    }}
                    className="bg-emerald-500 hover:bg-emerald-400 disabled:opacity-60 disabled:hover:bg-emerald-500 text-black font-semibold px-4 py-2 rounded-lg transition"
                  >
                    Start
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className="text-slate-400">No pending items.</div>
          )}
        </div>
      </div>

      {/* Spec Jam reminder */}
      {specJamDue && (
        <div className="mb-6 bg-amber-500/10 border border-amber-500/30 rounded-xl p-6">
          <div className="font-semibold text-amber-300">Quarterly Spec Jam due</div>
          <div className="text-sm text-amber-200/80 mt-1">
            Schedule a quarterly “Spec Jam” to refresh systems/process specs and ensure the deal room stays buyer-ready.
          </div>
        </div>
      )}

      {/* Full roadmap grouped by driver */}
      <div>
        <div className="text-sm text-slate-400 mb-3">Roadmap</div>
        <div className="space-y-4">
          {Array.from(grouped.entries()).map(([driverKey, arr]) => (
            <div key={driverKey} className="bg-slate-800 rounded-xl p-6 border border-slate-700/60">
              <div className="font-semibold mb-4">{DRIVER_LABELS[driverKey] || 'Other'}</div>
              <div className="space-y-3">
                {arr.map((it) => (
                  <div key={it.id} className="bg-slate-900 rounded-lg p-4 border border-slate-800">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <div className="font-medium">{it.title}</div>
                        {it.description ? <div className="text-sm text-slate-400 mt-1">{it.description}</div> : null}
                        <div className="text-sm text-slate-400 mt-2">
                          EV impact:{' '}
                          <span className="text-slate-200 font-semibold tabular-nums">{formatCurrency(it.expected_impact_ev)}</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className={`px-3 py-1 rounded-lg border text-xs ${statusBadge(it.status)}`}>{it.status}</div>
                        {it.status !== 'completed' ? (
                          <>
                            {it.status === 'pending'
                              ? actionButton({
                                  label: 'Start',
                                  variant: 'primary',
                                  disabled: updatingId === it.id,
                                  onClick: () => {
                                    void (async () => {
                                      try {
                                        setUpdatingId(it.id)
                                        await patchStatus(it.id, 'in_progress')
                                        await fetchRoadmap()
                                      } catch (e) {
                                        setError(e instanceof Error ? e.message : 'Failed to start item')
                                      } finally {
                                        setUpdatingId(null)
                                      }
                                    })()
                                  },
                                })
                              : null}
                            {actionButton({
                              label: 'Mark Completed',
                              variant: 'secondary',
                              disabled: updatingId === it.id,
                              onClick: () => {
                                void (async () => {
                                  try {
                                    setUpdatingId(it.id)
                                    await patchStatus(it.id, 'completed')
                                    await fetchRoadmap()
                                  } catch (e) {
                                    setError(e instanceof Error ? e.message : 'Failed to complete item')
                                  } finally {
                                    setUpdatingId(null)
                                  }
                                })()
                              },
                            })}
                          </>
                        ) : null}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}


