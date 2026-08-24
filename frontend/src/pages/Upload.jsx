import { useState, useEffect, useCallback, useRef } from 'react'
import { Link } from 'react-router-dom'
import { UploadCloud, FileCode, Trash2, CheckCircle2, AlertCircle } from 'lucide-react'
import { submissionsApi } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'

export default function Upload() {
  const [submissions, setSubmissions] = useState(null)
  const [dragActive, setDragActive] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState(null) // { type: 'success' | 'error', text }
  const fileInputRef = useRef(null)

  const loadSubmissions = useCallback(() => {
    submissionsApi.list().then((res) => setSubmissions(res.data)).catch(() => setSubmissions([]))
  }, [])

  useEffect(() => {
    loadSubmissions()
  }, [loadSubmissions])

  const handleFiles = async (files) => {
    if (!files || files.length === 0) return
    setUploading(true)
    setMessage(null)
    let successCount = 0
    let lastError = ''
    for (const file of files) {
      try {
        await submissionsApi.upload(file)
        successCount += 1
      } catch (err) {
        lastError = err.response?.data?.detail || `Failed to upload ${file.name}.`
      }
    }
    setUploading(false)
    loadSubmissions()
    if (lastError) {
      setMessage({ type: 'error', text: lastError })
    } else {
      setMessage({ type: 'success', text: `${successCount} file(s) uploaded successfully.` })
    }
  }

  const onDrop = (e) => {
    e.preventDefault()
    setDragActive(false)
    handleFiles(e.dataTransfer.files)
  }

  const handleDelete = async (id) => {
    await submissionsApi.delete(id)
    loadSubmissions()
  }

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <p className="label-eyebrow mb-1">Submissions</p>
      <h1 className="font-display text-2xl font-bold text-slate-100 mb-8">Upload source code</h1>

      <div
        onDragOver={(e) => { e.preventDefault(); setDragActive(true) }}
        onDragLeave={() => setDragActive(false)}
        onDrop={onDrop}
        className={`card border-dashed p-10 text-center transition-colors ${
          dragActive ? 'border-cyan-400 bg-cyan-400/5' : ''
        }`}
      >
        <UploadCloud className="w-9 h-9 text-cyan-400 mx-auto mb-3" />
        <p className="text-slate-200 font-medium">Drag and drop files here</p>
        <p className="text-sm text-slate-500 mt-1">or click below to browse — Python (.py) files, up to 2 MB each</p>
        <button
          className="btn-primary mt-5"
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
        >
          {uploading ? 'Uploading…' : 'Browse files'}
        </button>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".py"
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
      </div>

      {message && (
        <div
          className={`flex items-start gap-2 text-sm rounded-lg px-3 py-2.5 mt-4 border ${
            message.type === 'success'
              ? 'bg-risk-low/10 border-risk-low/30 text-risk-low'
              : 'bg-risk-critical/10 border-risk-critical/30 text-risk-critical'
          }`}
        >
          {message.type === 'success' ? (
            <CheckCircle2 className="w-4 h-4 mt-0.5 shrink-0" />
          ) : (
            <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
          )}
          <span>{message.text}</span>
        </div>
      )}

      <div className="mt-10">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-slate-100">Your submissions</h2>
          {submissions && submissions.length >= 2 && (
            <Link to="/compare" className="text-sm text-cyan-400 hover:text-cyan-300">
              Compare two submissions →
            </Link>
          )}
        </div>

        {submissions === null ? (
          <LoadingSpinner label="Loading submissions" />
        ) : submissions.length === 0 ? (
          <p className="text-sm text-slate-500 text-center py-8">No submissions yet. Upload a file to get started.</p>
        ) : (
          <div className="card divide-y divide-edge">
            {submissions.map((s) => (
              <div key={s.id} className="flex items-center justify-between px-5 py-3.5">
                <div className="flex items-center gap-3 min-w-0">
                  <FileCode className="w-4 h-4 text-cyan-400 shrink-0" />
                  <div className="min-w-0">
                    <p className="text-sm text-slate-200 truncate">{s.filename}</p>
                    <p className="text-xs text-slate-500 font-mono">
                      {s.language} · {(s.file_size / 1024).toFixed(1)} KB · {new Date(s.uploaded_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(s.id)}
                  className="text-slate-500 hover:text-risk-critical transition-colors p-1.5"
                  title="Delete submission"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
