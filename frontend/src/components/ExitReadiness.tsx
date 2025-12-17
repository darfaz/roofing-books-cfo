import { useEffect, useMemo, useState } from 'react'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

type ExitReadinessItem = {
  key: string
  label: string
  uploaded: boolean
}

type ExitReadinessResponse = {
  readiness_score: number
  status: 'green' | 'yellow' | 'red'
  completeness_pct: number
  checklist: ExitReadinessItem[]
  files_by_key?: Record<
    string,
    {
      id: string
      file_name: string
      content_type?: string | null
      size_bytes?: number | null
      created_at?: string | null
      signed_url?: string | null
      storage_bucket?: string | null
      storage_path?: string | null
    }[]
  >
}

const STATUS_STYLES: Record<ExitReadinessResponse['status'], string> = {
  green: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
  yellow: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
  red: 'text-red-400 bg-red-500/10 border-red-500/30',
}

export function ExitReadiness({ accessToken }: { accessToken: string }) {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [data, setData] = useState<ExitReadinessResponse | null>(null)

  const [uploads, setUploads] = useState<Record<string, File[]>>({})
  const [uploadingKey, setUploadingKey] = useState<string | null>(null)

  const authHeaders = useMemo(
    () => ({
      Authorization: `Bearer ${accessToken}`,
    }),
    [accessToken],
  )

  const fetchExitReadiness = async () => {
    const res = await fetch(`${API_BASE_URL}/api/valuation/exit-readiness`, { headers: authHeaders })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const json = (await res.json()) as ExitReadinessResponse
    setData(json)
  }

  useEffect(() => {
    void (async () => {
      try {
        setLoading(true)
        setError(null)
        await fetchExitReadiness()
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Failed to load exit readiness')
        setData(null)
      } finally {
        setLoading(false)
      }
    })()
  }, [authHeaders])

  const statusLabel = (s: ExitReadinessResponse['status']) => (s === 'green' ? 'Ready' : s === 'yellow' ? 'In Progress' : 'Not Ready')

  const uploadFiles = async (key: string, files: File[]) => {
    const form = new FormData()
    form.append('checklist_key', key)
    files.forEach((f) => form.append('files', f))

    const res = await fetch(`${API_BASE_URL}/api/valuation/exit-readiness/upload`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
      body: form,
    })
    if (!res.ok) {
      const text = await res.text()
      throw new Error(text || `HTTP ${res.status}`)
    }
  }

  const deleteDoc = async (docId: string) => {
    const res = await fetch(`${API_BASE_URL}/api/valuation/exit-readiness/files/${docId}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${accessToken}` },
    })
    if (!res.ok) {
      const text = await res.text()
      throw new Error(text || `HTTP ${res.status}`)
    }
  }

  const onFiles = (key: string, files: FileList | null) => {
    if (!files) return
    const list = Array.from(files)
    setUploads((prev) => ({ ...prev, [key]: list }))
    void (async () => {
      try {
        setUploadingKey(key)
        setError(null)
        await uploadFiles(key, list)
        await fetchExitReadiness()
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Upload failed')
      } finally {
        setUploadingKey(null)
      }
    })()
  }

  const completenessPct = (() => {
    const base = data?.completeness_pct ?? 0
    // Local-only: if user selects files, count them as uploaded for the meter immediately
    if (!data?.checklist?.length) return base
    const total = data.checklist.length
    const uploaded = data.checklist.reduce((acc, item) => {
      const local = uploads[item.key]?.length ? 1 : 0
      return acc + (item.uploaded ? 1 : local)
    }, 0)
    return Math.round((uploaded / total) * 100)
  })()

  const generateCimOutline = () => {
    const outline = [
      '1. Executive Summary',
      '2. Company Overview',
      '3. Services & Markets',
      '4. Operations & Crew Structure',
      '5. Financial Overview (3–5 years)',
      '6. KPI Dashboard & Unit Economics',
      '7. Customers & Backlog',
      '8. Assets & Equipment',
      '9. Safety, Insurance & Compliance',
      '10. Organization & Key Personnel',
      '11. Growth Opportunities',
      '12. Transaction Considerations',
      '',
      'Appendix: Due Diligence Documents',
    ].join('\n')

    const blob = new Blob([outline], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'CIM_Outline.txt'
    a.click()
    URL.revokeObjectURL(url)
  }

  if (loading) {
    return (
      <div className="bg-slate-900 rounded-xl p-8 border border-slate-800">
        <div className="text-slate-400">Loading exit readiness…</div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="bg-slate-900 rounded-xl p-8 border border-slate-800">
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-red-300 text-sm">
          {error || 'Exit readiness unavailable'}
        </div>
      </div>
    )
  }

  return (
    <div className="bg-slate-900 rounded-xl p-8 border border-slate-800">
      <div className="flex items-start justify-between gap-4 mb-6">
        <div>
          <h2 className="text-xl font-semibold">Exit Readiness</h2>
          <p className="text-slate-400 mt-1">Track deal-room completeness and prepare diligence documents for an exit process.</p>
        </div>
        <button
          onClick={generateCimOutline}
          className="bg-emerald-500 hover:bg-emerald-400 text-black font-semibold px-4 py-2 rounded-lg transition"
        >
          Generate CIM Outline
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Readiness score card */}
        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700/60">
          <div className="flex items-center justify-between mb-4">
            <div className="font-semibold">Readiness Score</div>
            <div className={`px-3 py-1 rounded-lg border text-xs ${STATUS_STYLES[data.status]}`}>{statusLabel(data.status)}</div>
          </div>
          <div className="text-5xl font-bold tabular-nums">{data.readiness_score}</div>
          <div className="text-sm text-slate-400 mt-2">0–100 based on due diligence completeness.</div>
          <div className="mt-5 pt-5 border-t border-slate-700/60">
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm text-slate-400">Deal Room Completeness</div>
              <div className="font-semibold tabular-nums">{completenessPct}%</div>
            </div>
            <div className="w-full bg-slate-900 rounded-full h-2">
              <div className="h-2 rounded-full bg-emerald-500/20" style={{ width: `${completenessPct}%` }} />
            </div>
          </div>
        </div>

        {/* Checklist + upload */}
        <div className="lg:col-span-2 bg-slate-800 rounded-lg p-6 border border-slate-700/60">
          <div className="font-semibold mb-4">Due Diligence Checklist</div>
          {error && (
            <div className="mb-4 bg-red-500/10 border border-red-500/30 rounded-lg p-3 text-red-300 text-sm">{error}</div>
          )}
          <div className="space-y-3">
            {data.checklist.map((item) => {
              const localSelected = uploads[item.key]?.length ? true : false
              const checked = item.uploaded || localSelected
              const files = data.files_by_key?.[item.key] || []
              return (
                <div key={item.key} className="bg-slate-900 rounded-lg p-4 border border-slate-800">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <div className="font-medium">{item.label}</div>
                      <div className="text-xs text-slate-500 mt-1">
                        {uploadingKey === item.key ? 'Uploading…' : checked ? '✓ Uploaded' : '✗ Missing'}
                      </div>
                    </div>
                    <div className="text-lg">{checked ? '✓' : '✗'}</div>
                  </div>

                  <div className="mt-4">
                    <label className="block text-xs text-slate-400 mb-2">Upload documents</label>
                    <input
                      type="file"
                      multiple
                      onChange={(e) => onFiles(item.key, e.target.files)}
                      disabled={uploadingKey === item.key}
                      className="block w-full text-sm text-slate-300 file:mr-4 file:py-2 file:px-3 file:rounded-lg file:border-0 file:bg-slate-800 file:text-slate-100 hover:file:bg-slate-700"
                    />
                    {!!uploads[item.key]?.length && (
                      <div className="mt-2 text-xs text-slate-500">
                        Selected: {uploads[item.key].map((f) => f.name).join(', ')}
                      </div>
                    )}
                  </div>

                  {/* Uploaded files */}
                  <div className="mt-4 pt-4 border-t border-slate-800">
                    <div className="text-xs text-slate-400 mb-2">Uploaded files</div>
                    {files.length ? (
                      <div className="space-y-2">
                        {files.map((f) => (
                          <div key={f.id} className="flex items-center justify-between gap-3 bg-slate-950/40 border border-slate-800 rounded-lg px-3 py-2">
                            <div className="min-w-0">
                              <div className="text-sm text-slate-200 truncate">{f.file_name}</div>
                              <div className="text-[11px] text-slate-500">
                                {f.created_at ? new Date(f.created_at).toLocaleString() : ''}
                              </div>
                            </div>
                            <div className="flex items-center gap-2 shrink-0">
                              {f.signed_url ? (
                                <a
                                  href={f.signed_url}
                                  target="_blank"
                                  rel="noreferrer"
                                  className="bg-slate-800 hover:bg-slate-700 text-white text-sm font-medium px-3 py-1.5 rounded-lg transition"
                                >
                                  Download
                                </a>
                              ) : (
                                <span className="text-xs text-slate-500">Link unavailable</span>
                              )}
                              <button
                                onClick={() => {
                                  void (async () => {
                                    try {
                                      setError(null)
                                      await deleteDoc(f.id)
                                      await fetchExitReadiness()
                                    } catch (e) {
                                      setError(e instanceof Error ? e.message : 'Delete failed')
                                    }
                                  })()
                                }}
                                className="bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 text-red-300 text-sm font-medium px-3 py-1.5 rounded-lg transition"
                              >
                                Delete
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-xs text-slate-500">No files yet.</div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>

          <div className="mt-5 pt-5 border-t border-slate-700/60 text-xs text-slate-500">
            Files are uploaded to Supabase Storage bucket <span className="text-slate-300">deal-room</span> and registered in
            <span className="text-slate-300"> exit_readiness_documents</span>.
          </div>
        </div>
      </div>
    </div>
  )
}


