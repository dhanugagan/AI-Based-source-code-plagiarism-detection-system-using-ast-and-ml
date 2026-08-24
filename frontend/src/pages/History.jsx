import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { History as HistoryIcon } from 'lucide-react'
import { comparisonsApi } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'

const RISK_CLASS = {
  Low: 'risk-pill Low',
  Medium: 'risk-pill Medium',
  High: 'risk-pill High',
  'Very High': 'risk-pill VeryHigh',
}

export default function History() {
  const [comparisons, setComparisons] = useState(null)

  useEffect(() => {
    comparisonsApi.list().then((res) => setComparisons(res.data)).catch(() => setComparisons([]))
  }, [])

  if (comparisons === null) return <LoadingSpinner label="Loading history" />

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <p className="label-eyebrow mb-1">Records</p>
      <h1 className="font-display text-2xl font-bold text-slate-100 mb-8">Comparison history</h1>

      {comparisons.length === 0 ? (
        <div className="card p-12 text-center">
          <HistoryIcon className="w-8 h-8 text-slate-600 mx-auto mb-3" />
          <p className="text-sm text-slate-400">No comparisons yet.</p>
        </div>
      ) : (
        <div className="card divide-y divide-edge">
          <div className="grid grid-cols-[60px_1fr_100px_140px] gap-4 px-5 py-3 text-xs text-slate-500 font-mono uppercase tracking-wide">
            <span>ID</span>
            <span>Submissions</span>
            <span>Score</span>
            <span>Risk / Date</span>
          </div>
          {comparisons.map((c) => (
            <Link
              key={c.id}
              to={`/result/${c.id}`}
              className="grid grid-cols-[60px_1fr_100px_140px] gap-4 px-5 py-4 items-center hover:bg-surface-alt/50 transition-colors"
            >
              <span className="font-mono text-sm text-slate-500">#{c.id}</span>
              <span className="text-sm text-slate-300">
                {c.submission1_id} vs {c.submission2_id}
              </span>
              <span className="font-mono text-sm text-slate-200">{c.final_score.toFixed(1)}%</span>
              <div className="flex flex-col items-start gap-1">
                <span className={RISK_CLASS[c.risk_level]}>{c.risk_level}</span>
                <span className="text-[11px] text-slate-500 font-mono">
                  {new Date(c.created_at).toLocaleDateString()}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
