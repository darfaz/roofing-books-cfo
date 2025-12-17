import { motion } from 'framer-motion'
import type { HTMLMotionProps } from 'framer-motion'
import type { ReactNode } from 'react'

interface GlassCardProps extends Omit<HTMLMotionProps<'div'>, 'children'> {
  children: ReactNode
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info'
  glow?: boolean
  hover?: boolean
  padding?: 'sm' | 'md' | 'lg'
}

const variantStyles = {
  default: {
    border: 'border-slate-700/50',
    bg: 'bg-slate-900/80',
    glow: 'shadow-slate-500/10',
  },
  success: {
    border: 'border-emerald-500/30',
    bg: 'bg-emerald-950/30',
    glow: 'shadow-emerald-500/20',
  },
  warning: {
    border: 'border-amber-500/30',
    bg: 'bg-amber-950/30',
    glow: 'shadow-amber-500/20',
  },
  danger: {
    border: 'border-red-500/30',
    bg: 'bg-red-950/30',
    glow: 'shadow-red-500/20',
  },
  info: {
    border: 'border-blue-500/30',
    bg: 'bg-blue-950/30',
    glow: 'shadow-blue-500/20',
  },
}

const paddingStyles = {
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
}

export function GlassCard({
  children,
  variant = 'default',
  glow = false,
  hover = true,
  padding = 'md',
  className = '',
  ...props
}: GlassCardProps) {
  const styles = variantStyles[variant]

  return (
    <motion.div
      className={`
        rounded-xl border backdrop-blur-sm
        ${styles.border} ${styles.bg}
        ${glow ? `shadow-lg ${styles.glow}` : ''}
        ${hover ? 'hover:border-opacity-60 transition-colors duration-300' : ''}
        ${paddingStyles[padding]}
        ${className}
      `}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      whileHover={hover ? { scale: 1.01 } : undefined}
      {...props}
    >
      {children}
    </motion.div>
  )
}

interface MetricCardProps {
  label: string
  value: ReactNode
  subValue?: ReactNode
  icon?: ReactNode
  trend?: 'up' | 'down' | 'neutral'
  trendValue?: string
  variant?: GlassCardProps['variant']
}

export function MetricCard({
  label,
  value,
  subValue,
  icon,
  trend,
  trendValue,
  variant = 'default',
}: MetricCardProps) {
  const trendColors = {
    up: 'text-emerald-400',
    down: 'text-red-400',
    neutral: 'text-slate-400',
  }

  const trendIcons = {
    up: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
      </svg>
    ),
    down: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
      </svg>
    ),
    neutral: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14" />
      </svg>
    ),
  }

  return (
    <GlassCard variant={variant} padding="md">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="text-sm text-slate-400 mb-1">{label}</div>
          <div className="text-2xl font-bold text-white">{value}</div>
          {subValue && <div className="text-sm text-slate-500 mt-1">{subValue}</div>}
          {trend && trendValue && (
            <div className={`flex items-center gap-1 mt-2 text-sm ${trendColors[trend]}`}>
              {trendIcons[trend]}
              <span>{trendValue}</span>
            </div>
          )}
        </div>
        {icon && <div className="text-3xl">{icon}</div>}
      </div>
    </GlassCard>
  )
}

interface ProgressCardProps {
  label: string
  value: number
  maxValue?: number
  color?: 'emerald' | 'blue' | 'amber' | 'red'
  showPercentage?: boolean
  size?: 'sm' | 'md'
}

export function ProgressCard({
  label,
  value,
  maxValue = 100,
  color = 'emerald',
  showPercentage = true,
  size = 'md',
}: ProgressCardProps) {
  const percentage = Math.min(100, (value / maxValue) * 100)

  const colorStyles = {
    emerald: { bar: 'bg-emerald-500', glow: 'shadow-emerald-500/50' },
    blue: { bar: 'bg-blue-500', glow: 'shadow-blue-500/50' },
    amber: { bar: 'bg-amber-500', glow: 'shadow-amber-500/50' },
    red: { bar: 'bg-red-500', glow: 'shadow-red-500/50' },
  }

  const styles = colorStyles[color]

  return (
    <GlassCard padding={size === 'sm' ? 'sm' : 'md'}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm text-slate-400">{label}</span>
        {showPercentage && <span className="text-sm font-semibold text-white">{Math.round(percentage)}%</span>}
      </div>
      <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
        <motion.div
          className={`h-full rounded-full ${styles.bar} shadow-lg ${styles.glow}`}
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 1, ease: 'easeOut' }}
        />
      </div>
    </GlassCard>
  )
}
