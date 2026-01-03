/**
 * Friday Payday - Main Dashboard Container
 *
 * Container component with sub-navigation for:
 * - Collections (AR aging, invoices)
 * - Templates (email/SMS templates)
 * - Sequences (dunning configuration)
 */
import { useState } from 'react'
import { motion } from 'framer-motion'
import { CollectionsDashboard } from './CollectionsDashboard'
import { TemplateManager } from './TemplateManager'
import { SequenceManager } from './SequenceManager'

interface FridayPaydayDashboardProps {
  accessToken: string
}

type TabId = 'collections' | 'templates' | 'sequences'

const TABS: { id: TabId; label: string; icon: string }[] = [
  { id: 'collections', label: 'Collections', icon: '💰' },
  { id: 'templates', label: 'Templates', icon: '📝' },
  { id: 'sequences', label: 'Sequences', icon: '⚡' },
]

export function FridayPaydayDashboard({ accessToken }: FridayPaydayDashboardProps) {
  const [activeTab, setActiveTab] = useState<TabId>('collections')

  return (
    <div className="space-y-6">
      {/* Sub Navigation */}
      <div className="flex items-center gap-1 p-1 bg-slate-800/50 rounded-lg w-fit">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`relative px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? 'text-white'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            {activeTab === tab.id && (
              <motion.div
                layoutId="fridayPaydayTab"
                className="absolute inset-0 bg-emerald-600 rounded-md"
                transition={{ type: 'spring', bounce: 0.2, duration: 0.4 }}
              />
            )}
            <span className="relative flex items-center gap-2">
              <span>{tab.icon}</span>
              {tab.label}
            </span>
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === 'collections' && (
          <CollectionsDashboard accessToken={accessToken} />
        )}
        {activeTab === 'templates' && (
          <TemplateManager accessToken={accessToken} />
        )}
        {activeTab === 'sequences' && (
          <SequenceManager accessToken={accessToken} />
        )}
      </div>
    </div>
  )
}
