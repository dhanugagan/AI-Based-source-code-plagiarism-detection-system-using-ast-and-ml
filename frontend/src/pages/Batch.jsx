import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Grid3x3, AlertCircle, ShieldAlert } from 'lucide-react'
import { submissionsApi, comparisonsApi } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'

function cellColor(score) {
  if (score === 0) return 'bg-surface-alt text-slate-600'
  if (score <= 30) return 'bg-risk-low/15 text-risk-low'
  if (score <= 60) return 'bg-risk-medium/15 text-risk-medium'
  if (score <= 80) return 'bg-risk-high/15 text-risk-high'
  return 'bg-risk-critical/15 text-risk-critical'
}

const RISK_CLASS = {
  Low: 'risk-pill Low',
  Medium: 'risk-pill Medium',
  High: 'risk-pill High',
  'Very High': 'risk-pill VeryHigh',
}

export default function Batch() {
  const [submissions, setSubmissions] = useState(null)
  const [selected, setSelected] = useState([])
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [running, setRunning] = useState(false)

  useEffect(() => {
    submissionsApi.list().then((res) => setSubmissions(res.data)).catch(() => setSubmissions([]))
  }, [])

  const toggle = (id) => {
    setSelected((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]))
  }

  const runBatch = async () => {
    if (selected.length < 3) {
      setError('Select at least 3 submissions to build a plagiarism matrix.')
      return
    }
    setError('')
    setRunning(true)
    setResult(null)
    try {
      const res = await comparisonsApi.batch(selected)
      setResult(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Batch analysis failed.')
    } finally {
      setRunning(false)
    }
  }

  if (submissions === null) return <LoadingSpinner label="Loading submissions" />

  return (
    <div className="max-w-6xl mx-auto px-6 py-10">
      <p className="label-eyebrow mb-1">Assignment mode</p>
      <h1 className="font-display text-2xl font-bold text-slate-100 mb-2">Batch comparison</h1>
      <p className="text-sm text-slate-400 mb-8 max-w-2xl">
        Select three or more submissions — e.g. an entire assignment's worth — to automatically
        generate a full pairwise plagiarism matrix, the same way a teacher would compare every
        student's submission against every other one.
      </p>

      {submissions.length < 3 ? (
        <div className="card p-12 text-center">
          <Grid3x3 className="w-8 h-8 text-slate-600 mx-auto mb-3" />
          <p className="text-sm text-slate-400">Upload at least 3 submissions to use batch mode.</p>
          <Link to="/upload" className="text-sm text-cyan-400 hover:text-cyan-300 mt-1 inline-block">
            Go to Upload →
          </Link>
        </div>
      ) : (
        <>
          <div className="card p-5 mb-6">
            <p className="text-xs font-medium text-slate-400 mb-3">
              Select submissions ({selected.length} selected)
            </p>
            <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-2">
              {submissions.map((s) => (
                <label
                  key={s.id}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg border cursor-pointer text-sm transition-colors ${
                    selected.includes(s.id)
                      ? 'border-cyan-400/60 bg-cyan-400/5 text-slate-100'
                      : 'border-edge text-slate-400 hover:border-edge/80'
                  }`}
                >
                  <input
                    type="checkbox"
                    className="accent-cyan-400"
                    checked={selected.includes(s.id)}
                    onChange={() => toggle(s.id)}
                  />
                  <span className="truncate font-mono text-xs">{s.filename}</span>
                </label>
              ))}
            </div>
          </div>

          {error && (
            <div className="flex items-start gap-2 bg-risk-critical/10 border border-risk-critical/30 text-risk-critical text-sm rounded-lg px-3 py-2.5 mb-4">
              <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <button onClick={runBatch} disabled={running} className="btn-primary mb-10">
            {running ? (
              <>
                <span className="w-3.5 h-3.5 border-2 border-ink border-t-transparent rounded-full animate-spin" />
                Running batch analysis…
              </>
            ) : (
              <>
                <Grid3x3 className="w-4 h-4" />
                Generate plagiarism matrix
              </>
            )}
          </button>
        </>
      )}

      {result && (
        <>
          <h2 className="font-semibold text-slate-100 mb-4">Similarity matrix</h2>
          <div className="card p-5 overflow-x-auto mb-8">
            <table className="border-collapse font-mono text-xs">
              <thead>
                <tr>
                  <th className="p-2 text-left text-slate-500"></th>
                  {result.filenames.map((f, i) => (
                    <th key={i} className="p-2 text-slate-400 font-medium whitespace-nowrap max-w-[100px] truncate">
                      S{i + 1}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {result.matrix.map((row, i) => (
                  <tr key={i}>
                    <td className="p-2 text-slate-400 font-medium whitespace-nowrap">
                      S{i + 1} <span className="text-slate-600">· {result.filenames[i]}</span>
                    </td>
                    {row.map((val, j) => (
                      <td key={j} className="p-1">
                        <div className={`w-14 h-10 flex items-center justify-center rounded-md font-semibold ${cellColor(val)}`}>
                          {i === j ? '—' : `${val.toFixed(0)}%`}
                        </div>
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex items-center gap-2 mb-4">
            <ShieldAlert className="w-4 h-4 text-cyan-400" />
            <h2 className="font-semibold text-slate-100">High-risk pairs</h2>
          </div>
          {result.high_risk_pairs.length === 0 ? (
            <p className="text-sm text-slate-400">No high-risk pairs detected in this batch.</p>
          ) : (
            <div className="card divide-y divide-edge">
              {result.high_risk_pairs.map((p, i) => (
                <div key={i} className="flex items-center justify-between px-5 py-3.5">
                  <span className="text-sm text-slate-300 font-mono">
                    {p.filename1} <span className="text-slate-600">vs</span> {p.filename2}
                  </span>
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-sm text-slate-200">{p.final_score.toFixed(1)}%</span>
                    <span className={RISK_CLASS[p.risk_level]}>{p.risk_level}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}
