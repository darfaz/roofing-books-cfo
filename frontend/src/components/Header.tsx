import { motion } from 'framer-motion'
import { supabase } from '../lib/supabase'

interface HeaderProps {
  userEmail?: string
}

export function Header({ userEmail }: HeaderProps) {
  const handleLogout = async () => {
    await supabase.auth.signOut()
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

        {/* Right side - user info and logout */}
        <div className="flex items-center gap-4">
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
