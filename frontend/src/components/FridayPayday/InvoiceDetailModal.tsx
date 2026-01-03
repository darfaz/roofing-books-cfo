/**
 * Friday Payday - Invoice Detail Modal
 *
 * Shows full invoice details with ability to:
 * - Override payer classification
 * - Pause/resume dunning sequence
 * - View reminder history
 * - Record manual actions
 */
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { GlassCard } from '../ui/GlassCard'

interface Invoice {
  id: string
  customer_id: string
  customer_name: string
  invoice_number: string | null
  amount: number
  balance: number
  due_date: string
  invoice_date: string
  days_overdue: number
  status: string
  payer_type: string
  payer_type_override: boolean
  classification_confidence: number
  sequence_status: string
  sequence_paused_reason: string | null
  job_address: string | null
  description: string | null
  fp_customers?: {
    display_name: string
    email: string | null
    phone: string | null
  }
  fp_reminders?: Array<{
    id: string
    step_number: number
    channel: string
    status: string
    sent_at: string
    opened_at: string | null
    clicked_at: string | null
  }>
}

interface InvoiceDetailModalProps {
  invoice: Invoice | null
  isOpen: boolean
  onClose: () => void
  onUpdate: (invoiceId: string, updates: Record<string, unknown>) => Promise<void>
  onPauseSequence: (invoiceId: string, reason?: string) => Promise<void>
  onResumeSequence: (invoiceId: string) => Promise<void>
  isDemoMode?: boolean
}

const PAYER_TYPES = [
  { value: 'homeowner_direct', label: 'Homeowner Direct', description: 'Customer pays directly' },
  { value: 'insurance_pending', label: 'Insurance Pending', description: 'Waiting on insurance payment' },
  { value: 'supplement_pending', label: 'Supplement Pending', description: 'Supplement filed, awaiting approval' },
  { value: 'depreciation_recovery', label: 'Depreciation Recovery', description: 'ACV paid, collecting depreciation' },
  { value: 'gc_commercial', label: 'GC/Commercial', description: 'General contractor or commercial account' },
  { value: 'retainage', label: 'Retainage', description: 'Retainage held pending completion' },
]

const STATUS_COLORS: Record<string, string> = {
  sent: 'blue',
  partial: 'amber',
  overdue: 'red',
  paid: 'emerald',
  disputed: 'rose',
  written_off: 'slate',
}

const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
  }).format(amount)
}

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

const formatDateTime = (dateString: string): string => {
  return new Date(dateString).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

export function InvoiceDetailModal({
  invoice,
  isOpen,
  onClose,
  onUpdate,
  onPauseSequence,
  onResumeSequence,
  isDemoMode = false,
}: InvoiceDetailModalProps) {
  const [selectedPayerType, setSelectedPayerType] = useState(invoice?.payer_type || '')
  const [pauseReason, setPauseReason] = useState('')
  const [showPauseDialog, setShowPauseDialog] = useState(false)
  const [saving, setSaving] = useState(false)

  if (!isOpen || !invoice) return null

  const statusColor = STATUS_COLORS[invoice.status] || 'slate'
  const isPaused = invoice.sequence_status === 'paused'

  const handlePayerTypeChange = async (newType: string) => {
    if (isDemoMode || newType === invoice.payer_type) return

    setSaving(true)
    try {
      await onUpdate(invoice.id, { payer_type: newType })
      setSelectedPayerType(newType)
    } finally {
      setSaving(false)
    }
  }

  const handlePauseSequence = async () => {
    if (isDemoMode) return

    setSaving(true)
    try {
      await onPauseSequence(invoice.id, pauseReason || undefined)
      setShowPauseDialog(false)
      setPauseReason('')
    } finally {
      setSaving(false)
    }
  }

  const handleResumeSequence = async () => {
    if (isDemoMode) return

    setSaving(true)
    try {
      await onResumeSequence(invoice.id)
    } finally {
      setSaving(false)
    }
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          {/* Modal */}
          <motion.div
            className="fixed inset-4 md:inset-auto md:top-1/2 md:left-1/2 md:-translate-x-1/2 md:-translate-y-1/2 md:w-full md:max-w-2xl md:max-h-[85vh] overflow-y-auto z-50"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
          >
            <GlassCard padding="lg" className="relative">
              {/* Close button */}
              <button
                onClick={onClose}
                className="absolute top-4 right-4 text-slate-400 hover:text-white transition"
              >
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>

              {/* Header */}
              <div className="mb-6">
                <div className="flex items-start justify-between">
                  <div>
                    <h2 className="text-2xl font-bold text-white">
                      Invoice {invoice.invoice_number || invoice.id.slice(0, 8)}
                    </h2>
                    <p className="text-slate-400">{invoice.customer_name}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-white">{formatCurrency(invoice.balance)}</div>
                    <div className="text-sm text-slate-400">of {formatCurrency(invoice.amount)}</div>
                  </div>
                </div>

                {/* Status badges */}
                <div className="flex items-center gap-2 mt-4">
                  <span className={`px-3 py-1 rounded-full text-sm bg-${statusColor}-500/20 text-${statusColor}-300`}>
                    {invoice.status.charAt(0).toUpperCase() + invoice.status.slice(1)}
                  </span>
                  {invoice.days_overdue > 0 && (
                    <span className="px-3 py-1 rounded-full text-sm bg-red-500/20 text-red-300">
                      {invoice.days_overdue} days overdue
                    </span>
                  )}
                  {isPaused && (
                    <span className="px-3 py-1 rounded-full text-sm bg-amber-500/20 text-amber-300">
                      Sequence Paused
                    </span>
                  )}
                </div>
              </div>

              {/* Invoice Details */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div>
                  <div className="text-sm text-slate-400">Invoice Date</div>
                  <div className="text-white">{invoice.invoice_date ? formatDate(invoice.invoice_date) : '—'}</div>
                </div>
                <div>
                  <div className="text-sm text-slate-400">Due Date</div>
                  <div className={invoice.days_overdue > 0 ? 'text-red-400' : 'text-white'}>
                    {formatDate(invoice.due_date)}
                  </div>
                </div>
                {invoice.job_address && (
                  <div className="col-span-2">
                    <div className="text-sm text-slate-400">Job Address</div>
                    <div className="text-white">{invoice.job_address}</div>
                  </div>
                )}
                {invoice.description && (
                  <div className="col-span-2">
                    <div className="text-sm text-slate-400">Description</div>
                    <div className="text-white">{invoice.description}</div>
                  </div>
                )}
              </div>

              {/* Customer Contact */}
              {invoice.fp_customers && (
                <div className="mb-6 p-4 bg-slate-800/50 rounded-lg">
                  <h3 className="text-sm font-medium text-slate-400 mb-2">Customer Contact</h3>
                  <div className="space-y-1">
                    <div className="text-white">{invoice.fp_customers.display_name}</div>
                    {invoice.fp_customers.email && (
                      <div className="text-slate-300 text-sm">{invoice.fp_customers.email}</div>
                    )}
                    {invoice.fp_customers.phone && (
                      <div className="text-slate-300 text-sm">{invoice.fp_customers.phone}</div>
                    )}
                  </div>
                </div>
              )}

              {/* Payer Classification */}
              <div className="mb-6">
                <h3 className="text-sm font-medium text-slate-400 mb-2">
                  Payer Classification
                  {invoice.payer_type_override && (
                    <span className="ml-2 text-xs text-amber-400">(manually set)</span>
                  )}
                  {!invoice.payer_type_override && invoice.classification_confidence && (
                    <span className="ml-2 text-xs text-slate-500">
                      ({Math.round(invoice.classification_confidence * 100)}% confidence)
                    </span>
                  )}
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {PAYER_TYPES.map((type) => (
                    <button
                      key={type.value}
                      onClick={() => handlePayerTypeChange(type.value)}
                      disabled={isDemoMode || saving}
                      className={`p-3 rounded-lg border text-left transition ${
                        (selectedPayerType || invoice.payer_type) === type.value
                          ? 'border-emerald-500 bg-emerald-500/10'
                          : 'border-slate-700 hover:border-slate-600 bg-slate-800/50'
                      } ${isDemoMode ? 'cursor-not-allowed opacity-60' : ''}`}
                    >
                      <div className="text-sm font-medium text-white">{type.label}</div>
                      <div className="text-xs text-slate-400 mt-0.5">{type.description}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Sequence Control */}
              <div className="mb-6">
                <h3 className="text-sm font-medium text-slate-400 mb-2">Collection Sequence</h3>
                {isPaused ? (
                  <div className="p-4 bg-amber-500/10 border border-amber-500/30 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-amber-300 font-medium">Sequence Paused</div>
                        {invoice.sequence_paused_reason && (
                          <div className="text-sm text-amber-400/70 mt-1">
                            Reason: {invoice.sequence_paused_reason}
                          </div>
                        )}
                      </div>
                      <button
                        onClick={handleResumeSequence}
                        disabled={isDemoMode || saving}
                        className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white rounded-lg text-sm transition"
                      >
                        Resume Sequence
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="p-4 bg-slate-800/50 border border-slate-700 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-white font-medium">Sequence Active</div>
                        <div className="text-sm text-slate-400 mt-1">
                          Automated reminders are enabled
                        </div>
                      </div>
                      <button
                        onClick={() => setShowPauseDialog(true)}
                        disabled={isDemoMode || saving}
                        className="px-4 py-2 bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white rounded-lg text-sm transition"
                      >
                        Pause Sequence
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {/* Pause Dialog */}
              {showPauseDialog && (
                <div className="mb-6 p-4 bg-slate-800 border border-slate-700 rounded-lg">
                  <h4 className="text-white font-medium mb-2">Pause Collection Sequence</h4>
                  <p className="text-sm text-slate-400 mb-3">
                    Optionally provide a reason for pausing (e.g., "Customer promised payment Friday")
                  </p>
                  <input
                    type="text"
                    value={pauseReason}
                    onChange={(e) => setPauseReason(e.target.value)}
                    placeholder="Reason (optional)"
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-500 mb-3"
                  />
                  <div className="flex justify-end gap-2">
                    <button
                      onClick={() => setShowPauseDialog(false)}
                      className="px-4 py-2 text-slate-400 hover:text-white transition"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handlePauseSequence}
                      disabled={saving}
                      className="px-4 py-2 bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white rounded-lg transition"
                    >
                      {saving ? 'Pausing...' : 'Pause Sequence'}
                    </button>
                  </div>
                </div>
              )}

              {/* Reminder History */}
              {invoice.fp_reminders && invoice.fp_reminders.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-slate-400 mb-2">Reminder History</h3>
                  <div className="space-y-2">
                    {invoice.fp_reminders.map((reminder) => (
                      <div
                        key={reminder.id}
                        className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg"
                      >
                        <div className="flex items-center gap-3">
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                            reminder.status === 'sent' ? 'bg-blue-500/20 text-blue-400' :
                            reminder.status === 'delivered' ? 'bg-emerald-500/20 text-emerald-400' :
                            'bg-slate-700 text-slate-400'
                          }`}>
                            {reminder.channel === 'email' ? '✉️' : '📱'}
                          </div>
                          <div>
                            <div className="text-sm text-white">
                              Step {reminder.step_number} - {reminder.channel.toUpperCase()}
                            </div>
                            <div className="text-xs text-slate-400">
                              {formatDateTime(reminder.sent_at)}
                            </div>
                          </div>
                        </div>
                        <div className="text-right text-xs">
                          {reminder.opened_at && (
                            <div className="text-emerald-400">Opened {formatDateTime(reminder.opened_at)}</div>
                          )}
                          {reminder.clicked_at && (
                            <div className="text-blue-400">Clicked {formatDateTime(reminder.clicked_at)}</div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex justify-end gap-3 mt-6 pt-4 border-t border-slate-700">
                <button
                  onClick={onClose}
                  className="px-4 py-2 text-slate-400 hover:text-white transition"
                >
                  Close
                </button>
              </div>
            </GlassCard>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
