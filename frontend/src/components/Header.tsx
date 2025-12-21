import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { supabase } from '../lib/supabase'

interface HeaderProps {
  userEmail?: string
}

export function Header({ userEmail }: HeaderProps) {
  const [qboConnected, setQboConnected] = useState<boolean | null>(null)
  const [tenantId, setTenantId] = useState<string | null>(null)
  const [connecting, setConnecting] = useState(false)

  useEffect(() => {
    const checkQboStatus = async () => {
      try {
        const { data: { user } } = await supabase.auth.getUser()
        const tid = user?.user_metadata?.tenant_id
        setTenantId(tid)

        if (!tid) {
          setQboConnected(false)
          return
        }

        // Check tenant_integrations for QBO connection
        const { data } = await supabase
          .from('tenant_integrations')
          .select('is_active')
          .eq('tenant_id', tid)
          .eq('provider', 'quickbooks')
          .single()

        setQboConnected(data?.is_active === true)
      } catch {
        setQboConnected(false)
      }
    }

    void checkQboStatus()
  }, [])

  const handleLogout = async () => {
    await supabase.auth.signOut()
  }

  const handleConnectQbo = () => {
    if (!tenantId) return
    setConnecting(true)
    const returnUrl = `${window.location.origin}${window.location.pathname}`
    window.location.href = `/auth/qbo/connect?tenant_id=${tenantId}&return_url=${encodeURIComponent(returnUrl)}`
  }

  const homeUrl = import.meta.env.PROD ? 'https://crewcfo.com' : '/'

  return (
    <motion.header
      className="fixed top-0 w-full bg-slate-950/90 backdrop-blur-sm z-50 border-b border-slate-800"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="max-w-7xl mx-auto px-6 py-3 flex justify-between items-center">
        {/* Logo - links to home */}
        <a
          href={homeUrl}
          className="flex items-center gap-2 hover:opacity-80 transition"
        >
          <span className="text-2xl">🏠</span>
          <span className="text-xl font-bold text-white">CrewCFO</span>
        </a>

        {/* Right side - QBO status, user info and logout */}
        <div className="flex items-center gap-3">
          {/* QBO Connection Button */}
          {qboConnected === null ? (
            <span className="text-xs text-slate-500">...</span>
          ) : qboConnected ? (
            <span className="flex items-center gap-1.5 text-xs bg-emerald-500/10 text-emerald-400 px-3 py-1.5 rounded-full border border-emerald-500/30">
              <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              QuickBooks
            </span>
          ) : (
            <button
              onClick={handleConnectQbo}
              disabled={connecting || !tenantId}
              className="flex items-center gap-1.5 text-xs bg-[#2CA01C] hover:bg-[#3AB82A] disabled:opacity-50 text-white font-medium px-3 py-1.5 rounded-lg transition"
            >
              {connecting ? (
                <>
                  <div className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Connecting...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                  </svg>
                  Connect QuickBooks
                </>
              )}
            </button>
          )}

          {userEmail && (
            <span className="text-sm text-slate-400 hidden sm:block">
              {userEmail}
            </span>
          )}
          <a
            href={homeUrl}
            className="text-sm text-slate-400 hover:text-white transition hidden sm:block"
          >
            Home
          </a>
          <button
            onClick={() => void handleLogout()}
            className="text-sm text-slate-400 hover:text-white transition bg-slate-800 hover:bg-slate-700 px-4 py-2 rounded-lg"
          >
            Logout
          </button>
        </div>
      </div>
    </motion.header>
  )
}
