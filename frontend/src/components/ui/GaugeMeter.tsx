import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'

interface GaugeMeterProps {
  value: number
  min: number
  max: number
  label?: string
  formatValue?: (value: number) => string
  gradientFrom?: string
  gradientTo?: string
  size?: 'sm' | 'md' | 'lg'
}

export function GaugeMeter({
  value,
  min,
  max,
  label,
  formatValue = (v) => v.toLocaleString(),
  gradientFrom = '#f59e0b',
  gradientTo = '#10b981',
  size = 'lg',
}: GaugeMeterProps) {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const percentage = Math.min(100, Math.max(0, ((value - min) / (max - min)) * 100))
  const angle = (percentage / 100) * 180 - 90 // -90 to 90 degrees

  const sizeConfig = {
    sm: { width: 160, height: 100, strokeWidth: 8, fontSize: 'text-lg' },
    md: { width: 240, height: 140, strokeWidth: 12, fontSize: 'text-2xl' },
    lg: { width: 320, height: 180, strokeWidth: 16, fontSize: 'text-4xl' },
  }

  const config = sizeConfig[size]
  const radius = (config.width - config.strokeWidth) / 2
  const circumference = Math.PI * radius

  return (
    <div className="relative flex flex-col items-center">
      <svg
        width={config.width}
        height={config.height}
        viewBox={`0 0 ${config.width} ${config.height + 10}`}
        className="overflow-visible"
      >
        <defs>
          <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor={gradientFrom} />
            <stop offset="100%" stopColor={gradientTo} />
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <filter id="shadow">
            <feDropShadow dx="0" dy="2" stdDeviation="4" floodOpacity="0.3" />
          </filter>
        </defs>

        {/* Background arc */}
        <path
          d={`M ${config.strokeWidth / 2} ${config.height} A ${radius} ${radius} 0 0 1 ${config.width - config.strokeWidth / 2} ${config.height}`}
          fill="none"
          stroke="rgba(100, 116, 139, 0.2)"
          strokeWidth={config.strokeWidth}
          strokeLinecap="round"
        />

        {/* Animated progress arc */}
        <motion.path
          d={`M ${config.strokeWidth / 2} ${config.height} A ${radius} ${radius} 0 0 1 ${config.width - config.strokeWidth / 2} ${config.height}`}
          fill="none"
          stroke="url(#gaugeGradient)"
          strokeWidth={config.strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: mounted ? circumference * (1 - percentage / 100) : circumference }}
          transition={{ duration: 1.5, ease: 'easeOut' }}
          filter="url(#glow)"
        />

        {/* Needle */}
        <motion.g
          initial={{ rotate: -90 }}
          animate={{ rotate: mounted ? angle : -90 }}
          transition={{ duration: 1.5, ease: 'easeOut' }}
          style={{ transformOrigin: `${config.width / 2}px ${config.height}px` }}
        >
          <line
            x1={config.width / 2}
            y1={config.height}
            x2={config.width / 2}
            y2={config.height - radius + 20}
            stroke="white"
            strokeWidth="3"
            strokeLinecap="round"
            filter="url(#shadow)"
          />
          <circle
            cx={config.width / 2}
            cy={config.height}
            r="8"
            fill="white"
            filter="url(#shadow)"
          />
        </motion.g>

        {/* Min/Max labels */}
        <text x={config.strokeWidth} y={config.height + 20} className="fill-slate-500 text-xs">
          {formatValue(min)}
        </text>
        <text
          x={config.width - config.strokeWidth}
          y={config.height + 20}
          textAnchor="end"
          className="fill-slate-500 text-xs"
        >
          {formatValue(max)}
        </text>
      </svg>

      {/* Value display */}
      <div className="absolute bottom-0 text-center">
        <motion.div
          className={`font-bold ${config.fontSize} text-white`}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.5 }}
        >
          {formatValue(value)}
        </motion.div>
        {label && (
          <motion.div
            className="text-sm text-slate-400 mt-1"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.7, duration: 0.5 }}
          >
            {label}
          </motion.div>
        )}
      </div>
    </div>
  )
}
