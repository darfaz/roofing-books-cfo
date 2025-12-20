import React, { useState, useEffect } from 'react';

// Types
interface ValuationSnapshot {
  id: string;
  tenant_id: string;
  as_of_date: string;
  ttm_revenue: number;
  ttm_sde: number;
  ttm_ebitda: number;
  tier: 'below_avg' | 'avg' | 'above_avg';
  multiple_low: number;
  multiple_high: number;
  ev_low: number;
  ev_high: number;
  confidence_score: number;
  drivers_json?: Record<string, number>;
  created_at: string;
  updated_at: string;
}

interface DriverScore {
  id: string;
  driver_key: string;
  score: number; // 0-100
  confidence: number;
  computed_by: string;
  as_of_date: string;
}

interface DriverScoresResponse {
  success: boolean;
  data: {
    scores: DriverScore[];
    overall_score: number;
    tier_impact: string;
  };
}

interface ValuationSnapshotResponse {
  success: boolean;
  data: {
    snapshot: ValuationSnapshot;
  };
}

// Driver labels
const DRIVER_LABELS: Record<string, { label: string; icon: string; description: string }> = {
  management_independence: {
    label: 'Management Independence',
    icon: '👔',
    description: 'Reduced owner dependency'
  },
  financial_records: {
    label: 'Financial Records',
    icon: '📊',
    description: 'Clean, organized books'
  },
  recurring_revenue: {
    label: 'Recurring Revenue',
    icon: '🔄',
    description: 'Predictable income streams'
  },
  operational_systems: {
    label: 'Operational Systems',
    icon: '⚙️',
    description: 'Systematized processes'
  },
  customer_diversity: {
    label: 'Customer Diversity',
    icon: '👥',
    description: 'Low concentration risk'
  },
  market_outlook: {
    label: 'Market Outlook',
    icon: '📈',
    description: 'Favorable market conditions'
  }
};

// API base URL (adjust based on your setup)
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

interface ValuationDashboardProps {
  tenantId: string;
  apiBaseUrl?: string;
}

const ValuationDashboard: React.FC<ValuationDashboardProps> = ({ 
  tenantId, 
  apiBaseUrl = API_BASE_URL 
}) => {
  const [snapshot, setSnapshot] = useState<ValuationSnapshot | null>(null);
  const [driverScores, setDriverScores] = useState<DriverScore[]>([]);
  const [historicalSnapshots, setHistoricalSnapshots] = useState<ValuationSnapshot[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchValuationData();
  }, [tenantId, apiBaseUrl]);

  const fetchValuationData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch latest snapshot
      const snapshotRes = await fetch(`${apiBaseUrl}/api/valuation/snapshot?tenant_id=${tenantId}`);
      const snapshotData: ValuationSnapshotResponse = await snapshotRes.json();
      
      if (snapshotData.success && snapshotData.data.snapshot) {
        setSnapshot(snapshotData.data.snapshot);
      }

      // Fetch driver scores
      const driversRes = await fetch(`${apiBaseUrl}/api/valuation/drivers?tenant_id=${tenantId}`);
      const driversData: DriverScoresResponse = await driversRes.json();
      
      if (driversData.success && driversData.data.scores) {
        setDriverScores(driversData.data.scores);
      }

      // Fetch historical snapshots for timeline
      const historicalRes = await fetch(
        `${apiBaseUrl}/api/valuation/snapshots?tenant_id=${tenantId}&limit=12`
      );
      const historicalData = await historicalRes.json();
      
      if (historicalData.success && historicalData.data.snapshots) {
        setHistoricalSnapshots(historicalData.data.snapshots);
      }
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load valuation data');
      console.error('Error fetching valuation data:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const getTierColor = (tier: string): string => {
    switch (tier) {
      case 'above_avg':
        return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
      case 'avg':
        return 'text-blue-400 bg-blue-500/10 border-blue-500/30';
      case 'below_avg':
        return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
      default:
        return 'text-slate-400 bg-slate-500/10 border-slate-500/30';
    }
  };

  const getTierLabel = (tier: string): string => {
    switch (tier) {
      case 'above_avg':
        return 'Above Average';
      case 'avg':
        return 'Average';
      case 'below_avg':
        return 'Below Average';
      default:
        return tier;
    }
  };

  const getScoreColor = (score: number): string => {
    if (score >= 80) return 'text-emerald-400';
    if (score >= 60) return 'text-blue-400';
    if (score >= 40) return 'text-amber-400';
    return 'text-red-400';
  };

  const getScoreBgColor = (score: number): string => {
    if (score >= 80) return 'bg-emerald-500/20';
    if (score >= 60) return 'bg-blue-500/20';
    if (score >= 40) return 'bg-amber-500/20';
    return 'bg-red-500/20';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 text-white p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="text-slate-400">Loading valuation data...</div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-950 text-white p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-red-400">
            Error: {error}
          </div>
        </div>
      </div>
    );
  }

  if (!snapshot) {
    return (
      <div className="min-h-screen bg-slate-950 text-white p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-slate-900 rounded-xl p-8 border border-slate-800 text-center">
            <h2 className="text-2xl font-bold mb-4">No Valuation Data Available</h2>
            <p className="text-slate-400 mb-6">
              Create your first valuation snapshot to see your business valuation.
            </p>
            <button
              onClick={fetchValuationData}
              className="bg-emerald-500 hover:bg-emerald-400 text-black font-semibold px-6 py-3 rounded-lg transition"
            >
              Calculate Valuation
            </button>
          </div>
        </div>
      </div>
    );
  }

  const avgValue = (snapshot.ev_low + snapshot.ev_high) / 2;
  const valueRange = snapshot.ev_high - snapshot.ev_low;

  return (
    <div className="min-h-screen bg-slate-950 text-white p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Valuation Dashboard</h1>
            <p className="text-slate-400">
              As of {formatDate(snapshot.as_of_date)}
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className={`px-4 py-2 rounded-lg border ${getTierColor(snapshot.tier)}`}>
              <div className="text-xs text-slate-400 mb-1">Tier</div>
              <div className="font-semibold">{getTierLabel(snapshot.tier)}</div>
            </div>
            <button
              onClick={fetchValuationData}
              className="bg-slate-800 hover:bg-slate-700 text-white font-medium px-4 py-2 rounded-lg transition"
            >
              Refresh
            </button>
          </div>
        </div>

        {/* Valuation Meter */}
        <div className="bg-slate-900 rounded-xl p-8 border border-slate-800">
          <h2 className="text-xl font-semibold mb-6">Estimated Enterprise Value</h2>
          
          <div className="relative">
            {/* Value Range Bar */}
            <div className="relative h-24 bg-slate-800 rounded-lg overflow-hidden mb-6">
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-4xl font-bold">{formatCurrency(avgValue)}</div>
                  <div className="text-sm text-slate-400 mt-1">
                    {formatCurrency(snapshot.ev_low)} - {formatCurrency(snapshot.ev_high)}
                  </div>
                </div>
              </div>
              
              {/* Gradient bar representing range */}
              <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r from-amber-500 via-emerald-500 to-emerald-400 opacity-30"></div>
              
              {/* Low marker */}
              <div className="absolute bottom-0 left-0 w-1 h-full bg-amber-400"></div>
              
              {/* High marker */}
              <div className="absolute bottom-0 right-0 w-1 h-full bg-emerald-400"></div>
              
              {/* Average marker */}
              <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-1 h-full bg-white"></div>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-slate-800 rounded-lg p-4">
                <div className="text-sm text-slate-400 mb-1">TTM Revenue</div>
                <div className="text-xl font-bold">{formatCurrency(snapshot.ttm_revenue)}</div>
              </div>
              <div className="bg-slate-800 rounded-lg p-4">
                <div className="text-sm text-slate-400 mb-1">TTM SDE</div>
                <div className="text-xl font-bold">{formatCurrency(snapshot.ttm_sde)}</div>
              </div>
              <div className="bg-slate-800 rounded-lg p-4">
                <div className="text-sm text-slate-400 mb-1">TTM EBITDA</div>
                <div className="text-xl font-bold">{formatCurrency(snapshot.ttm_ebitda)}</div>
              </div>
              <div className="bg-slate-800 rounded-lg p-4">
                <div className="text-sm text-slate-400 mb-1">Multiple Range</div>
                <div className="text-xl font-bold">
                  {snapshot.multiple_low}x - {snapshot.multiple_high}x
                </div>
              </div>
            </div>

            {/* Confidence Score */}
            <div className="mt-6 pt-6 border-t border-slate-800">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm text-slate-400">Confidence Score</div>
                <div className={`font-semibold ${getScoreColor(snapshot.confidence_score)}`}>
                  {snapshot.confidence_score}%
                </div>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all ${getScoreBgColor(snapshot.confidence_score)}`}
                  style={{ width: `${snapshot.confidence_score}%` }}
                ></div>
              </div>
              {snapshot.confidence_score < 80 && (
                <div className="text-amber-400 text-sm mt-2">
                  ⚠️ Review recommended (confidence below 80%)
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Driver Scorecards */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Value Driver Scores</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(DRIVER_LABELS).map(([key, { label, icon, description }]) => {
              const driverScore = driverScores.find(d => d.driver_key === key);
              const score = driverScore?.score || 0;
              const scorePercent = score; // Already 0-100

              return (
                <div
                  key={key}
                  className="bg-slate-900 rounded-xl p-6 border border-slate-800 hover:border-slate-700 transition"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <div className="text-3xl mb-2">{icon}</div>
                      <h3 className="font-semibold text-lg mb-1">{label}</h3>
                      <p className="text-sm text-slate-400">{description}</p>
                    </div>
                  </div>

                  {/* Score Display */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-slate-400">Score</span>
                      <span className={`text-2xl font-bold ${getScoreColor(scorePercent)}`}>
                        {scorePercent}
                      </span>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full bg-slate-800 rounded-full h-3">
                      <div
                        className={`h-3 rounded-full transition-all ${getScoreBgColor(scorePercent)}`}
                        style={{ width: `${scorePercent}%` }}
                      ></div>
                    </div>

                    {/* Confidence Badge */}
                    {driverScore && (
                      <div className="text-xs text-slate-500 mt-2">
                        Confidence: {driverScore.confidence}%
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Value Timeline */}
        <div className="bg-slate-900 rounded-xl p-8 border border-slate-800">
          <h2 className="text-xl font-semibold mb-6">Valuation Timeline</h2>
          
          {historicalSnapshots.length > 0 ? (
            <div className="relative">
              {/* Timeline Chart */}
              <div className="h-64 flex items-end justify-between gap-2">
                {historicalSnapshots.map((snap, index) => {
                  const avgVal = (snap.ev_low + snap.ev_high) / 2;
                  const maxVal = Math.max(...historicalSnapshots.map(s => (s.ev_low + s.ev_high) / 2));
                  const heightPercent = (avgVal / maxVal) * 100;

                  return (
                    <div
                      key={snap.id}
                      className="flex-1 flex flex-col items-center group cursor-pointer"
                    >
                      {/* Bar */}
                      <div
                        className={`w-full rounded-t transition-all hover:opacity-80 ${getTierColor(snap.tier).split(' ')[1]}`}
                        style={{ height: `${heightPercent}%`, minHeight: '20px' }}
                        title={`${formatDate(snap.as_of_date)}: ${formatCurrency(avgVal)}`}
                      ></div>
                      
                      {/* Date Label */}
                      <div className="text-xs text-slate-400 mt-2 transform -rotate-45 origin-top-left whitespace-nowrap opacity-0 group-hover:opacity-100 transition">
                        {formatDate(snap.as_of_date)}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Legend */}
              <div className="flex items-center justify-center gap-6 mt-6 pt-6 border-t border-slate-800">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-amber-500/20 border border-amber-500/30 rounded"></div>
                  <span className="text-sm text-slate-400">Below Avg</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-blue-500/20 border border-blue-500/30 rounded"></div>
                  <span className="text-sm text-slate-400">Average</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-emerald-500/20 border border-emerald-500/30 rounded"></div>
                  <span className="text-sm text-slate-400">Above Avg</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-slate-400">
              <p>No historical data available yet.</p>
              <p className="text-sm mt-2">
                Valuation snapshots will appear here as you track your business value over time.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ValuationDashboard;





