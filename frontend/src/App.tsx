import { useEffect, useState, useCallback } from 'react'
import { supabase } from './lib/supabase'
import { Login } from './components/Login'
import { ValuationDashboard } from './components/ValuationDashboard'
import { OnboardingFlow } from './components/OnboardingFlow'

function App() {
  const [accessToken, setAccessToken] = useState<string | null>(null)
  const [showOnboarding, setShowOnboarding] = useState(false)
  const [checkingOnboarding, setCheckingOnboarding] = useState(true)

  // Check if user should see onboarding (no shock report yet)
  const checkOnboardingStatus = useCallback(async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser()
      const tenantId = user?.user_metadata?.tenant_id

      if (!tenantId) {
        setShowOnboarding(true)
        return
      }

      // Check for existing shock report
      const { data } = await supabase
        .from('valuation_shock_reports')
        .select('id')
        .eq('tenant_id', tenantId)
        .limit(1)

      // If no shock report, show onboarding
      setShowOnboarding(!data || data.length === 0)
    } catch {
      // Default to showing onboarding on error
      setShowOnboarding(true)
    } finally {
      setCheckingOnboarding(false)
    }
  }, [])

  useEffect(() => {
    // Initial session
    supabase.auth.getSession().then(({ data }) => {
      setAccessToken(data.session?.access_token ?? null)
      if (data.session?.access_token) {
        void checkOnboardingStatus()
      } else {
        setCheckingOnboarding(false)
      }
    })

    // Listen for auth changes
    const { data: sub } = supabase.auth.onAuthStateChange((_event, session) => {
      setAccessToken(session?.access_token ?? null)
      if (session?.access_token) {
        void checkOnboardingStatus()
      } else {
        setCheckingOnboarding(false)
      }
    })

    return () => {
      sub.subscription.unsubscribe()
    }
  }, [checkOnboardingStatus])

  if (!accessToken) return <Login />

  // Show loading while checking onboarding status
  if (checkingOnboarding) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 flex items-center justify-center">
        <div className="flex items-center gap-3 text-slate-400">
          <div className="w-6 h-6 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
          Loading...
        </div>
      </div>
    )
  }

  // Show onboarding flow for new users
  if (showOnboarding) {
    return (
      <OnboardingFlow
        accessToken={accessToken}
        onComplete={() => setShowOnboarding(false)}
      />
    )
  }

  return <ValuationDashboard accessToken={accessToken} />
}

export default App
