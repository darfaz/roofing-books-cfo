import { motion } from 'framer-motion'
import { supabase } from '../lib/supabase'

interface HeaderProps {
  currentPage?: 'dashboard' | 'valuation'
}

export function Header({ currentPage }: HeaderProps) {
  const handleLogout = async () => {
    await supabase.auth.signOut()
  }

  const homeUrl = import.meta.env.PROD ? 'https://crewcfo.com' : '/'
  const dashboardUrl = import.meta.env.PROD ? 'https://app.crewcfo.com' : '/'
  const valuationUrl = import.meta.env.PROD ? 'https://valuation.crewcfo.com' : '/'

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

        {/* Navigation Links */}
        <nav className="flex items-center gap-6">
          <a
            href={dashboardUrl}
            className={`text-sm transition ${
              currentPage === 'dashboard'
                ? 'text-emerald-400 font-medium'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Dashboard
          </a>
          <a
            href={valuationUrl}
            className={`text-sm transition ${
              currentPage === 'valuation'
                ? 'text-emerald-400 font-medium'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Valuation
          </a>
          <button
            onClick={() => void handleLogout()}
            className="text-sm text-slate-400 hover:text-white transition bg-slate-800 hover:bg-slate-700 px-4 py-2 rounded-lg"
          >
            Logout
          </button>
        </nav>
      </div>
    </motion.header>
  )
}
