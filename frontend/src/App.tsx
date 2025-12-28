import { useEffect, useState } from 'react'
import { supabase } from './lib/supabase'
import { Login } from './components/Login'
import { ValuationDashboard } from './components/ValuationDashboard'
import { Header } from './components/Header'
import { DemoGate } from './components/DemoGate'
import { DemoProvider, useDemoMode } from './context/DemoContext'

function AppContent() {
  const [accessToken, setAccessToken] = useState<string | null>(null)
  const [userEmail, setUserEmail] = useState<string | undefined>(undefined)
  const [loading, setLoading] = useState(true)
  const { isDemoMode, setDemoMode, demoEmail, setDemoEmail } = useDemoMode()

  // Check if we're on the /demo route
  const isDemoRoute = window.location.pathname === '/demo'

  useEffect(() => {
    // Initial session
    supabase.auth.getSession().then(({ data }) => {
      setAccessToken(data.session?.access_token ?? null)
      setUserEmail(data.session?.user?.email)
      setLoading(false)
    })

    // Listen for auth changes
    const { data: sub } = supabase.auth.onAuthStateChange((_event, session) => {
      setAccessToken(session?.access_token ?? null)
      setUserEmail(session?.user?.email)
      setLoading(false)
    })

    return () => {
      sub.subscription.unsubscribe()
    }
  }, [])

  const handleDemoAccess = (email: string) => {
    setDemoEmail(email)
    setDemoMode(true)
  }

  const handleExitDemo = () => {
    setDemoMode(false)
    // Redirect to home page
    window.location.href = 'https://crewcfo.com'
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 flex items-center justify-center">
        <div className="flex items-center gap-3 text-slate-400">
          <div className="w-6 h-6 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
          Loading...
        </div>
      </div>
    )
  }

  // Demo route: show demo gate or demo dashboard
  if (isDemoRoute) {
    // If already captured email, show demo
    if (isDemoMode && demoEmail) {
      return (
        <>
          <Header
            userEmail={demoEmail}
            onExitDemo={handleExitDemo}
          />
          <div className="pt-16">
            <ValuationDashboard accessToken="demo" />
          </div>
        </>
      )
    }

    // Show demo gate to capture email
    return <DemoGate onAccessGranted={handleDemoAccess} />
  }

  // Regular app: show dashboard if logged in
  if (accessToken) {
    return (
      <>
        <Header userEmail={userEmail} />
        <div className="pt-16">
          <ValuationDashboard accessToken={accessToken} />
        </div>
      </>
    )
  }

  // Show login if not authenticated
  return <Login />
}

function App() {
  return (
    <DemoProvider>
      <AppContent />
    </DemoProvider>
  )
}

export default App
