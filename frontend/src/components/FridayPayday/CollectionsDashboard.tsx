/**
 * Friday Payday - Collections Dashboard
 *
 * Main dashboard for AR collections automation.
 * Shows AR aging, DSO metrics, and invoice management.
 */
import { useEffect, useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { GlassCard } from '../ui/GlassCard'
import { InvoiceDetailModal } from './InvoiceDetailModal'

interface ARAgingBucket {
  bucket: string
  amount: number
  count: number
  percentage: number
}

interface ARAgingSummary {
  tenant_id: string
  as_of_date: string
  buckets: ARAgingBucket[]
  total_ar: number
  total_invoices: number
  dso: number | null
}

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

interface CollectionMetrics {
  period_start: string
  period_end: string
  amount_collected: number
  invoices_paid: number
  reminders_sent: number
  reminders_opened: number
  reminders_clicked: number
}

interface CollectionsDashboardProps {
  accessToken: string
  isDemoMode?: boolean
}

const PAYER_TYPE_LABELS: Record<string, { label: string; color: string }> = {
  homeowner_direct: { label: 'Homeowner', color: 'emerald' },
  insurance_pending: { label: 'Insurance', color: 'blue' },
  supplement_pending: { label: 'Supplement', color: 'purple' },
  depreciation_recovery: { label: 'Depreciation', color: 'amber' },
  gc_commercial: { label: 'Commercial', color: 'slate' },
  retainage: { label: 'Retainage', color: 'rose' },
}

const STATUS_LABELS: Record<string, { label: string; color: string }> = {
  sent: { label: 'Sent', color: 'blue' },
  partial: { label: 'Partial', color: 'amber' },
  overdue: { label: 'Overdue', color: 'red' },
  paid: { label: 'Paid', color: 'emerald' },
  disputed: { label: 'Disputed', color: 'rose' },
}

const BUCKET_COLORS: Record<string, string> = {
  current: 'bg-emerald-500',
  '1-30': 'bg-blue-500',
  '31-60': 'bg-amber-500',
  '61-90': 'bg-orange-500',
  '90+': 'bg-red-500',
}

const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  })
}

export function CollectionsDashboard({ accessToken, isDemoMode = false }: CollectionsDashboardProps) {
  const [aging, setAging] = useState<ARAgingSummary | null>(null)
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [metrics, setMetrics] = useState<CollectionMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [filterPayerType, setFilterPayerType] = useState<string>('all')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [selectedInvoice, setSelectedInvoice] = useState<Invoice | null>(null)
  const [modalOpen, setModalOpen] = useState(false)

  const fetchData = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      }
      if (!isDemoMode) {
        headers['Authorization'] = `Bearer ${accessToken}`
      }

      // Fetch AR aging
      const agingRes = await fetch(
        isDemoMode ? '/api/friday-payday/demo' : '/api/friday-payday/analytics/aging',
        { headers }
      )
      if (agingRes.ok) {
        const agingData = await agingRes.json()
        if (isDemoMode) {
          // Demo API returns { success: true, data: { invoices, aging, metrics } }
          const data = agingData.data || agingData
          setAging(data.aging)
          setInvoices(data.invoices || [])
          setMetrics(data.metrics || null)
        } else {
          // Aging API returns { success: true, data: {...} }
          setAging(agingData.data || agingData)
        }
      }

      // Fetch invoices (non-demo mode)
      if (!isDemoMode) {
        const invoicesRes = await fetch('/api/friday-payday/invoices', { headers })
        if (invoicesRes.ok) {
          const invoicesData = await invoicesRes.json()
          // API returns { success: true, data: { invoices: [...] } }
          setInvoices(invoicesData.data?.invoices || invoicesData.invoices || [])
        }

        // Fetch collection metrics
        const metricsRes = await fetch('/api/friday-payday/analytics/collected?days=7', { headers })
        if (metricsRes.ok) {
          const metricsData = await metricsRes.json()
          // API returns { success: true, data: {...} }
          setMetrics(metricsData.data || metricsData)
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load collections data')
    } finally {
      setLoading(false)
    }
  }, [accessToken, isDemoMode])

  useEffect(() => {
    void fetchData()
  }, [fetchData])

  const handleSync = async () => {
    try {
      setSyncing(true)
      setError(null)

      const res = await fetch('/api/friday-payday/sync', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
      })

      const data = await res.json()

      if (!res.ok) {
        // Handle FastAPI error response format
        const errorMsg = data?.detail?.error?.message || data?.detail || data?.error || 'Sync failed'
        setError(typeof errorMsg === 'string' ? errorMsg : 'Sync failed')
        return
      }

      // Sync completed - refresh data
      console.log('Sync result:', data)
      await fetchData()

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Sync failed')
    } finally {
      setSyncing(false)
    }
  }

  const handleInvoiceClick = (invoice: Invoice) => {
    setSelectedInvoice(invoice)
    setModalOpen(true)
  }

  const handleCloseModal = () => {
    setModalOpen(false)
    setSelectedInvoice(null)
  }

  const handleUpdateInvoice = async (invoiceId: string, updates: Record<string, unknown>) => {
    try {
      const res = await fetch(`/api/friday-payday/invoices/${invoiceId}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates),
      })
      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.error || 'Failed to update invoice')
      }
      // Update local state
      setInvoices((prev) =>
        prev.map((inv) => (inv.id === invoiceId ? { ...inv, ...updates } : inv))
      )
      if (selectedInvoice?.id === invoiceId) {
        setSelectedInvoice((prev) => prev ? { ...prev, ...updates } : null)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update invoice')
    }
  }

  const handlePauseSequence = async (invoiceId: string, reason?: string) => {
    try {
      const res = await fetch(`/api/friday-payday/invoices/${invoiceId}/pause`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ reason }),
      })
      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.error || 'Failed to pause sequence')
      }
      // Update local state
      const updates = { sequence_status: 'paused', sequence_paused_reason: reason || null }
      setInvoices((prev) =>
        prev.map((inv) => (inv.id === invoiceId ? { ...inv, ...updates } : inv))
      )
      if (selectedInvoice?.id === invoiceId) {
        setSelectedInvoice((prev) => prev ? { ...prev, ...updates } : null)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to pause sequence')
    }
  }

  const handleResumeSequence = async (invoiceId: string) => {
    try {
      const res = await fetch(`/api/friday-payday/invoices/${invoiceId}/resume`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
      })
      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.error || 'Failed to resume sequence')
      }
      // Update local state
      const updates = { sequence_status: 'active', sequence_paused_reason: null }
      setInvoices((prev) =>
        prev.map((inv) => (inv.id === invoiceId ? { ...inv, ...updates } : inv))
      )
      if (selectedInvoice?.id === invoiceId) {
        setSelectedInvoice((prev) => prev ? { ...prev, ...updates } : null)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to resume sequence')
    }
  }

  const filteredInvoices = invoices.filter((inv) => {
    if (filterPayerType !== 'all' && inv.payer_type !== filterPayerType) return false
    if (filterStatus !== 'all' && inv.status !== filterStatus) return false
    return true
  })

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <motion.div
          className="flex items-center gap-3 text-slate-400"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <motion.div
            className="w-6 h-6 border-2 border-emerald-500 border-t-transparent rounded-full"
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          />
          Loading collections data...
        </motion.div>
      </div>
    )
  }

  if (error) {
    return (
      <GlassCard variant="danger">
        <div className="flex items-center gap-3">
          <span className="text-2xl">⚠️</span>
          <div>
            <div className="font-semibold text-red-300">Error Loading Data</div>
            <div className="text-sm text-red-400/80">{error}</div>
          </div>
          <button
            onClick={() => void fetchData()}
            className="ml-auto px-4 py-2 bg-red-500/20 hover:bg-red-500/30 rounded-lg text-sm"
          >
            Retry
          </button>
        </div>
      </GlassCard>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header with actions */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Collections</h2>
          <p className="text-slate-400 text-sm">
            {aging?.as_of_date && `As of ${formatDate(aging.as_of_date)}`}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <motion.button
            onClick={handleSync}
            disabled={syncing || isDemoMode}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-600 text-white rounded-lg transition"
            whileHover={{ scale: syncing ? 1 : 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {syncing ? (
              <>
                <motion.div
                  className="w-4 h-4 border-2 border-white border-t-transparent rounded-full"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                />
                Syncing...
              </>
            ) : (
              <>
                <span>🔄</span>
                Sync Invoices
              </>
            )}
          </motion.button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <GlassCard padding="md">
          <div className="text-slate-400 text-sm">Total AR</div>
          <div className="text-2xl font-bold text-white">
            {aging ? formatCurrency(aging.total_ar) : '$0'}
          </div>
          <div className="text-slate-500 text-xs">
            {aging?.total_invoices || 0} invoices
          </div>
        </GlassCard>

        <GlassCard padding="md">
          <div className="text-slate-400 text-sm">DSO</div>
          <div className="text-2xl font-bold text-white">
            {aging?.dso ? `${aging.dso.toFixed(0)} days` : '—'}
          </div>
          <div className="text-slate-500 text-xs">
            Industry avg: 83 days
          </div>
        </GlassCard>

        <GlassCard padding="md">
          <div className="text-slate-400 text-sm">Collected (7d)</div>
          <div className="text-2xl font-bold text-emerald-400">
            {metrics ? formatCurrency(metrics.amount_collected) : '$0'}
          </div>
          <div className="text-slate-500 text-xs">
            {metrics?.invoices_paid || 0} invoices paid
          </div>
        </GlassCard>

        <GlassCard padding="md">
          <div className="text-slate-400 text-sm">Reminders Sent</div>
          <div className="text-2xl font-bold text-white">
            {metrics?.reminders_sent || 0}
          </div>
          <div className="text-slate-500 text-xs">
            {metrics ? `${metrics.reminders_opened} opened` : '—'}
          </div>
        </GlassCard>
      </div>

      {/* AR Aging Chart */}
      {aging && aging.buckets.length > 0 && (
        <GlassCard padding="md">
          <h3 className="text-lg font-semibold text-white mb-4">AR Aging</h3>

          {/* Stacked bar */}
          <div className="h-8 rounded-lg overflow-hidden flex mb-4">
            {aging.buckets.map((bucket) => (
              <motion.div
                key={bucket.bucket}
                className={`${BUCKET_COLORS[bucket.bucket] || 'bg-slate-500'} relative`}
                style={{ width: `${bucket.percentage}%` }}
                initial={{ width: 0 }}
                animate={{ width: `${bucket.percentage}%` }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
                title={`${bucket.bucket}: ${formatCurrency(bucket.amount)} (${bucket.percentage}%)`}
              />
            ))}
          </div>

          {/* Legend */}
          <div className="grid grid-cols-5 gap-4">
            {aging.buckets.map((bucket) => (
              <div key={bucket.bucket} className="text-center">
                <div className="flex items-center justify-center gap-2 mb-1">
                  <div className={`w-3 h-3 rounded ${BUCKET_COLORS[bucket.bucket] || 'bg-slate-500'}`} />
                  <span className="text-slate-400 text-xs uppercase">{bucket.bucket}</span>
                </div>
                <div className="text-white font-semibold">{formatCurrency(bucket.amount)}</div>
                <div className="text-slate-500 text-xs">{bucket.count} inv</div>
              </div>
            ))}
          </div>
        </GlassCard>
      )}

      {/* Invoice List */}
      <GlassCard padding="md">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">Open Invoices</h3>

          {/* Filters */}
          <div className="flex items-center gap-3">
            <select
              value={filterPayerType}
              onChange={(e) => setFilterPayerType(e.target.value)}
              className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-sm text-white"
            >
              <option value="all">All Types</option>
              {Object.entries(PAYER_TYPE_LABELS).map(([value, { label }]) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-sm text-white"
            >
              <option value="all">All Status</option>
              {Object.entries(STATUS_LABELS).map(([value, { label }]) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>
          </div>
        </div>

        {filteredInvoices.length === 0 ? (
          <div className="text-center py-12 text-slate-400">
            <div className="text-4xl mb-3">📄</div>
            <p>No invoices found</p>
            {!isDemoMode && (
              <p className="text-sm mt-2">
                Click "Sync Invoices" to import from QuickBooks
              </p>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-slate-400 text-sm border-b border-slate-700">
                  <th className="pb-3 font-medium">Invoice</th>
                  <th className="pb-3 font-medium">Customer</th>
                  <th className="pb-3 font-medium">Type</th>
                  <th className="pb-3 font-medium text-right">Amount</th>
                  <th className="pb-3 font-medium text-right">Balance</th>
                  <th className="pb-3 font-medium">Due</th>
                  <th className="pb-3 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                <AnimatePresence>
                  {filteredInvoices.slice(0, 20).map((invoice, idx) => {
                    const payerConfig = PAYER_TYPE_LABELS[invoice.payer_type] || { label: invoice.payer_type, color: 'slate' }
                    const statusConfig = STATUS_LABELS[invoice.status] || { label: invoice.status, color: 'slate' }

                    return (
                      <motion.tr
                        key={invoice.id}
                        className="border-b border-slate-800 hover:bg-slate-800/50 transition-colors cursor-pointer"
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.03 }}
                        onClick={() => handleInvoiceClick(invoice)}
                      >
                        <td className="py-3">
                          <div className="font-medium text-white">
                            {invoice.invoice_number || '—'}
                          </div>
                          {invoice.job_address && (
                            <div className="text-xs text-slate-500 truncate max-w-[150px]">
                              {invoice.job_address}
                            </div>
                          )}
                        </td>
                        <td className="py-3 text-slate-300">{invoice.customer_name}</td>
                        <td className="py-3">
                          <span className={`inline-block px-2 py-0.5 rounded text-xs bg-${payerConfig.color}-500/20 text-${payerConfig.color}-300`}>
                            {payerConfig.label}
                          </span>
                        </td>
                        <td className="py-3 text-right text-slate-300">
                          {formatCurrency(invoice.amount)}
                        </td>
                        <td className="py-3 text-right font-medium text-white">
                          {formatCurrency(invoice.balance)}
                        </td>
                        <td className="py-3">
                          <div className={invoice.days_overdue > 0 ? 'text-red-400' : 'text-slate-300'}>
                            {formatDate(invoice.due_date)}
                          </div>
                          {invoice.days_overdue > 0 && (
                            <div className="text-xs text-red-500">
                              {invoice.days_overdue}d overdue
                            </div>
                          )}
                        </td>
                        <td className="py-3">
                          <span className={`inline-block px-2 py-0.5 rounded text-xs bg-${statusConfig.color}-500/20 text-${statusConfig.color}-300`}>
                            {statusConfig.label}
                          </span>
                        </td>
                      </motion.tr>
                    )
                  })}
                </AnimatePresence>
              </tbody>
            </table>
            {filteredInvoices.length > 20 && (
              <div className="text-center py-4 text-slate-400 text-sm">
                Showing 20 of {filteredInvoices.length} invoices
              </div>
            )}
          </div>
        )}
      </GlassCard>

      {/* Invoice Detail Modal */}
      <InvoiceDetailModal
        invoice={selectedInvoice}
        isOpen={modalOpen}
        onClose={handleCloseModal}
        onUpdate={handleUpdateInvoice}
        onPauseSequence={handlePauseSequence}
        onResumeSequence={handleResumeSequence}
        isDemoMode={isDemoMode}
      />
    </div>
  )
}
