import { motion } from 'framer-motion'
import { Area, AreaChart, ResponsiveContainer, Tooltip, YAxis } from 'recharts'

interface SparklineProps {
  data: { value: number; label?: string }[]
  color?: string
  height?: number
  showTooltip?: boolean
  showArea?: boolean
  animate?: boolean
}

export function Sparkline({
  data,
  color = '#10b981',
  height = 60,
  showTooltip = true,
  showArea = true,
  animate = true,
}: SparklineProps) {
  const minValue = Math.min(...data.map((d) => d.value))
  const maxValue = Math.max(...data.map((d) => d.value))
  const padding = (maxValue - minValue) * 0.1

  return (
    <motion.div
      style={{ height }}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 5, right: 5, bottom: 5, left: 5 }}>
          <defs>
            <linearGradient id={`sparklineGradient-${color.replace('#', '')}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={color} stopOpacity={0.4} />
              <stop offset="100%" stopColor={color} stopOpacity={0} />
            </linearGradient>
          </defs>
          <YAxis domain={[minValue - padding, maxValue + padding]} hide />
          {showTooltip && (
            <Tooltip
              content={({ payload }) => {
                if (!payload || !payload[0]) return null
                const data = payload[0].payload as { value: number; label?: string }
                return (
                  <div className="bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs shadow-lg">
                    {data.label && <div className="text-slate-400">{data.label}</div>}
                    <div className="text-white font-semibold">
                      {new Intl.NumberFormat('en-US', {
                        style: 'currency',
                        currency: 'USD',
                        minimumFractionDigits: 0,
                        maximumFractionDigits: 0,
                      }).format(data.value)}
                    </div>
                  </div>
                )
              }}
            />
          )}
          <Area
            type="monotone"
            dataKey="value"
            stroke={color}
            strokeWidth={2}
            fill={showArea ? `url(#sparklineGradient-${color.replace('#', '')})` : 'transparent'}
            isAnimationActive={animate}
            animationDuration={1500}
            animationEasing="ease-out"
          />
        </AreaChart>
      </ResponsiveContainer>
    </motion.div>
  )
}

interface MiniChartCardProps {
  title: string
  value: string | number
  data: { value: number; label?: string }[]
  trend?: 'up' | 'down' | 'neutral'
  trendValue?: string
  color?: string
}

export function MiniChartCard({ title, value, data, trend, trendValue, color = '#10b981' }: MiniChartCardProps) {
  const trendColors = {
    up: 'text-emerald-400',
    down: 'text-red-400',
    neutral: 'text-slate-400',
  }

  return (
    <motion.div
      className="bg-slate-900/80 border border-slate-700/50 rounded-xl p-4 backdrop-blur-sm"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <div className="flex items-start justify-between mb-2">
        <div>
          <div className="text-sm text-slate-400">{title}</div>
          <div className="text-xl font-bold text-white mt-1">{value}</div>
        </div>
        {trend && trendValue && (
          <div className={`text-sm font-medium ${trendColors[trend]}`}>
            {trend === 'up' ? '+' : trend === 'down' ? '' : ''}
            {trendValue}
          </div>
        )}
      </div>
      <Sparkline data={data} color={color} height={50} showTooltip={false} />
    </motion.div>
  )
}
