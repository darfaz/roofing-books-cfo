import { useEffect, useState } from 'react'
import { supabase } from './lib/supabase'
import { Login } from './components/Login'
import { ValuationDashboard } from './components/ValuationDashboard'
import { Header } from './components/Header'

function App() {
  const [accessToken, setAccessToken] = useState<string | null>(null)
  const [userEmail, setUserEmail] = useState<string | undefined>(undefined)
  const [loading, setLoading] = useState(true)

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

  if (!accessToken) return <Login />

  return (
    <>
      <Header userEmail={userEmail} />
      <div className="pt-16">
        <ValuationDashboard accessToken={accessToken} />
      </div>
    </>
  )
}

export default App
