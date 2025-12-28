import { useState } from 'react'
import { motion } from 'framer-motion'
import { GlassCard } from './ui/GlassCard'

interface DemoGateProps {
  onAccessGranted: (email: string) => void
}

export function DemoGate({ onAccessGranted }: DemoGateProps) {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!email.trim()) {
      setError('Please enter your email')
      return
    }

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) {
      setError('Please enter a valid email address')
      return
    }

    setLoading(true)
    setError(null)

    try {
      // Store lead in backend
      const response = await fetch('/api/demo/capture-lead', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim() }),
      })

      if (!response.ok) {
        const result = await response.json()
        throw new Error(result.detail || 'Failed to register')
      }

      // Store in localStorage to remember this user
      localStorage.setItem('crewcfo_demo_email', email.trim())

      onAccessGranted(email.trim())
    } catch (err) {
      // Even if lead capture fails, allow demo access
      console.error('Lead capture error:', err)
      localStorage.setItem('crewcfo_demo_email', email.trim())
      onAccessGranted(email.trim())
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 flex items-center justify-center p-6">
      {/* Background decoration */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-1/2 -right-1/2 w-full h-full bg-emerald-500/5 rounded-full blur-3xl" />
        <div className="absolute -bottom-1/2 -left-1/2 w-full h-full bg-blue-500/5 rounded-full blur-3xl" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md relative"
      >
        <GlassCard padding="lg">
          {/* Logo */}
          <div className="text-center mb-8">
            <div className="text-5xl mb-4">🏠</div>
            <h1 className="text-2xl font-bold text-white mb-2">CrewCFO Demo</h1>
            <p className="text-slate-400">
              See how CrewCFO helps roofing contractors maximize business value
            </p>
          </div>

          {/* Demo Preview */}
          <div className="bg-slate-800/50 rounded-xl p-4 mb-6">
            <div className="text-sm text-slate-400 mb-3">What you'll see:</div>
            <div className="space-y-2">
              {[
                { icon: '📊', text: 'Owner Dashboard with cash flow' },
                { icon: '💵', text: 'Financial forecasts & projections' },
                { icon: '🔍', text: 'Profit leak analysis' },
                { icon: '⚡', text: 'Valuation shock report' },
                { icon: '🎮', text: 'What-if scenario simulator' },
                { icon: '🗺️', text: 'Value-building roadmap' },
              ].map((item, i) => (
                <div key={i} className="flex items-center gap-2 text-sm">
                  <span>{item.icon}</span>
                  <span className="text-slate-300">{item.text}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Demo Company Info */}
          <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4 mb-6">
            <div className="flex items-center gap-3">
              <span className="text-2xl">🎭</span>
              <div>
                <div className="font-semibold text-amber-400">Apex Roofing Solutions</div>
                <div className="text-sm text-slate-400">$3.5M revenue roofing contractor</div>
              </div>
            </div>
          </div>

          {/* Email Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm text-slate-400 mb-2">
                Enter your email to access the demo
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@company.com"
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition"
                autoFocus
              />
              {error && (
                <p className="text-red-400 text-sm mt-2">{error}</p>
              )}
            </div>

            <motion.button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-emerald-500 to-emerald-400 hover:from-emerald-400 hover:to-emerald-300 disabled:opacity-50 text-black font-bold py-3 rounded-xl transition flex items-center justify-center gap-2"
              whileHover={{ scale: loading ? 1 : 1.02 }}
              whileTap={{ scale: loading ? 1 : 0.98 }}
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                  Loading Demo...
                </>
              ) : (
                <>
                  <span>Access Demo</span>
                  <span>→</span>
                </>
              )}
            </motion.button>
          </form>

          <p className="text-xs text-slate-500 text-center mt-4">
            We'll send you tips on maximizing your business value. Unsubscribe anytime.
          </p>

          {/* Back to home link */}
          <div className="text-center mt-6 pt-6 border-t border-slate-800">
            <a
              href="https://crewcfo.com"
              className="text-sm text-slate-400 hover:text-white transition"
            >
              ← Back to CrewCFO.com
            </a>
          </div>
        </GlassCard>
      </motion.div>
    </div>
  )
}
