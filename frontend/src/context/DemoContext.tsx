import { createContext, useContext, useState, useCallback, type ReactNode } from 'react'

interface DemoContextType {
  isDemoMode: boolean
  setDemoMode: (enabled: boolean) => void
  demoEmail: string | null
  setDemoEmail: (email: string | null) => void
  demoCompanyName: string
}

const DemoContext = createContext<DemoContextType | undefined>(undefined)

export function DemoProvider({ children }: { children: ReactNode }) {
  const [isDemoMode, setIsDemoMode] = useState(() => {
    // Check localStorage for persisted demo mode
    if (typeof window !== 'undefined') {
      return localStorage.getItem('crewcfo_demo_mode') === 'true'
    }
    return false
  })

  const [demoEmail, setDemoEmailState] = useState<string | null>(() => {
    // Check localStorage for persisted demo email
    if (typeof window !== 'undefined') {
      return localStorage.getItem('crewcfo_demo_email')
    }
    return null
  })

  const setDemoMode = useCallback((enabled: boolean) => {
    setIsDemoMode(enabled)
    localStorage.setItem('crewcfo_demo_mode', String(enabled))
    if (!enabled) {
      // Clear demo email when exiting demo
      localStorage.removeItem('crewcfo_demo_email')
      setDemoEmailState(null)
    }
  }, [])

  const setDemoEmail = useCallback((email: string | null) => {
    setDemoEmailState(email)
    if (email) {
      localStorage.setItem('crewcfo_demo_email', email)
    } else {
      localStorage.removeItem('crewcfo_demo_email')
    }
  }, [])

  return (
    <DemoContext.Provider
      value={{
        isDemoMode,
        setDemoMode,
        demoEmail,
        setDemoEmail,
        demoCompanyName: 'Apex Roofing Solutions',
      }}
    >
      {children}
    </DemoContext.Provider>
  )
}

export function useDemoMode() {
  const context = useContext(DemoContext)
  if (context === undefined) {
    throw new Error('useDemoMode must be used within a DemoProvider')
  }
  return context
}
