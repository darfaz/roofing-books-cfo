import { useEffect, useMemo, useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { supabase } from '../lib/supabase'
import { GlassCard, ProgressCard } from './ui/GlassCard'

interface ChecklistItem {
  key: string
  label: string
  description: string
  icon: string
}

interface UploadedDoc {
  id: string
  checklist_key: string
  file_name: string
  content_type: string | null
  size_bytes: number | null
  created_at: string
  storage_bucket: string
  storage_path: string
}

const CHECKLIST_ITEMS: ChecklistItem[] = [
  {
    key: 'financial_statements',
    label: 'Financial Statements',
    description: '3-5 years of P&L, Balance Sheet, and Cash Flow statements',
    icon: '📊',
  },
  {
    key: 'tax_returns',
    label: 'Tax Returns',
    description: 'Federal and state tax returns for the past 3-5 years',
    icon: '📋',
  },
  {
    key: 'ar_ap_aging',
    label: 'AR/AP Aging Reports',
    description: 'Current accounts receivable and payable aging schedules',
    icon: '💰',
  },
  {
    key: 'asset_list',
    label: 'Asset List',
    description: 'Fixed assets, equipment, vehicles with values and depreciation',
    icon: '🏗️',
  },
  {
    key: 'org_chart',
    label: 'Organization Chart',
    description: 'Company structure with key personnel and responsibilities',
    icon: '👥',
  },
  {
    key: 'kpi_dashboard',
    label: 'KPI Dashboard',
    description: 'Key performance metrics and unit economics',
    icon: '📈',
  },
  {
    key: 'safety_insurance',
    label: 'Safety & Insurance',
    description: 'Safety records, insurance policies, and compliance docs',
    icon: '🛡️',
  },
]

const CIM_OUTLINE = `# Confidential Information Memorandum (CIM) Outline

## 1. Executive Summary
- Business overview and investment highlights
- Key financial metrics and growth trajectory
- Transaction rationale

## 2. Company Overview
- History and founding story
- Mission, vision, and values
- Geographic footprint and service areas

## 3. Services & Markets
- Core service offerings
- Target markets and customer segments
- Competitive positioning and differentiation

## 4. Operations & Crew Structure
- Operational workflow and processes
- Crew organization and capabilities
- Equipment and technology stack

## 5. Financial Overview (3-5 Years)
- Revenue growth and profitability trends
- Key financial metrics and ratios
- Working capital and cash flow analysis

## 6. KPI Dashboard & Unit Economics
- Job profitability metrics
- Crew efficiency and utilization
- Customer acquisition costs and lifetime value

## 7. Customers & Backlog
- Customer concentration analysis
- Top customer profiles
- Sales pipeline and backlog visibility

## 8. Assets & Equipment
- Owned vs. leased assets
- Vehicle and equipment inventory
- Real estate and facilities

## 9. Safety, Insurance & Compliance
- Safety record and certifications
- Insurance coverage summary
- Regulatory compliance status

## 10. Organization & Key Personnel
- Management team bios
- Organizational structure
- Key employee retention considerations

## 11. Growth Opportunities
- Market expansion potential
- Service line extensions
- Acquisition opportunities

## 12. Transaction Considerations
- Deal structure preferences
- Transition support availability
- Key terms and conditions

---

## Appendix: Due Diligence Documents
- Financial statements (3-5 years)
- Tax returns
- AR/AP aging reports
- Asset list
- Org chart
- KPI dashboard
- Safety/insurance documentation
`

export function ExitReadiness({ accessToken }: { accessToken: string }) {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [documents, setDocuments] = useState<UploadedDoc[]>([])
  const [uploadingKey, setUploadingKey] = useState<string | null>(null)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [expandedKey, setExpandedKey] = useState<string | null>(null)
  const fileInputRefs = useRef<Record<string, HTMLInputElement | null>>({})

  const fetchDocuments = async () => {
    try {
      setLoading(true)
      setError(null)

      const { data: { user } } = await supabase.auth.getUser()
      const tenantId = user?.user_metadata?.tenant_id

      if (!tenantId) {
        setError('No tenant_id found in user metadata')
        return
      }

      const { data, error: fetchError } = await supabase
        .from('exit_readiness_documents')
        .select('*')
        .eq('tenant_id', tenantId)
        .order('created_at', { ascending: false })

      if (fetchError) {
        console.error('Exit readiness error:', fetchError)
        setError(fetchError.message)
      } else {
        setDocuments(data || [])
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load documents')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void fetchDocuments()
  }, [accessToken])

  const uploadFile = async (checklistKey: string, file: File) => {
    try {
      setUploadingKey(checklistKey)
      setError(null)

      const { data: { user } } = await supabase.auth.getUser()
      const tenantId = user?.user_metadata?.tenant_id

      if (!tenantId) {
        throw new Error('No tenant_id found')
      }

      const bucket = 'deal-room'
      const timestamp = Date.now()
      const safeName = file.name.replace(/[^a-zA-Z0-9._-]/g, '_')
      const storagePath = `${tenantId}/${checklistKey}/${timestamp}_${safeName}`

      // Upload to Supabase Storage
      const { error: uploadError } = await supabase.storage
        .from(bucket)
        .upload(storagePath, file, {
          cacheControl: '3600',
          upsert: false,
        })

      if (uploadError) {
        throw uploadError
      }

      // Register in database
      const { error: dbError } = await supabase
        .from('exit_readiness_documents')
        .insert({
          tenant_id: tenantId,
          checklist_key: checklistKey,
          storage_bucket: bucket,
          storage_path: storagePath,
          file_name: file.name,
          content_type: file.type,
          size_bytes: file.size,
        })

      if (dbError) {
        throw dbError
      }

      await fetchDocuments()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setUploadingKey(null)
    }
  }

  const deleteDocument = async (doc: UploadedDoc) => {
    try {
      setDeletingId(doc.id)
      setError(null)

      // Delete from storage
      await supabase.storage
        .from(doc.storage_bucket)
        .remove([doc.storage_path])

      // Delete from database
      const { error: dbError } = await supabase
        .from('exit_readiness_documents')
        .delete()
        .eq('id', doc.id)

      if (dbError) {
        throw dbError
      }

      await fetchDocuments()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Delete failed')
    } finally {
      setDeletingId(null)
    }
  }

  const downloadDocument = async (doc: UploadedDoc) => {
    try {
      const { data, error } = await supabase.storage
        .from(doc.storage_bucket)
        .createSignedUrl(doc.storage_path, 3600)

      if (error) throw error
      if (data?.signedUrl) {
        window.open(data.signedUrl, '_blank')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate download link')
    }
  }

  const generateCimOutline = () => {
    const blob = new Blob([CIM_OUTLINE], { type: 'text/markdown;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'CIM_Outline.md'
    a.click()
    URL.revokeObjectURL(url)
  }

  const docsByKey = useMemo(() => {
    const map = new Map<string, UploadedDoc[]>()
    for (const doc of documents) {
      if (!map.has(doc.checklist_key)) map.set(doc.checklist_key, [])
      map.get(doc.checklist_key)!.push(doc)
    }
    return map
  }, [documents])

  const stats = useMemo(() => {
    const total = CHECKLIST_ITEMS.length
    const uploaded = new Set(documents.map(d => d.checklist_key)).size
    const totalDocs = documents.length
    return { total, uploaded, totalDocs, completeness: Math.round((uploaded / total) * 100) }
  }, [documents])

  const readinessStatus = useMemo(() => {
    if (stats.completeness >= 80) return { label: 'Ready', color: 'emerald', bg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' }
    if (stats.completeness >= 50) return { label: 'In Progress', color: 'amber', bg: 'bg-amber-500/10 border-amber-500/30 text-amber-400' }
    return { label: 'Not Ready', color: 'red', bg: 'bg-red-500/10 border-red-500/30 text-red-400' }
  }, [stats.completeness])

  const formatFileSize = (bytes: number | null) => {
    if (!bytes) return 'Unknown size'
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  if (loading) {
    return (
      <GlassCard padding="lg">
        <div className="flex items-center gap-3 text-slate-400">
          <motion.div
            className="w-5 h-5 border-2 border-emerald-500 border-t-transparent rounded-full"
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          />
          Loading exit readiness...
        </div>
      </GlassCard>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        className="flex flex-col sm:flex-row sm:items-center justify-between gap-4"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div>
          <h2 className="text-xl font-semibold">Exit Readiness</h2>
          <p className="text-slate-400 mt-1">Track deal-room completeness and prepare due diligence documents</p>
        </div>
        <motion.button
          onClick={generateCimOutline}
          className="bg-emerald-500 hover:bg-emerald-400 text-black font-semibold px-4 py-2 rounded-lg transition"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          Download CIM Outline
        </motion.button>
      </motion.div>

      {/* Error Banner */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <GlassCard variant="danger" padding="md">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-xl">⚠️</span>
                  <span className="text-red-300">{error}</span>
                </div>
                <button
                  onClick={() => setError(null)}
                  className="text-red-400 hover:text-red-300"
                >
                  ✕
                </button>
              </div>
            </GlassCard>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <GlassCard padding="sm">
          <div className="flex items-center justify-between mb-2">
            <div className="text-sm text-slate-400">Readiness Score</div>
            <div className={`px-2 py-1 rounded text-xs border ${readinessStatus.bg}`}>
              {readinessStatus.label}
            </div>
          </div>
          <div className="text-3xl font-bold text-white">{stats.completeness}%</div>
        </GlassCard>

        <GlassCard padding="sm" variant="success">
          <div className="text-sm text-slate-400">Checklist Items</div>
          <div className="text-3xl font-bold text-emerald-400">
            {stats.uploaded}/{stats.total}
          </div>
        </GlassCard>

        <GlassCard padding="sm" variant="info">
          <div className="text-sm text-slate-400">Documents Uploaded</div>
          <div className="text-3xl font-bold text-blue-400">{stats.totalDocs}</div>
        </GlassCard>

        <ProgressCard
          label="Deal Room Completeness"
          value={stats.completeness}
          color={readinessStatus.color as 'emerald' | 'amber' | 'red'}
          size="sm"
        />
      </div>

      {/* What Buyers Look For */}
      <GlassCard padding="md" variant="info">
        <div className="flex items-start gap-4">
          <span className="text-3xl">💡</span>
          <div>
            <div className="font-semibold text-blue-300">What Buyers Look For</div>
            <div className="text-sm text-blue-200/80 mt-1">
              Complete documentation signals a well-run business and speeds up due diligence.
              Aim for 100% completeness before engaging with potential acquirers.
            </div>
          </div>
        </div>
      </GlassCard>

      {/* Checklist Items */}
      <div className="space-y-3">
        {CHECKLIST_ITEMS.map((item, index) => {
          const itemDocs = docsByKey.get(item.key) || []
          const hasUploads = itemDocs.length > 0
          const isExpanded = expandedKey === item.key
          const isUploading = uploadingKey === item.key

          return (
            <motion.div
              key={item.key}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <GlassCard
                padding="md"
                variant={hasUploads ? 'success' : 'default'}
                glow={hasUploads}
                hover={false}
              >
                <div
                  className="flex items-start justify-between gap-4 cursor-pointer"
                  onClick={() => setExpandedKey(isExpanded ? null : item.key)}
                >
                  <div className="flex items-start gap-4 flex-1">
                    <div className="text-3xl">{item.icon}</div>
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <span className="font-semibold text-white">{item.label}</span>
                        {hasUploads && (
                          <span className="text-emerald-400 text-sm">
                            ✓ {itemDocs.length} file{itemDocs.length !== 1 ? 's' : ''}
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-slate-400 mt-1">{item.description}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    <motion.button
                      onClick={(e) => {
                        e.stopPropagation()
                        fileInputRefs.current[item.key]?.click()
                      }}
                      disabled={isUploading}
                      className={`${
                        hasUploads
                          ? 'bg-slate-700 hover:bg-slate-600 text-white'
                          : 'bg-emerald-500 hover:bg-emerald-400 text-black'
                      } font-medium px-4 py-2 rounded-lg transition text-sm disabled:opacity-50`}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      {isUploading ? (
                        <div className="flex items-center gap-2">
                          <motion.div
                            className="w-4 h-4 border-2 border-current border-t-transparent rounded-full"
                            animate={{ rotate: 360 }}
                            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                          />
                          Uploading...
                        </div>
                      ) : hasUploads ? (
                        'Add More'
                      ) : (
                        'Upload'
                      )}
                    </motion.button>
                    <input
                      ref={(el) => { fileInputRefs.current[item.key] = el }}
                      type="file"
                      multiple
                      className="hidden"
                      onChange={(e) => {
                        const files = e.target.files
                        if (files && files.length > 0) {
                          // Upload first file (can extend to multiple)
                          void uploadFile(item.key, files[0])
                        }
                        e.target.value = ''
                      }}
                    />
                    <motion.div
                      animate={{ rotate: isExpanded ? 180 : 0 }}
                      className="text-slate-400"
                    >
                      ▼
                    </motion.div>
                  </div>
                </div>

                {/* Expanded section with uploaded files */}
                <AnimatePresence>
                  {isExpanded && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="overflow-hidden"
                    >
                      <div className="mt-4 pt-4 border-t border-slate-700/50">
                        {itemDocs.length > 0 ? (
                          <div className="space-y-2">
                            {itemDocs.map((doc) => (
                              <motion.div
                                key={doc.id}
                                className="flex items-center justify-between gap-3 bg-slate-800/50 rounded-lg px-4 py-3"
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                              >
                                <div className="flex items-center gap-3 min-w-0 flex-1">
                                  <span className="text-xl">📄</span>
                                  <div className="min-w-0">
                                    <div className="text-sm text-white truncate">{doc.file_name}</div>
                                    <div className="text-xs text-slate-500">
                                      {formatFileSize(doc.size_bytes)} • {new Date(doc.created_at).toLocaleDateString()}
                                    </div>
                                  </div>
                                </div>
                                <div className="flex items-center gap-2 shrink-0">
                                  <motion.button
                                    onClick={() => void downloadDocument(doc)}
                                    className="bg-slate-700 hover:bg-slate-600 text-white text-sm font-medium px-3 py-1.5 rounded-lg transition"
                                    whileTap={{ scale: 0.95 }}
                                  >
                                    Download
                                  </motion.button>
                                  <motion.button
                                    onClick={() => void deleteDocument(doc)}
                                    disabled={deletingId === doc.id}
                                    className="bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 text-red-400 text-sm font-medium px-3 py-1.5 rounded-lg transition disabled:opacity-50"
                                    whileTap={{ scale: 0.95 }}
                                  >
                                    {deletingId === doc.id ? '...' : 'Delete'}
                                  </motion.button>
                                </div>
                              </motion.div>
                            ))}
                          </div>
                        ) : (
                          <div className="text-center py-4">
                            <div className="text-slate-500 text-sm">No files uploaded yet</div>
                            <button
                              onClick={() => fileInputRefs.current[item.key]?.click()}
                              className="text-emerald-400 hover:text-emerald-300 text-sm mt-2"
                            >
                              Click to upload
                            </button>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </GlassCard>
            </motion.div>
          )
        })}
      </div>

      {/* Footer Info */}
      <GlassCard padding="md" className="text-center">
        <div className="text-sm text-slate-500">
          Files are securely stored in Supabase Storage (bucket: <span className="text-slate-400">deal-room</span>)
          and tracked in <span className="text-slate-400">exit_readiness_documents</span>.
        </div>
      </GlassCard>
    </div>
  )
}
