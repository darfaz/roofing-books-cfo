import { useEffect, useState } from 'react'
import { supabase } from './lib/supabase'
import { Login } from './components/Login'
import { ValuationDashboard } from './components/ValuationDashboard'

function App() {
  const [accessToken, setAccessToken] = useState<string | null>(null)

  useEffect(() => {
    // Initial session
    supabase.auth.getSession().then(({ data }) => {
      setAccessToken(data.session?.access_token ?? null)
    })

    // Listen for auth changes
    const { data: sub } = supabase.auth.onAuthStateChange((_event, session) => {
      setAccessToken(session?.access_token ?? null)
    })

    return () => {
      sub.subscription.unsubscribe()
    }
  }, [])

  if (!accessToken) return <Login />

  return <ValuationDashboard accessToken={accessToken} />
}

export default App
