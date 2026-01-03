/**
 * Friday Payday - Template Manager
 *
 * UI for managing email/SMS templates used in dunning sequences.
 * Supports editing, creating, and previewing templates.
 */
import { useEffect, useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { GlassCard } from '../ui/GlassCard'

interface Template {
  id: string
  tenant_id: string
  name: string
  channel: 'email' | 'sms'
  payer_type: string
  step_number: number
  subject: string | null
  body: string
  is_default: boolean
  created_at: string
  updated_at: string
}

interface TemplateManagerProps {
  accessToken: string
}

const PAYER_TYPES = [
  { value: 'homeowner_direct', label: 'Homeowner Direct' },
  { value: 'insurance_pending', label: 'Insurance Pending' },
  { value: 'supplement_pending', label: 'Supplement Pending' },
  { value: 'depreciation_recovery', label: 'Depreciation Recovery' },
  { value: 'gc_commercial', label: 'GC / Commercial' },
  { value: 'retainage', label: 'Retainage' },
]

const CHANNELS = [
  { value: 'email', label: 'Email' },
  { value: 'sms', label: 'SMS' },
]

// Template variables for preview
const PREVIEW_VARS = {
  customer_name: 'John Smith',
  company_name: 'ABC Roofing',
  invoice_number: 'INV-2024-001',
  amount: '$5,250.00',
  balance: '$5,250.00',
  due_date: 'January 15, 2024',
  days_overdue: '15',
  job_address: '123 Oak Street, Dallas TX',
  payment_link: 'https://pay.example.com/abc123',
}

export function TemplateManager({ accessToken }: TemplateManagerProps) {
  const [templates, setTemplates] = useState<Template[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [isCreating, setIsCreating] = useState(false)
  const [saving, setSaving] = useState(false)

  // Filter state
  const [filterChannel, setFilterChannel] = useState<string>('all')
  const [filterPayerType, setFilterPayerType] = useState<string>('all')

  // Edit form state
  const [editForm, setEditForm] = useState({
    name: '',
    channel: 'email' as 'email' | 'sms',
    payer_type: 'homeowner_direct',
    step_number: 1,
    subject: '',
    body: '',
  })

  const isDemoMode = accessToken === 'demo'

  const fetchTemplates = useCallback(async () => {
    if (isDemoMode) {
      // Demo templates
      setTemplates([
        {
          id: 'demo-1',
          tenant_id: 'demo',
          name: 'Friendly First Reminder',
          channel: 'email',
          payer_type: 'homeowner_direct',
          step_number: 1,
          subject: 'Friendly reminder: Invoice {{invoice_number}} is due',
          body: 'Hi {{customer_name}},\n\nThis is a friendly reminder that invoice {{invoice_number}} for {{amount}} is now due.\n\nPay online: {{payment_link}}\n\nThank you!\n{{company_name}}',
          is_default: true,
          created_at: '2024-01-01',
          updated_at: '2024-01-01',
        },
        {
          id: 'demo-2',
          tenant_id: 'demo',
          name: 'Past Due Notice',
          channel: 'email',
          payer_type: 'homeowner_direct',
          step_number: 2,
          subject: 'Past due: Invoice {{invoice_number}} - {{days_overdue}} days overdue',
          body: 'Hi {{customer_name}},\n\nYour invoice {{invoice_number}} for {{balance}} is now {{days_overdue}} days past due.\n\nPlease pay immediately: {{payment_link}}\n\nIf you have questions, please contact us.\n\n{{company_name}}',
          is_default: true,
          created_at: '2024-01-01',
          updated_at: '2024-01-01',
        },
        {
          id: 'demo-3',
          tenant_id: 'demo',
          name: 'SMS Reminder',
          channel: 'sms',
          payer_type: 'homeowner_direct',
          step_number: 1,
          subject: null,
          body: '{{company_name}}: Invoice {{invoice_number}} for {{amount}} is due. Pay now: {{payment_link}}',
          is_default: true,
          created_at: '2024-01-01',
          updated_at: '2024-01-01',
        },
      ])
      setLoading(false)
      return
    }

    try {
      const res = await fetch('/api/friday-payday/templates', {
        headers: { 'Authorization': `Bearer ${accessToken}` },
      })
      const data = await res.json()
      if (data.success) {
        setTemplates(data.templates || [])
      } else {
        setError(data.error || 'Failed to load templates')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load templates')
    } finally {
      setLoading(false)
    }
  }, [accessToken, isDemoMode])

  useEffect(() => {
    void fetchTemplates()
  }, [fetchTemplates])

  const handleEdit = (template: Template) => {
    setSelectedTemplate(template)
    setEditForm({
      name: template.name,
      channel: template.channel,
      payer_type: template.payer_type,
      step_number: template.step_number,
      subject: template.subject || '',
      body: template.body,
    })
    setIsEditing(true)
    setIsCreating(false)
  }

  const handleCreate = () => {
    setSelectedTemplate(null)
    setEditForm({
      name: '',
      channel: 'email',
      payer_type: 'homeowner_direct',
      step_number: 1,
      subject: '',
      body: '',
    })
    setIsCreating(true)
    setIsEditing(true)
  }

  const handleSave = async () => {
    if (isDemoMode) {
      setIsEditing(false)
      return
    }

    setSaving(true)
    try {
      const url = isCreating
        ? '/api/friday-payday/templates'
        : `/api/friday-payday/templates/${selectedTemplate?.id}`

      const res = await fetch(url, {
        method: isCreating ? 'POST' : 'PATCH',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(editForm),
      })

      const data = await res.json()
      if (data.success) {
        await fetchTemplates()
        setIsEditing(false)
      } else {
        setError(data.error || 'Failed to save template')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save template')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (templateId: string) => {
    if (isDemoMode) return
    if (!confirm('Are you sure you want to delete this template?')) return

    try {
      const res = await fetch(`/api/friday-payday/templates/${templateId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${accessToken}` },
      })

      const data = await res.json()
      if (data.success) {
        await fetchTemplates()
      } else {
        setError(data.error || 'Failed to delete template')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete template')
    }
  }

  const handleSeedDefaults = async () => {
    if (isDemoMode) return

    try {
      const res = await fetch('/api/friday-payday/templates/seed', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${accessToken}` },
      })

      const data = await res.json()
      if (data.success) {
        await fetchTemplates()
      } else {
        setError(data.error || 'Failed to seed templates')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to seed templates')
    }
  }

  // Render preview with variable substitution
  const renderPreview = (text: string) => {
    let result = text
    for (const [key, value] of Object.entries(PREVIEW_VARS)) {
      result = result.replace(new RegExp(`{{${key}}}`, 'g'), value)
    }
    return result
  }

  // Filter templates
  const filteredTemplates = templates.filter(t => {
    if (filterChannel !== 'all' && t.channel !== filterChannel) return false
    if (filterPayerType !== 'all' && t.payer_type !== filterPayerType) return false
    return true
  })

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
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Templates</h2>
          <p className="text-slate-400 text-sm">
            Manage email and SMS templates for collection reminders
          </p>
        </div>
        <div className="flex items-center gap-3">
          {templates.length === 0 && (
            <motion.button
              onClick={handleSeedDefaults}
              disabled={isDemoMode}
              className="px-4 py-2 bg-slate-600 hover:bg-slate-500 disabled:bg-slate-700 text-white rounded-lg transition"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              Load Defaults
            </motion.button>
          )}
          <motion.button
            onClick={handleCreate}
            disabled={isDemoMode}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-600 text-white rounded-lg transition"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <span>+</span>
            New Template
          </motion.button>
        </div>
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
            <button
              onClick={() => setError(null)}
              className="ml-4 text-red-300 hover:text-red-200"
            >
              ✕
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Filters */}
      <div className="flex gap-4">
        <select
          value={filterChannel}
          onChange={(e) => setFilterChannel(e.target.value)}
          className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white"
        >
          <option value="all">All Channels</option>
          {CHANNELS.map(c => (
            <option key={c.value} value={c.value}>{c.label}</option>
          ))}
        </select>
        <select
          value={filterPayerType}
          onChange={(e) => setFilterPayerType(e.target.value)}
          className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white"
        >
          <option value="all">All Payer Types</option>
          {PAYER_TYPES.map(p => (
            <option key={p.value} value={p.value}>{p.label}</option>
          ))}
        </select>
      </div>

      {/* Template List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {filteredTemplates.map((template) => (
          <GlassCard key={template.id} padding="md">
            <div className="space-y-3">
              {/* Header */}
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-white">{template.name}</h3>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={`px-2 py-0.5 text-xs rounded-full ${
                      template.channel === 'email'
                        ? 'bg-blue-500/20 text-blue-400'
                        : 'bg-purple-500/20 text-purple-400'
                    }`}>
                      {template.channel.toUpperCase()}
                    </span>
                    <span className="px-2 py-0.5 text-xs rounded-full bg-slate-600 text-slate-300">
                      Step {template.step_number}
                    </span>
                    <span className="text-xs text-slate-500">
                      {PAYER_TYPES.find(p => p.value === template.payer_type)?.label}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleEdit(template)}
                    className="p-2 text-slate-400 hover:text-white transition"
                    title="Edit"
                  >
                    ✏️
                  </button>
                  {!template.is_default && (
                    <button
                      onClick={() => handleDelete(template.id)}
                      disabled={isDemoMode}
                      className="p-2 text-slate-400 hover:text-red-400 transition disabled:opacity-50"
                      title="Delete"
                    >
                      🗑️
                    </button>
                  )}
                </div>
              </div>

              {/* Subject (email only) */}
              {template.channel === 'email' && template.subject && (
                <div className="text-sm text-slate-400">
                  <span className="text-slate-500">Subject:</span> {template.subject}
                </div>
              )}

              {/* Body preview */}
              <div className="p-3 bg-slate-800/50 rounded-lg text-sm text-slate-300 whitespace-pre-wrap max-h-32 overflow-y-auto">
                {template.body.substring(0, 200)}
                {template.body.length > 200 && '...'}
              </div>
            </div>
          </GlassCard>
        ))}
      </div>

      {filteredTemplates.length === 0 && (
        <div className="text-center py-12 text-slate-500">
          No templates found. Click "Load Defaults" to get started.
        </div>
      )}

      {/* Edit/Create Modal */}
      <AnimatePresence>
        {isEditing && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            onClick={() => setIsEditing(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-slate-900 border border-slate-700 rounded-xl w-full max-w-4xl max-h-[90vh] overflow-hidden"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Modal Header */}
              <div className="p-6 border-b border-slate-700">
                <h3 className="text-xl font-bold text-white">
                  {isCreating ? 'Create Template' : 'Edit Template'}
                </h3>
              </div>

              {/* Modal Body */}
              <div className="p-6 overflow-y-auto max-h-[60vh]">
                <div className="grid grid-cols-2 gap-6">
                  {/* Left: Form */}
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm text-slate-400 mb-1">Template Name</label>
                      <input
                        type="text"
                        value={editForm.name}
                        onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                        className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white"
                        placeholder="e.g., Friendly First Reminder"
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm text-slate-400 mb-1">Channel</label>
                        <select
                          value={editForm.channel}
                          onChange={(e) => setEditForm({ ...editForm, channel: e.target.value as 'email' | 'sms' })}
                          className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white"
                        >
                          {CHANNELS.map(c => (
                            <option key={c.value} value={c.value}>{c.label}</option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm text-slate-400 mb-1">Step Number</label>
                        <input
                          type="number"
                          min={1}
                          max={10}
                          value={editForm.step_number}
                          onChange={(e) => setEditForm({ ...editForm, step_number: parseInt(e.target.value) || 1 })}
                          className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm text-slate-400 mb-1">Payer Type</label>
                      <select
                        value={editForm.payer_type}
                        onChange={(e) => setEditForm({ ...editForm, payer_type: e.target.value })}
                        className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white"
                      >
                        {PAYER_TYPES.map(p => (
                          <option key={p.value} value={p.value}>{p.label}</option>
                        ))}
                      </select>
                    </div>

                    {editForm.channel === 'email' && (
                      <div>
                        <label className="block text-sm text-slate-400 mb-1">Subject</label>
                        <input
                          type="text"
                          value={editForm.subject}
                          onChange={(e) => setEditForm({ ...editForm, subject: e.target.value })}
                          className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white"
                          placeholder="e.g., Invoice {{invoice_number}} is due"
                        />
                      </div>
                    )}

                    <div>
                      <label className="block text-sm text-slate-400 mb-1">
                        Body {editForm.channel === 'sms' && '(160 chars recommended)'}
                      </label>
                      <textarea
                        value={editForm.body}
                        onChange={(e) => setEditForm({ ...editForm, body: e.target.value })}
                        rows={8}
                        className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white font-mono text-sm"
                        placeholder="Enter template body..."
                      />
                      {editForm.channel === 'sms' && (
                        <div className="text-xs text-slate-500 mt-1">
                          {editForm.body.length} characters
                        </div>
                      )}
                    </div>

                    {/* Variables help */}
                    <div className="p-3 bg-slate-800/50 rounded-lg">
                      <div className="text-xs text-slate-400 mb-2">Available Variables:</div>
                      <div className="flex flex-wrap gap-1">
                        {Object.keys(PREVIEW_VARS).map(v => (
                          <code
                            key={v}
                            className="px-1.5 py-0.5 bg-slate-700 text-emerald-400 text-xs rounded cursor-pointer hover:bg-slate-600"
                            onClick={() => {
                              const textarea = document.querySelector('textarea')
                              if (textarea) {
                                const pos = textarea.selectionStart
                                const before = editForm.body.substring(0, pos)
                                const after = editForm.body.substring(pos)
                                setEditForm({ ...editForm, body: `${before}{{${v}}}${after}` })
                              }
                            }}
                          >
                            {`{{${v}}}`}
                          </code>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Right: Preview */}
                  <div className="space-y-4">
                    <h4 className="text-sm font-semibold text-slate-400">Preview</h4>

                    {editForm.channel === 'email' ? (
                      <div className="bg-white rounded-lg p-4 text-slate-800">
                        <div className="border-b border-slate-200 pb-2 mb-3">
                          <div className="text-xs text-slate-500">Subject:</div>
                          <div className="font-medium">
                            {renderPreview(editForm.subject || '(no subject)')}
                          </div>
                        </div>
                        <div className="whitespace-pre-wrap text-sm">
                          {renderPreview(editForm.body || '(no body)')}
                        </div>
                      </div>
                    ) : (
                      <div className="bg-slate-800 rounded-2xl p-4 max-w-xs">
                        <div className="bg-emerald-600 text-white rounded-2xl rounded-bl-md p-3 text-sm">
                          {renderPreview(editForm.body || '(no message)')}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Modal Footer */}
              <div className="p-6 border-t border-slate-700 flex justify-end gap-3">
                <button
                  onClick={() => setIsEditing(false)}
                  className="px-4 py-2 text-slate-400 hover:text-white transition"
                >
                  Cancel
                </button>
                <motion.button
                  onClick={handleSave}
                  disabled={saving || isDemoMode || !editForm.name || !editForm.body}
                  className="px-6 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-600 text-white rounded-lg transition"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {saving ? 'Saving...' : 'Save Template'}
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
