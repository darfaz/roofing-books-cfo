import { motion } from 'framer-motion'

interface DriverScoreCardProps {
  icon: string
  label: string
  description: string
  score: number // 0-100
  maxScore?: number
  delay?: number
}

export function DriverScoreCard({
  icon,
  label,
  description,
  score,
  maxScore = 100,
  delay = 0,
}: DriverScoreCardProps) {
  const percentage = Math.min(100, (score / maxScore) * 100)

  const getScoreColor = (pct: number) => {
    if (pct >= 80) return { text: 'text-emerald-400', bg: 'bg-emerald-500', glow: 'shadow-emerald-500/30' }
    if (pct >= 60) return { text: 'text-blue-400', bg: 'bg-blue-500', glow: 'shadow-blue-500/30' }
    if (pct >= 40) return { text: 'text-amber-400', bg: 'bg-amber-500', glow: 'shadow-amber-500/30' }
    return { text: 'text-red-400', bg: 'bg-red-500', glow: 'shadow-red-500/30' }
  }

  const colors = getScoreColor(percentage)

  return (
    <motion.div
      className="bg-slate-900/80 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm hover:border-slate-600/50 transition-colors group"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
      whileHover={{ scale: 1.02 }}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-start gap-3">
          <motion.div
            className="text-3xl"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 200, delay: delay + 0.2 }}
          >
            {icon}
          </motion.div>
          <div>
            <h3 className="font-semibold text-white group-hover:text-emerald-300 transition-colors">{label}</h3>
            <p className="text-sm text-slate-400 mt-0.5">{description}</p>
          </div>
        </div>
        <motion.div
          className={`text-3xl font-bold ${colors.text}`}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: delay + 0.3 }}
        >
          {score}
        </motion.div>
      </div>

      {/* Progress bar */}
      <div className="relative">
        <div className="h-3 bg-slate-800 rounded-full overflow-hidden">
          <motion.div
            className={`h-full rounded-full ${colors.bg} shadow-lg ${colors.glow}`}
            initial={{ width: 0 }}
            animate={{ width: `${percentage}%` }}
            transition={{ duration: 0.8, delay: delay + 0.4, ease: 'easeOut' }}
          />
        </div>

        {/* Tick marks */}
        <div className="absolute top-0 left-0 right-0 h-3 flex justify-between px-0.5 pointer-events-none">
          {[20, 40, 60, 80].map((tick) => (
            <div
              key={tick}
              className="w-px h-full bg-slate-700/50"
              style={{ marginLeft: `${tick}%`, position: 'absolute', left: 0 }}
            />
          ))}
        </div>
      </div>

      {/* Labels */}
      <div className="flex justify-between mt-2 text-xs text-slate-500">
        <span>Low</span>
        <span>High</span>
      </div>
    </motion.div>
  )
}
