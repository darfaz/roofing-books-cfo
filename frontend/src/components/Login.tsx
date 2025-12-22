import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { supabase } from '../lib/supabase'

type AuthStep = 'login' | 'mfa_verify' | 'mfa_enroll'

export function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [mfaCode, setMfaCode] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [authStep, setAuthStep] = useState<AuthStep>('login')
  const [factorId, setFactorId] = useState<string | null>(null)
  const [qrCode, setQrCode] = useState<string | null>(null)
  const [mfaSecret, setMfaSecret] = useState<string | null>(null)

  const homeUrl = import.meta.env.PROD ? 'https://crewcfo.com' : '/'

  const signIn = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const { data, error } = await supabase.auth.signInWithPassword({ email, password })
      if (error) throw error

      // Check if MFA is required
      if (data?.user && !data.session) {
        // MFA challenge required - get the factor
        const { data: factorsData } = await supabase.auth.mfa.listFactors()
        if (factorsData?.totp && factorsData.totp.length > 0) {
          const totpFactor = factorsData.totp[0]
          setFactorId(totpFactor.id)

          // Create MFA challenge
          const { data: challengeData, error: challengeError } = await supabase.auth.mfa.challenge({
            factorId: totpFactor.id
          })
          if (challengeError) throw challengeError
          if (challengeData) {
            setFactorId(challengeData.id)
          }
          setAuthStep('mfa_verify')
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to sign in')
    } finally {
      setLoading(false)
    }
  }

  const verifyMfa = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!factorId) return

    setLoading(true)
    setError(null)
    try {
      const { error } = await supabase.auth.mfa.verify({
        factorId,
        challengeId: factorId,
        code: mfaCode
      })
      if (error) throw error
      // Success - session will be established
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Invalid verification code')
    } finally {
      setLoading(false)
    }
  }

  const completeMfaEnrollment = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!factorId) return

    setLoading(true)
    setError(null)
    try {
      // First create a challenge
      const { data: challengeData, error: challengeError } = await supabase.auth.mfa.challenge({
        factorId
      })
      if (challengeError) throw challengeError

      // Then verify with the code
      const { error: verifyError } = await supabase.auth.mfa.verify({
        factorId,
        challengeId: challengeData.id,
        code: mfaCode
      })
      if (verifyError) throw verifyError

      // MFA is now enabled and verified
      setAuthStep('login')
      setQrCode(null)
      setMfaSecret(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to verify MFA code')
    } finally {
      setLoading(false)
    }
  }

  const renderLoginForm = () => (
    <>
      <div className="text-center mb-8">
        <div className="text-5xl mb-4">📊</div>
        <h1 className="text-2xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
          CrewCFO Dashboard
        </h1>
        <p className="text-slate-400 mt-2">Sign in to view your business metrics & valuation</p>
      </div>

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
    </>
  )

  const renderMfaVerify = () => (
    <>
      <div className="text-center mb-8">
        <div className="text-5xl mb-4">🔐</div>
        <h1 className="text-2xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
          Two-Factor Authentication
        </h1>
        <p className="text-slate-400 mt-2">Enter the code from your authenticator app</p>
      </div>

      <form onSubmit={verifyMfa} className="space-y-5">
        <div>
          <label className="block text-sm text-slate-300 mb-2 font-medium">Verification Code</label>
          <input
            className="w-full bg-slate-950/50 border border-slate-700 rounded-xl px-4 py-3 text-white text-center text-2xl tracking-widest placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 transition"
            type="text"
            inputMode="numeric"
            pattern="[0-9]*"
            maxLength={6}
            value={mfaCode}
            onChange={(e) => setMfaCode(e.target.value.replace(/\D/g, ''))}
            placeholder="000000"
            required
            autoFocus
          />
        </div>

        <motion.button
          type="submit"
          disabled={loading || mfaCode.length !== 6}
          className="w-full bg-gradient-to-r from-emerald-500 to-emerald-400 hover:from-emerald-400 hover:to-emerald-300 disabled:opacity-50 disabled:cursor-not-allowed text-black font-semibold py-3 rounded-xl transition shadow-lg shadow-emerald-500/20"
          whileHover={{ scale: loading ? 1 : 1.02 }}
          whileTap={{ scale: loading ? 1 : 0.98 }}
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <div className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin" />
              Verifying...
            </span>
          ) : (
            'Verify'
          )}
        </motion.button>
      </form>

      <div className="mt-6 pt-6 border-t border-slate-800 text-center">
        <button
          onClick={() => {
            setAuthStep('login')
            setMfaCode('')
            setFactorId(null)
          }}
          className="text-sm text-slate-400 hover:text-white transition"
        >
          ← Back to login
        </button>
      </div>
    </>
  )

  const renderMfaEnroll = () => (
    <>
      <div className="text-center mb-6">
        <div className="text-5xl mb-4">🔐</div>
        <h1 className="text-2xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
          Set Up Two-Factor Auth
        </h1>
        <p className="text-slate-400 mt-2">Scan the QR code with your authenticator app</p>
      </div>

      {qrCode && (
        <div className="flex justify-center mb-4">
          <div className="bg-white p-3 rounded-xl">
            <img src={qrCode} alt="MFA QR Code" className="w-48 h-48" />
          </div>
        </div>
      )}

      {mfaSecret && (
        <div className="mb-4 p-3 bg-slate-800/50 rounded-lg">
          <p className="text-xs text-slate-400 text-center mb-1">Or enter this code manually:</p>
          <p className="text-sm text-emerald-400 font-mono text-center break-all">{mfaSecret}</p>
        </div>
      )}

      <form onSubmit={completeMfaEnrollment} className="space-y-5">
        <div>
          <label className="block text-sm text-slate-300 mb-2 font-medium">Enter Code to Verify</label>
          <input
            className="w-full bg-slate-950/50 border border-slate-700 rounded-xl px-4 py-3 text-white text-center text-2xl tracking-widest placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 transition"
            type="text"
            inputMode="numeric"
            pattern="[0-9]*"
            maxLength={6}
            value={mfaCode}
            onChange={(e) => setMfaCode(e.target.value.replace(/\D/g, ''))}
            placeholder="000000"
            required
          />
        </div>

        <motion.button
          type="submit"
          disabled={loading || mfaCode.length !== 6}
          className="w-full bg-gradient-to-r from-emerald-500 to-emerald-400 hover:from-emerald-400 hover:to-emerald-300 disabled:opacity-50 disabled:cursor-not-allowed text-black font-semibold py-3 rounded-xl transition shadow-lg shadow-emerald-500/20"
          whileHover={{ scale: loading ? 1 : 1.02 }}
          whileTap={{ scale: loading ? 1 : 0.98 }}
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <div className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin" />
              Enabling...
            </span>
          ) : (
            'Enable Two-Factor Auth'
          )}
        </motion.button>
      </form>

      <div className="mt-6 pt-6 border-t border-slate-800 text-center">
        <button
          onClick={() => {
            setAuthStep('login')
            setMfaCode('')
            setQrCode(null)
            setMfaSecret(null)
            setFactorId(null)
          }}
          className="text-sm text-slate-400 hover:text-white transition"
        >
          ← Cancel and go back
        </button>
      </div>
    </>
  )

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

      {/* Main Content */}
      <div className="relative flex items-center justify-center min-h-screen p-6 pt-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-md"
        >
          <div className="bg-slate-900/80 backdrop-blur-sm border border-slate-800 rounded-2xl p-8 shadow-2xl">
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

            {authStep === 'login' && renderLoginForm()}
            {authStep === 'mfa_verify' && renderMfaVerify()}
            {authStep === 'mfa_enroll' && renderMfaEnroll()}
          </div>

          {/* Demo credentials hint - only show on login */}
          {authStep === 'login' && (
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
          )}
        </motion.div>
      </div>
    </div>
  )
}
