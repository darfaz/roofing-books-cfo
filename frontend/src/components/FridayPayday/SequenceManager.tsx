/**
 * Friday Payday - Sequence Manager
 *
 * UI for configuring dunning sequences per payer type.
 * Each sequence defines the steps (reminders) sent at specific intervals.
 */
import { useEffect, useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { GlassCard } from '../ui/GlassCard'

interface SequenceStep {
  step_number: number
  days_from_due: number
  channel: 'email' | 'sms'
  template_id: string | null
}

interface Sequence {
  id: string
  tenant_id: string
  name: string
  payer_type: string
  is_default: boolean
  steps: SequenceStep[]
  created_at: string
  updated_at: string
}

interface Template {
  id: string
  name: string
  channel: 'email' | 'sms'
  payer_type: string
  step_number: number
}

interface SequenceManagerProps {
  accessToken: string
}

const PAYER_TYPES = [
  { value: 'homeowner_direct', label: 'Homeowner Direct', color: 'emerald', description: 'Direct homeowner payments' },
  { value: 'insurance_pending', label: 'Insurance Pending', color: 'blue', description: 'Waiting on insurance check' },
  { value: 'supplement_pending', label: 'Supplement Pending', color: 'amber', description: 'Supplement approval needed' },
  { value: 'depreciation_recovery', label: 'Depreciation Recovery', color: 'purple', description: 'Recoverable depreciation' },
  { value: 'gc_commercial', label: 'GC / Commercial', color: 'cyan', description: 'General contractor or commercial' },
  { value: 'retainage', label: 'Retainage', color: 'orange', description: 'Held retainage amounts' },
]

const DEFAULT_SEQUENCES: Record<string, SequenceStep[]> = {
  homeowner_direct: [
    { step_number: 1, days_from_due: 0, channel: 'email', template_id: null },
    { step_number: 2, days_from_due: 7, channel: 'email', template_id: null },
    { step_number: 3, days_from_due: 14, channel: 'sms', template_id: null },
    { step_number: 4, days_from_due: 21, channel: 'email', template_id: null },
  ],
  insurance_pending: [
    { step_number: 1, days_from_due: 7, channel: 'email', template_id: null },
    { step_number: 2, days_from_due: 21, channel: 'email', template_id: null },
    { step_number: 3, days_from_due: 45, channel: 'email', template_id: null },
  ],
  supplement_pending: [
    { step_number: 1, days_from_due: 30, channel: 'email', template_id: null },
  ],
  gc_commercial: [
    { step_number: 1, days_from_due: 0, channel: 'email', template_id: null },
    { step_number: 2, days_from_due: 30, channel: 'email', template_id: null },
  ],
  depreciation_recovery: [
    { step_number: 1, days_from_due: 14, channel: 'email', template_id: null },
    { step_number: 2, days_from_due: 30, channel: 'email', template_id: null },
  ],
  retainage: [
    { step_number: 1, days_from_due: 60, channel: 'email', template_id: null },
  ],
}

export function SequenceManager({ accessToken }: SequenceManagerProps) {
  const [sequences, setSequences] = useState<Sequence[]>([])
  const [templates, setTemplates] = useState<Template[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedPayerType, setSelectedPayerType] = useState<string>('homeowner_direct')
  const [editingSequence, setEditingSequence] = useState<Sequence | null>(null)
  const [editSteps, setEditSteps] = useState<SequenceStep[]>([])
  const [saving, setSaving] = useState(false)

  const isDemoMode = accessToken === 'demo'

  const fetchData = useCallback(async () => {
    if (isDemoMode) {
      // Demo sequences
      const demoSequences: Sequence[] = PAYER_TYPES.map(pt => ({
        id: `demo-seq-${pt.value}`,
        tenant_id: 'demo',
        name: `${pt.label} Sequence`,
        payer_type: pt.value,
        is_default: true,
        steps: DEFAULT_SEQUENCES[pt.value] || [],
        created_at: '2024-01-01',
        updated_at: '2024-01-01',
      }))
      setSequences(demoSequences)
      setTemplates([])
      setLoading(false)
      return
    }

    try {
      const [seqRes, tplRes] = await Promise.all([
        fetch('/api/friday-payday/sequences', {
          headers: { 'Authorization': `Bearer ${accessToken}` },
        }),
        fetch('/api/friday-payday/templates', {
          headers: { 'Authorization': `Bearer ${accessToken}` },
        }),
      ])

      const seqData = await seqRes.json()
      const tplData = await tplRes.json()

      if (seqData.success) {
        setSequences(seqData.sequences || [])
      }
      if (tplData.success) {
        setTemplates(tplData.templates || [])
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }, [accessToken, isDemoMode])

  useEffect(() => {
    void fetchData()
  }, [fetchData])

  const getCurrentSequence = () => {
    return sequences.find(s => s.payer_type === selectedPayerType) || null
  }

  const handleEditSequence = () => {
    const seq = getCurrentSequence()
    if (seq) {
      setEditingSequence(seq)
      setEditSteps([...seq.steps])
    } else {
      // Create new sequence
      setEditingSequence({
        id: '',
        tenant_id: '',
        name: `${PAYER_TYPES.find(p => p.value === selectedPayerType)?.label} Sequence`,
        payer_type: selectedPayerType,
        is_default: false,
        steps: DEFAULT_SEQUENCES[selectedPayerType] || [],
        created_at: '',
        updated_at: '',
      })
      setEditSteps(DEFAULT_SEQUENCES[selectedPayerType] || [])
    }
  }

  const handleAddStep = () => {
    const nextStep = editSteps.length + 1
    const lastDays = editSteps[editSteps.length - 1]?.days_from_due || 0
    setEditSteps([
      ...editSteps,
      {
        step_number: nextStep,
        days_from_due: lastDays + 7,
        channel: 'email',
        template_id: null,
      },
    ])
  }

  const handleRemoveStep = (index: number) => {
    const newSteps = editSteps.filter((_, i) => i !== index)
    // Renumber steps
    newSteps.forEach((s, i) => {
      s.step_number = i + 1
    })
    setEditSteps(newSteps)
  }

  const handleUpdateStep = (index: number, field: keyof SequenceStep, value: number | string | null) => {
    const newSteps = [...editSteps]
    newSteps[index] = { ...newSteps[index], [field]: value }
    setEditSteps(newSteps)
  }

  const handleSave = async () => {
    if (isDemoMode) {
      setEditingSequence(null)
      return
    }

    setSaving(true)
    try {
      const isNew = !editingSequence?.id
      const url = isNew
        ? '/api/friday-payday/sequences'
        : `/api/friday-payday/sequences/${editingSequence?.id}`

      const res = await fetch(url, {
        method: isNew ? 'POST' : 'PATCH',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: editingSequence?.name,
          payer_type: selectedPayerType,
          steps: editSteps,
        }),
      })

      const data = await res.json()
      if (data.success) {
        await fetchData()
        setEditingSequence(null)
      } else {
        setError(data.error || 'Failed to save sequence')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save sequence')
    } finally {
      setSaving(false)
    }
  }

  const currentSequence = getCurrentSequence()
  const currentPayerInfo = PAYER_TYPES.find(p => p.value === selectedPayerType)

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white">Dunning Sequences</h2>
        <p className="text-slate-400 text-sm">
          Configure automated reminder schedules for each payer type
        </p>
      </div>

      {/* Error */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="p-4 bg-red-500/20 border border-red-500/30 rounded-lg text-red-400"
          >
            {error}
            <button onClick={() => setError(null)} className="ml-4 text-red-300 hover:text-red-200">✕</button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Payer Type Tabs */}
      <div className="flex flex-wrap gap-2">
        {PAYER_TYPES.map((pt) => {
          const hasSequence = sequences.some(s => s.payer_type === pt.value)
          return (
            <button
              key={pt.value}
              onClick={() => setSelectedPayerType(pt.value)}
              className={`px-4 py-2 rounded-lg transition flex items-center gap-2 ${
                selectedPayerType === pt.value
                  ? 'bg-emerald-600 text-white'
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }`}
            >
              {pt.label}
              {hasSequence && (
                <span className="w-2 h-2 rounded-full bg-emerald-400" />
              )}
            </button>
          )
        })}
      </div>

      {/* Current Sequence Display */}
      <GlassCard padding="lg">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h3 className="text-xl font-semibold text-white">
              {currentPayerInfo?.label} Sequence
            </h3>
            <p className="text-slate-400 text-sm mt-1">
              {currentPayerInfo?.description}
            </p>
          </div>
          <motion.button
            onClick={handleEditSequence}
            disabled={isDemoMode}
            className="px-4 py-2 bg-slate-700 hover:bg-slate-600 disabled:bg-slate-800 text-white rounded-lg transition"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {currentSequence ? 'Edit Sequence' : 'Create Sequence'}
          </motion.button>
        </div>

        {/* Timeline */}
        {currentSequence ? (
          <div className="relative">
            {/* Timeline line */}
            <div className="absolute left-6 top-8 bottom-8 w-0.5 bg-slate-700" />

            <div className="space-y-6">
              {currentSequence.steps.map((step, index) => (
                <div key={index} className="relative flex items-start gap-4">
                  {/* Timeline dot */}
                  <div className={`relative z-10 w-12 h-12 rounded-full flex items-center justify-center ${
                    step.channel === 'email' ? 'bg-blue-500/20 text-blue-400' : 'bg-purple-500/20 text-purple-400'
                  }`}>
                    {step.channel === 'email' ? '📧' : '📱'}
                  </div>

                  {/* Content */}
                  <div className="flex-1 bg-slate-800/50 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium text-white">Step {step.step_number}</div>
                        <div className="text-sm text-slate-400">
                          {step.days_from_due === 0
                            ? 'On due date'
                            : step.days_from_due > 0
                              ? `${step.days_from_due} days after due`
                              : `${Math.abs(step.days_from_due)} days before due`
                          }
                        </div>
                      </div>
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        step.channel === 'email'
                          ? 'bg-blue-500/20 text-blue-400'
                          : 'bg-purple-500/20 text-purple-400'
                      }`}>
                        {step.channel.toUpperCase()}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {currentSequence.steps.length === 0 && (
              <div className="text-center py-8 text-slate-500">
                No steps configured. Click "Edit Sequence" to add steps.
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-12 text-slate-500">
            No sequence configured for this payer type.
            <br />
            Click "Create Sequence" to set up automated reminders.
          </div>
        )}
      </GlassCard>

      {/* Edit Modal */}
      <AnimatePresence>
        {editingSequence && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            onClick={() => setEditingSequence(null)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-slate-900 border border-slate-700 rounded-xl w-full max-w-2xl max-h-[90vh] overflow-hidden"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header */}
              <div className="p-6 border-b border-slate-700">
                <h3 className="text-xl font-bold text-white">
                  Edit {currentPayerInfo?.label} Sequence
                </h3>
                <p className="text-slate-400 text-sm mt-1">
                  Configure when and how reminders are sent
                </p>
              </div>

              {/* Body */}
              <div className="p-6 overflow-y-auto max-h-[60vh]">
                <div className="space-y-4">
                  {editSteps.map((step, index) => (
                    <div
                      key={index}
                      className="flex items-center gap-4 p-4 bg-slate-800/50 rounded-lg"
                    >
                      <div className="text-slate-500 font-medium w-16">
                        Step {step.step_number}
                      </div>

                      <div className="flex-1 grid grid-cols-3 gap-4">
                        <div>
                          <label className="block text-xs text-slate-500 mb-1">Days from due</label>
                          <input
                            type="number"
                            value={step.days_from_due}
                            onChange={(e) => handleUpdateStep(index, 'days_from_due', parseInt(e.target.value) || 0)}
                            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded text-white text-sm"
                          />
                        </div>

                        <div>
                          <label className="block text-xs text-slate-500 mb-1">Channel</label>
                          <select
                            value={step.channel}
                            onChange={(e) => handleUpdateStep(index, 'channel', e.target.value)}
                            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded text-white text-sm"
                          >
                            <option value="email">Email</option>
                            <option value="sms">SMS</option>
                          </select>
                        </div>

                        <div>
                          <label className="block text-xs text-slate-500 mb-1">Template</label>
                          <select
                            value={step.template_id || ''}
                            onChange={(e) => handleUpdateStep(index, 'template_id', e.target.value || null)}
                            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded text-white text-sm"
                          >
                            <option value="">Default</option>
                            {templates
                              .filter(t => t.channel === step.channel && t.payer_type === selectedPayerType)
                              .map(t => (
                                <option key={t.id} value={t.id}>{t.name}</option>
                              ))
                            }
                          </select>
                        </div>
                      </div>

                      <button
                        onClick={() => handleRemoveStep(index)}
                        className="p-2 text-slate-500 hover:text-red-400 transition"
                        title="Remove step"
                      >
                        ✕
                      </button>
                    </div>
                  ))}

                  <button
                    onClick={handleAddStep}
                    className="w-full p-4 border-2 border-dashed border-slate-700 rounded-lg text-slate-500 hover:text-slate-300 hover:border-slate-600 transition"
                  >
                    + Add Step
                  </button>
                </div>
              </div>

              {/* Footer */}
              <div className="p-6 border-t border-slate-700 flex justify-end gap-3">
                <button
                  onClick={() => setEditingSequence(null)}
                  className="px-4 py-2 text-slate-400 hover:text-white transition"
                >
                  Cancel
                </button>
                <motion.button
                  onClick={handleSave}
                  disabled={saving || isDemoMode}
                  className="px-6 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-600 text-white rounded-lg transition"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {saving ? 'Saving...' : 'Save Sequence'}
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
