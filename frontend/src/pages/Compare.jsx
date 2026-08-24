import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Editor from '@monaco-editor/react'
import { GitCompare, AlertCircle } from 'lucide-react'
import { submissionsApi, comparisonsApi } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'

export default function Compare() {
  const navigate = useNavigate()
  const [submissions, setSubmissions] = useState(null)
  const [idA, setIdA] = useState('')
  const [idB, setIdB] = useState('')
  const [codeA, setCodeA] = useState('')
  const [codeB, setCodeB] = useState('')
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    submissionsApi.list().then((res) => setSubmissions(res.data)).catch(() => setSubmissions([]))
  }, [])

  useEffect(() => {
    if (idA) submissionsApi.get(idA).then(() => {})
  }, [idA])

  const loadPreview = async (id, setter) => {
    if (!id) {
      setter('')
      return
    }
    try {
      const res = await submissionsApi.source(id)
      setter(res.data.source)
    } catch {
      setter('# Could not load preview.')
    }
  }

  useEffect(() => {
    if (idA) loadPreview(idA, setCodeA)
  }, [idA])
  useEffect(() => {
    if (idB) loadPreview(idB, setCodeB)
  }, [idB])

  const handleAnalyze = async () => {
    if (!idA || !idB) {
      setError('Select two submissions to compare.')
      return
    }
    if (idA === idB) {
      setError('Select two different submissions.')
      return
    }
    setError('')
    setAnalyzing(true)
    try {
      const res = await comparisonsApi.analyze(Number(idA), Number(idB))
      navigate(`/result/${res.data.id}`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis failed.')
    } finally {
      setAnalyzing(false)
    }
  }

  if (submissions === null) return <LoadingSpinner label="Loading submissions" />

  if (submissions.length < 2) {
    return (
      <div className="max-w-2xl mx-auto px-6 py-16 text-center">
        <GitCompare className="w-9 h-9 text-cyan-400 mx-auto mb-3" />
        <h1 className="font-display text-xl font-bold text-slate-100 mb-2">Not enough submissions</h1>
        <p className="text-sm text-slate-400">Upload at least two source files before running a comparison.</p>
      </div>
    )
  }

  const selectedA = submissions.find((s) => String(s.id) === String(idA))
  const selectedB = submissions.find((s) => String(s.id) === String(idB))

  return (
    <div className="max-w-6xl mx-auto px-6 py-10">
      <p className="label-eyebrow mb-1">Analysis</p>
      <h1 className="font-display text-2xl font-bold text-slate-100 mb-8">Compare submissions</h1>

      <div className="grid md:grid-cols-2 gap-4 mb-4">
        <div>
          <label className="text-xs font-medium text-slate-400 mb-1.5 block">Source A</label>
          <select className="input-field" value={idA} onChange={(e) => setIdA(e.target.value)}>
            <option value="">Select a submission…</option>
            {submissions.map((s) => (
              <option key={s.id} value={s.id}>{s.filename} (#{s.id})</option>
            ))}
          </select>
        </div>
        <div>
          <label className="text-xs font-medium text-slate-400 mb-1.5 block">Source B</label>
          <select className="input-field" value={idB} onChange={(e) => setIdB(e.target.value)}>
            <option value="">Select a submission…</option>
            {submissions.map((s) => (
              <option key={s.id} value={s.id}>{s.filename} (#{s.id})</option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-4 mb-6">
        <div className="card overflow-hidden">
          <div className="px-4 py-2.5 border-b border-edge text-xs font-mono text-slate-500">
            {selectedA ? selectedA.filename : 'source_a.py'}
          </div>
          <Editor
            height="360px"
            defaultLanguage="python"
            theme="vs-dark"
            value={codeA || '# Select Source A'}
            options={{ readOnly: true, minimap: { enabled: false }, fontSize: 13 }}
          />
        </div>
        <div className="card overflow-hidden">
          <div className="px-4 py-2.5 border-b border-edge text-xs font-mono text-slate-500">
            {selectedB ? selectedB.filename : 'source_b.py'}
          </div>
          <Editor
            height="360px"
            defaultLanguage="python"
            theme="vs-dark"
            value={codeB || '# Select Source B'}
            options={{ readOnly: true, minimap: { enabled: false }, fontSize: 13 }}
          />
        </div>
      </div>

      {error && (
        <div className="flex items-start gap-2 bg-risk-critical/10 border border-risk-critical/30 text-risk-critical text-sm rounded-lg px-3 py-2.5 mb-4">
          <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <button onClick={handleAnalyze} disabled={analyzing} className="btn-primary">
        {analyzing ? (
          <>
            <span className="w-3.5 h-3.5 border-2 border-ink border-t-transparent rounded-full animate-spin" />
            Analyzing…
          </>
        ) : (
          <>
            <GitCompare className="w-4 h-4" />
            Analyze Plagiarism
          </>
        )}
      </button>
    </div>
  )
}
