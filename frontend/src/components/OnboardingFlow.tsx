import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { supabase } from '../lib/supabase'
import { GlassCard } from './ui/GlassCard'
import { ShockReport } from './ShockReport'

interface OnboardingFlowProps {
  accessToken: string
  onComplete: () => void
}

type Step = 'welcome' | 'connect-qbo' | 'generating' | 'report' | 'complete'

export function OnboardingFlow({ accessToken, onComplete }: OnboardingFlowProps) {
  const [currentStep, setCurrentStep] = useState<Step>('welcome')
  const [tenantId, setTenantId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Check if QBO is already connected
  const checkQboConnection = useCallback(async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser()
      const tid = user?.user_metadata?.tenant_id
      setTenantId(tid)

      if (!tid) return

      const { data } = await supabase
        .from('tenant_integrations')
        .select('is_active')
        .eq('tenant_id', tid)
        .eq('provider', 'quickbooks')
        .single()

      if (data?.is_active) {
        // If already connected and on welcome, skip to report
        if (currentStep === 'welcome') {
          setCurrentStep('report')
        }
      }
    } catch {
      // Not connected, that's fine
    }
  }, [currentStep])

  useEffect(() => {
    void checkQboConnection()
  }, [checkQboConnection])

  // Handle QBO OAuth redirect
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    if (params.get('qbo') === 'connected') {
      setCurrentStep('generating')
      // Clean up URL
      window.history.replaceState({}, '', window.location.pathname)
      // Auto-generate report after connection
      generateShockReport()
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const startQboConnect = () => {
    if (!tenantId) {
      setError('No tenant found. Please log in again.')
      return
    }
    // Redirect to QBO OAuth with return URL
    const returnUrl = `${window.location.origin}${window.location.pathname}?qbo=connected`
    window.location.href = `/auth/qbo/connect?tenant_id=${tenantId}&return_url=${encodeURIComponent(returnUrl)}`
  }

  const generateShockReport = async () => {
    setCurrentStep('generating')

    try {
      const response = await fetch('/api/valuation/shock-report', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
      })

      if (!response.ok) {
        const result = await response.json()
        throw new Error(result.error?.message || 'Failed to generate report')
      }

      // Report generated, show it
      setCurrentStep('report')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate shock report')
      // Still show report section - it will handle the error
      setCurrentStep('report')
    }
  }

  const handleStartTrial = () => {
    setCurrentStep('complete')
    // TODO: Redirect to payment/trial signup
  }

  const stepVariants = {
    initial: { opacity: 0, x: 50 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -50 },
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white">
      {/* Background decoration */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-1/2 -right-1/2 w-full h-full bg-emerald-500/5 rounded-full blur-3xl" />
        <div className="absolute -bottom-1/2 -left-1/2 w-full h-full bg-red-500/5 rounded-full blur-3xl" />
      </div>

      {/* Progress indicator */}
      <div className="fixed top-0 left-0 right-0 z-50 bg-slate-950/80 backdrop-blur-sm border-b border-slate-800">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="text-xl font-bold bg-gradient-to-r from-emerald-400 to-emerald-200 bg-clip-text text-transparent">
              CrewCFO
            </div>
            <div className="flex items-center gap-2">
              {['welcome', 'connect-qbo', 'report'].map((step, idx) => {
                const stepOrder = ['welcome', 'connect-qbo', 'generating', 'report', 'complete']
                const currentIdx = stepOrder.indexOf(currentStep)
                const stepIdx = stepOrder.indexOf(step)
                const isActive = currentIdx >= stepIdx
                const isCurrent = step === currentStep || (step === 'report' && currentStep === 'generating')

                return (
                  <div key={step} className="flex items-center">
                    <motion.div
                      className={`w-3 h-3 rounded-full ${
                        isActive ? 'bg-emerald-500' : 'bg-slate-700'
                      } ${isCurrent ? 'ring-2 ring-emerald-400 ring-offset-2 ring-offset-slate-950' : ''}`}
                      animate={{ scale: isCurrent ? 1.2 : 1 }}
                    />
                    {idx < 2 && (
                      <div className={`w-12 h-0.5 ${isActive ? 'bg-emerald-500' : 'bg-slate-700'}`} />
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </div>

      <div className="relative pt-24 pb-12 px-6">
        <div className="max-w-4xl mx-auto">
          <AnimatePresence mode="wait">
            {/* Step 1: Welcome */}
            {currentStep === 'welcome' && (
              <motion.div
                key="welcome"
                variants={stepVariants}
                initial="initial"
                animate="animate"
                exit="exit"
                className="text-center"
              >
                <motion.div
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ delay: 0.2 }}
                >
                  <div className="text-6xl mb-6">💰</div>
                  <h1 className="text-4xl md:text-5xl font-black mb-4">
                    <span className="bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
                      Are You Leaving
                    </span>
                    <br />
                    <span className="bg-gradient-to-r from-red-400 to-amber-400 bg-clip-text text-transparent">
                      $100K+ On The Table?
                    </span>
                  </h1>
                  <p className="text-xl text-slate-400 max-w-2xl mx-auto mb-8">
                    Most roofing contractors think they know their business value.
                    But buyers see something very different.
                  </p>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="mb-12"
                >
                  <GlassCard className="max-w-xl mx-auto" padding="lg">
                    <div className="grid grid-cols-2 gap-8 text-center">
                      <div>
                        <div className="text-4xl font-bold text-white mb-2">$2.5M</div>
                        <div className="text-sm text-slate-400">What You Think</div>
                      </div>
                      <div>
                        <div className="text-4xl font-bold text-red-400 mb-2">$1.6M</div>
                        <div className="text-sm text-slate-400">What Buyers Pay</div>
                      </div>
                    </div>
                    <div className="mt-6 pt-6 border-t border-slate-700 text-center">
                      <div className="text-sm text-slate-500 mb-1">Average Gap</div>
                      <div className="text-3xl font-black text-red-400">-36%</div>
                    </div>
                  </GlassCard>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.6 }}
                >
                  <motion.button
                    onClick={() => setCurrentStep('connect-qbo')}
                    className="bg-gradient-to-r from-emerald-500 to-emerald-400 hover:from-emerald-400 hover:to-emerald-300 text-black font-bold px-10 py-4 rounded-xl text-lg transition"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    Find My Value Gap
                  </motion.button>
                  <p className="text-xs text-slate-500 mt-4">Takes less than 5 minutes</p>
                </motion.div>
              </motion.div>
            )}

            {/* Step 2: Connect QuickBooks */}
            {currentStep === 'connect-qbo' && (
              <motion.div
                key="connect"
                variants={stepVariants}
                initial="initial"
                animate="animate"
                exit="exit"
                className="text-center"
              >
                <div className="text-5xl mb-6">📊</div>
                <h2 className="text-3xl font-bold mb-4">Connect Your QuickBooks</h2>
                <p className="text-slate-400 max-w-lg mx-auto mb-8">
                  We'll analyze your real financial data to show you exactly
                  what buyers will see - and what they'll pay.
                </p>

                <GlassCard className="max-w-lg mx-auto" padding="lg">
                  <div className="space-y-4 text-left mb-6">
                    <div className="flex items-start gap-3">
                      <span className="text-emerald-400 mt-0.5">✓</span>
                      <div>
                        <div className="font-medium">Read-only access</div>
                        <div className="text-sm text-slate-400">We never modify your books</div>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <span className="text-emerald-400 mt-0.5">✓</span>
                      <div>
                        <div className="font-medium">Bank-level security</div>
                        <div className="text-sm text-slate-400">256-bit encryption, SOC 2 compliant</div>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <span className="text-emerald-400 mt-0.5">✓</span>
                      <div>
                        <div className="font-medium">Instant analysis</div>
                        <div className="text-sm text-slate-400">Your shock report in under 60 seconds</div>
                      </div>
                    </div>
                  </div>

                  {error && (
                    <div className="bg-red-500/20 border border-red-500/30 text-red-400 text-sm p-3 rounded-lg mb-4">
                      {error}
                    </div>
                  )}

                  <motion.button
                    onClick={startQboConnect}
                    className="w-full bg-[#2CA01C] hover:bg-[#3AB52A] text-white font-bold py-4 rounded-xl text-lg transition flex items-center justify-center gap-3"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                    </svg>
                    Connect QuickBooks Online
                  </motion.button>
                </GlassCard>

                <button
                  onClick={() => setCurrentStep('welcome')}
                  className="text-sm text-slate-500 hover:text-slate-300 mt-6 transition"
                >
                  ← Back
                </button>
              </motion.div>
            )}

            {/* Step 3: Generating Report */}
            {currentStep === 'generating' && (
              <motion.div
                key="generating"
                variants={stepVariants}
                initial="initial"
                animate="animate"
                exit="exit"
                className="text-center"
              >
                <motion.div
                  className="w-24 h-24 mx-auto mb-8 relative"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                >
                  <div className="absolute inset-0 border-4 border-emerald-500/20 rounded-full" />
                  <div className="absolute inset-0 border-4 border-transparent border-t-emerald-500 rounded-full" />
                </motion.div>

                <h2 className="text-3xl font-bold mb-4">Analyzing Your Books...</h2>

                <div className="max-w-md mx-auto space-y-3 text-left">
                  {[
                    'Syncing QuickBooks data',
                    'Calculating TTM financials',
                    'Analyzing add-backs and adjustments',
                    'Scoring value drivers',
                    'Determining buyer multiple',
                    'Generating shock report',
                  ].map((step, idx) => (
                    <motion.div
                      key={step}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.3 }}
                      className="flex items-center gap-3 text-slate-400"
                    >
                      <motion.div
                        className="w-5 h-5 rounded-full bg-emerald-500/20 flex items-center justify-center"
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ delay: idx * 0.3 + 0.2 }}
                      >
                        <motion.span
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ delay: idx * 0.3 + 0.4 }}
                          className="text-emerald-400 text-xs"
                        >
                          ✓
                        </motion.span>
                      </motion.div>
                      <span>{step}</span>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Step 4: Show Report */}
            {currentStep === 'report' && (
              <motion.div
                key="report"
                variants={stepVariants}
                initial="initial"
                animate="animate"
                exit="exit"
              >
                <ShockReport accessToken={accessToken} onStartTrial={handleStartTrial} />
              </motion.div>
            )}

            {/* Step 5: Complete / Trial Started */}
            {currentStep === 'complete' && (
              <motion.div
                key="complete"
                variants={stepVariants}
                initial="initial"
                animate="animate"
                exit="exit"
                className="text-center"
              >
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: 'spring', bounce: 0.5 }}
                  className="text-7xl mb-6"
                >
                  🎉
                </motion.div>

                <h2 className="text-4xl font-bold mb-4">
                  <span className="bg-gradient-to-r from-emerald-400 to-emerald-200 bg-clip-text text-transparent">
                    Trial Activated!
                  </span>
                </h2>
                <p className="text-xl text-slate-400 max-w-lg mx-auto mb-8">
                  You now have full access to your value recovery roadmap.
                  Let's start closing that gap.
                </p>

                <motion.button
                  onClick={onComplete}
                  className="bg-gradient-to-r from-emerald-500 to-emerald-400 hover:from-emerald-400 hover:to-emerald-300 text-black font-bold px-10 py-4 rounded-xl text-lg transition"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  Go to Dashboard
                </motion.button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}
