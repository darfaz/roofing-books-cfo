import { useEffect, useMemo, useRef, useState } from 'react'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

type Levers = {
  recurring_revenue_delta: number // -0.20 .. +1.00 (fraction)
  margin_delta: number // -0.05 .. +0.10 (fraction points)
  owner_hours_delta: number // negative hours (new - current)
  productivity_delta: number // -0.10 .. +0.20 (fraction)
}

type SimulationResponse = {
  projected_ebitda: number
  projected_multiple: number
  projected_ev_low: number
  projected_ev_high: number
}

export function ScenarioSimulator(props: {
  accessToken: string
  currentEbitda: number
  currentMultiple: number
  currentEvLow: number
  currentEvHigh: number
  currentOwnerHoursPerWeek?: number
}) {
  const currentOwnerHours = Math.max(0, props.currentOwnerHoursPerWeek ?? 40)

  const [recurringRevenueDeltaPct, setRecurringRevenueDeltaPct] = useState(0) // -20..100
  const [marginDeltaPctPts, setMarginDeltaPctPts] = useState(0) // -5..10
  const [ownerHoursPerWeek, setOwnerHoursPerWeek] = useState(currentOwnerHours) // current..0
  const [productivityDeltaPct, setProductivityDeltaPct] = useState(0) // -10..20

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<SimulationResponse | null>(null)

  const authHeaders = useMemo(
    () => ({
      Authorization: `Bearer ${props.accessToken}`,
      'Content-Type': 'application/json',
    }),
    [props.accessToken],
  )

  const levers: Levers = useMemo(
    () => ({
      recurring_revenue_delta: recurringRevenueDeltaPct / 100,
      margin_delta: marginDeltaPctPts / 100,
      owner_hours_delta: ownerHoursPerWeek - currentOwnerHours,
      productivity_delta: productivityDeltaPct / 100,
    }),
    [recurringRevenueDeltaPct, marginDeltaPctPts, ownerHoursPerWeek, productivityDeltaPct, currentOwnerHours],
  )

  const debounceRef = useRef<number | null>(null)

  useEffect(() => {
    // debounce API calls for slider drags
    if (debounceRef.current) window.clearTimeout(debounceRef.current)
    debounceRef.current = window.setTimeout(() => {
      void (async () => {
        try {
          setLoading(true)
          setError(null)

          const res = await fetch(`${API_BASE_URL}/api/valuation/simulate`, {
            method: 'POST',
            headers: authHeaders,
            body: JSON.stringify({ levers }),
          })

          if (!res.ok) {
            const text = await res.text()
            throw new Error(text || `HTTP ${res.status}`)
          }

          const json = (await res.json()) as SimulationResponse
          setResult(json)
        } catch (e) {
          setError(e instanceof Error ? e.message : 'Failed to simulate scenario')
          setResult(null)
        } finally {
          setLoading(false)
        }
      })()
    }, 250)

    return () => {
      if (debounceRef.current) window.clearTimeout(debounceRef.current)
    }
  }, [levers, authHeaders])

  const formatCurrency = (value: number): string =>
    new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value)

  const formatSignedCurrency = (value: number): string => `${value >= 0 ? '+' : ''}${formatCurrency(value)}`
  const formatSignedNumber = (value: number, suffix = ''): string => `${value >= 0 ? '+' : ''}${value.toFixed(2)}${suffix}`

  const currentEvAvg = (props.currentEvLow + props.currentEvHigh) / 2
  const projectedEvAvg = result ? (result.projected_ev_low + result.projected_ev_high) / 2 : null

  const ebitdaDelta = result ? result.projected_ebitda - props.currentEbitda : null
  const multipleDelta = result ? result.projected_multiple - props.currentMultiple : null
  const evDelta = projectedEvAvg != null ? projectedEvAvg - currentEvAvg : null

  const reset = () => {
    setRecurringRevenueDeltaPct(0)
    setMarginDeltaPctPts(0)
    setOwnerHoursPerWeek(currentOwnerHours)
    setProductivityDeltaPct(0)
  }

  const saveScenario = () => {
    const payload = {
      saved_at: new Date().toISOString(),
      levers,
      result,
    }
    const key = 'crewcfo.saved_scenarios'
    const existing = (() => {
      try {
        return JSON.parse(localStorage.getItem(key) || '[]') as unknown[]
      } catch {
        return []
      }
    })()
    localStorage.setItem(key, JSON.stringify([payload, ...existing].slice(0, 50)))
  }

  const sliderRow = (args: {
    label: string
    subtitle: string
    valueLabel: string
    min: number
    max: number
    step: number
    value: number
    onChange: (v: number) => void
  }) => (
    <div className="bg-slate-800 rounded-lg p-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="font-medium">{args.label}</div>
          <div className="text-sm text-slate-400 mt-1">{args.subtitle}</div>
        </div>
        <div className="text-sm font-semibold text-slate-200 tabular-nums">{args.valueLabel}</div>
      </div>
      <input
        type="range"
        min={args.min}
        max={args.max}
        step={args.step}
        value={args.value}
        onChange={(e) => args.onChange(Number(e.target.value))}
        className="mt-4 w-full accent-emerald-400"
      />
      <div className="mt-2 flex justify-between text-[11px] text-slate-500">
        <span>{args.min}</span>
        <span>{args.max}</span>
      </div>
    </div>
  )

  return (
    <div className="bg-slate-900 rounded-xl p-8 border border-slate-800">
      <div className="flex items-start justify-between gap-4 mb-6">
        <div>
          <h2 className="text-xl font-semibold">Scenario Simulator</h2>
          <p className="text-slate-400 mt-1">Adjust “what-if” levers and see projected valuation impacts in real time.</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={reset}
            className="bg-slate-800 hover:bg-slate-700 text-white font-medium px-4 py-2 rounded-lg transition"
          >
            Reset
          </button>
          <button
            onClick={saveScenario}
            className="bg-emerald-500 hover:bg-emerald-400 text-black font-semibold px-4 py-2 rounded-lg transition"
          >
            Save Scenario
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Levers */}
        <div className="space-y-4">
          {sliderRow({
            label: 'Recurring Revenue Change',
            subtitle: 'Impact on predictable income streams',
            valueLabel: `${recurringRevenueDeltaPct >= 0 ? '+' : ''}${recurringRevenueDeltaPct}%`,
            min: -20,
            max: 100,
            step: 1,
            value: recurringRevenueDeltaPct,
            onChange: setRecurringRevenueDeltaPct,
          })}

          {sliderRow({
            label: 'Gross Margin Change',
            subtitle: 'Change in margin (percentage points)',
            valueLabel: `${marginDeltaPctPts >= 0 ? '+' : ''}${marginDeltaPctPts.toFixed(1)} pts`,
            min: -5,
            max: 10,
            step: 0.5,
            value: marginDeltaPctPts,
            onChange: setMarginDeltaPctPts,
          })}

          {sliderRow({
            label: 'Owner Hours / Week',
            subtitle: `From current (${currentOwnerHours} hrs) down to 0`,
            valueLabel: `${ownerHoursPerWeek} hrs`,
            min: 0,
            max: currentOwnerHours,
            step: 1,
            value: ownerHoursPerWeek,
            onChange: setOwnerHoursPerWeek,
          })}

          {sliderRow({
            label: 'Crew Productivity',
            subtitle: 'Efficiency improvement or decline',
            valueLabel: `${productivityDeltaPct >= 0 ? '+' : ''}${productivityDeltaPct}%`,
            min: -10,
            max: 20,
            step: 1,
            value: productivityDeltaPct,
            onChange: setProductivityDeltaPct,
          })}
        </div>

        {/* Outputs */}
        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700/60">
          <div className="flex items-center justify-between mb-4">
            <div className="font-semibold">Projected Outputs</div>
            <div className="text-sm text-slate-400">{loading ? 'Simulating…' : error ? 'Error' : 'Live'}</div>
          </div>

          {error ? (
            <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-red-300 text-sm">{error}</div>
          ) : (
            <div className="space-y-4">
              <div className="bg-slate-900 rounded-lg p-4 border border-slate-800">
                <div className="text-sm text-slate-400">Projected EBITDA</div>
                <div className="mt-1 flex items-baseline justify-between gap-4">
                  <div className="text-2xl font-bold tabular-nums">
                    {result ? formatCurrency(result.projected_ebitda) : '—'}
                  </div>
                  <div className="text-sm text-slate-300 tabular-nums">
                    {ebitdaDelta == null ? '—' : `${formatSignedCurrency(ebitdaDelta)} vs current`}
                  </div>
                </div>
              </div>

              <div className="bg-slate-900 rounded-lg p-4 border border-slate-800">
                <div className="text-sm text-slate-400">Projected Multiple</div>
                <div className="mt-1 flex items-baseline justify-between gap-4">
                  <div className="text-2xl font-bold tabular-nums">{result ? `${result.projected_multiple}x` : '—'}</div>
                  <div className="text-sm text-slate-300 tabular-nums">
                    {multipleDelta == null ? '—' : `${formatSignedNumber(multipleDelta, 'x')} vs current`}
                  </div>
                </div>
              </div>

              <div className="bg-slate-900 rounded-lg p-4 border border-slate-800">
                <div className="text-sm text-slate-400">Projected Valuation Range</div>
                <div className="mt-1 flex items-baseline justify-between gap-4">
                  <div className="text-2xl font-bold tabular-nums">
                    {result ? `${formatCurrency(result.projected_ev_low)} - ${formatCurrency(result.projected_ev_high)}` : '—'}
                  </div>
                  <div className="text-sm text-slate-300 tabular-nums">
                    {evDelta == null ? '—' : `${formatSignedCurrency(evDelta)} avg`}
                  </div>
                </div>
              </div>
            </div>
          )}
          <div className="mt-5 pt-5 border-t border-slate-700/60 text-xs text-slate-500">
            Inputs are lever deltas; projections are computed from the latest snapshot. (This is a first-pass model; we can refine the math
            once you confirm the business rules.)
          </div>
        </div>
      </div>
    </div>
  )
}





