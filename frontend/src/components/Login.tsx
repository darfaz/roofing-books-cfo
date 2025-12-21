import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { supabase } from '../lib/supabase'

export function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const homeUrl = import.meta.env.PROD ? 'https://crewcfo.com' : '/'

  const signIn = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const { error } = await supabase.auth.signInWithPassword({ email, password })
      if (error) throw error
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to sign in')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white">
      {/* Background decoration */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-1/2 -right-1/2 w-full h-full bg-emerald-500/5 rounded-full blur-3xl" />
        <div className="absolute -bottom-1/2 -left-1/2 w-full h-full bg-blue-500/5 rounded-full blur-3xl" />
      </div>

      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-slate-950/90 backdrop-blur-sm z-50 border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-6 py-3 flex justify-between items-center">
          <a href={homeUrl} className="flex items-center gap-2 hover:opacity-80 transition">
            <span className="text-2xl">🏠</span>
            <span className="text-xl font-bold text-white">CrewCFO</span>
          </a>
          <div className="flex items-center gap-4">
            <a href={homeUrl} className="text-sm text-slate-400 hover:text-white transition">
              Home
            </a>
            <span className="text-sm text-emerald-400 font-medium">
              Valuation
            </span>
          </div>
        </div>
      </nav>

      {/* Login Form */}
      <div className="relative flex items-center justify-center min-h-screen p-6 pt-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-md"
        >
          <div className="bg-slate-900/80 backdrop-blur-sm border border-slate-800 rounded-2xl p-8 shadow-2xl">
            {/* Header */}
            <div className="text-center mb-8">
              <div className="text-5xl mb-4">📊</div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
                Valuation Dashboard
              </h1>
              <p className="text-slate-400 mt-2">Sign in to view your business valuation</p>
            </div>

            {error && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="mb-6 bg-red-500/10 border border-red-500/30 text-red-300 rounded-lg p-4 text-sm flex items-center gap-3"
              >
                <span className="text-lg">⚠️</span>
                {error}
              </motion.div>
            )}

            <form onSubmit={signIn} className="space-y-5">
              <div>
                <label className="block text-sm text-slate-300 mb-2 font-medium">Email</label>
                <input
                  className="w-full bg-slate-950/50 border border-slate-700 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 transition"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@company.com"
                  required
                />
              </div>

              <div>
                <label className="block text-sm text-slate-300 mb-2 font-medium">Password</label>
                <input
                  className="w-full bg-slate-950/50 border border-slate-700 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 transition"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                />
              </div>

              <motion.button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-emerald-500 to-emerald-400 hover:from-emerald-400 hover:to-emerald-300 disabled:opacity-50 disabled:cursor-not-allowed text-black font-semibold py-3 rounded-xl transition shadow-lg shadow-emerald-500/20"
                whileHover={{ scale: loading ? 1 : 1.02 }}
                whileTap={{ scale: loading ? 1 : 0.98 }}
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <div className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                    Signing in...
                  </span>
                ) : (
                  'Sign In'
                )}
              </motion.button>
            </form>

            {/* Links */}
            <div className="mt-6 pt-6 border-t border-slate-800 text-center space-y-3">
              <p className="text-sm text-slate-500">
                Don't have an account?{' '}
                <a href={homeUrl} className="text-emerald-400 hover:text-emerald-300 transition">
                  Get started
                </a>
              </p>
              <a
                href={homeUrl}
                className="inline-block text-sm text-slate-400 hover:text-white transition"
              >
                ← Back to CrewCFO.com
              </a>
            </div>
          </div>

          {/* Demo credentials hint */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="mt-6 text-center"
          >
            <p className="text-xs text-slate-600">
              Demo: demo@crewcfo.com / demo1234
            </p>
          </motion.div>
        </motion.div>
      </div>
    </div>
  )
}






