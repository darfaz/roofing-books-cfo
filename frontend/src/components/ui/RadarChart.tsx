import { motion } from 'framer-motion'
import {
  Radar,
  RadarChart as RechartsRadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from 'recharts'

interface RadarDataPoint {
  subject: string
  value: number
  fullMark: number
  icon?: string
}

interface RadarChartProps {
  data: RadarDataPoint[]
  color?: string
  fillOpacity?: number
  showTooltip?: boolean
  animate?: boolean
}

export function RadarChart({
  data,
  color = '#10b981',
  fillOpacity = 0.3,
  showTooltip = true,
  animate = true,
}: RadarChartProps) {
  return (
    <motion.div
      className="w-full h-full"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      <ResponsiveContainer width="100%" height="100%">
        <RechartsRadarChart cx="50%" cy="50%" outerRadius="70%" data={data}>
          <PolarGrid stroke="rgba(148, 163, 184, 0.2)" />
          <PolarAngleAxis
            dataKey="subject"
            tick={{ fill: '#94a3b8', fontSize: 12 }}
            tickLine={false}
          />
          <PolarRadiusAxis
            angle={30}
            domain={[0, 100]}
            tick={{ fill: '#64748b', fontSize: 10 }}
            tickCount={5}
            axisLine={false}
          />
          <Radar
            name="Score"
            dataKey="value"
            stroke={color}
            fill={color}
            fillOpacity={fillOpacity}
            strokeWidth={2}
            isAnimationActive={animate}
            animationDuration={1500}
            animationEasing="ease-out"
          />
          {showTooltip && (
            <Tooltip
              content={({ payload }) => {
                if (!payload || !payload[0]) return null
                const data = payload[0].payload as RadarDataPoint
                return (
                  <div className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 shadow-xl">
                    <div className="flex items-center gap-2">
                      {data.icon && <span>{data.icon}</span>}
                      <span className="text-white font-medium">{data.subject}</span>
                    </div>
                    <div className="text-emerald-400 font-bold text-lg mt-1">{data.value}/100</div>
                  </div>
                )
              }}
            />
          )}
        </RechartsRadarChart>
      </ResponsiveContainer>
    </motion.div>
  )
}
