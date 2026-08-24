import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { FileStack, GitCompare, TrendingUp, ShieldAlert, ArrowRight } from 'lucide-react'
import { dashboardApi } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'

const STAT_CARDS = [
  { key: 'total_submissions', label: 'Total submissions', icon: FileStack },
  { key: 'total_comparisons', label: 'Total comparisons', icon: GitCompare },
  { key: 'average_similarity', label: 'Average similarity', icon: TrendingUp, suffix: '%' },
  { key: 'high_risk_cases', label: 'High-risk cases', icon: ShieldAlert },
]

const RISK_CLASS = {
  Low: 'risk-pill Low',
  Medium: 'risk-pill Medium',
  High: 'risk-pill High',
  'Very High': 'risk-pill VeryHigh',
}

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    dashboardApi
      .summary()
      .then((res) => setSummary(res.data))
      .catch(() => setError('Could not load dashboard data.'))
  }, [])

  if (error) return <div className="max-w-6xl mx-auto px-6 py-10 text-risk-critical">{error}</div>
  if (!summary) return <LoadingSpinner label="Loading dashboard" />

  return (
    <div className="max-w-6xl mx-auto px-6 py-10">
      <div className="flex items-center justify-between mb-8">
        <div>
          <p className="label-eyebrow mb-1">Overview</p>
          <h1 className="font-display text-2xl font-bold text-slate-100">Dashboard</h1>
        </div>
        <Link to="/upload" className="btn-primary">
          Upload code <ArrowRight className="w-4 h-4" />
        </Link>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
        {STAT_CARDS.map(({ key, label, icon: Icon, suffix }) => (
          <div key={key} className="card p-5">
            <Icon className="w-5 h-5 text-cyan-400 mb-3" />
            <div className="font-display text-2xl font-bold text-slate-100">
              {summary[key]}
              {suffix || ''}
            </div>
            <div className="text-xs text-slate-400 mt-1">{label}</div>
          </div>
        ))}
      </div>

      <div className="card p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-slate-100">Recent comparisons</h2>
          <Link to="/history" className="text-sm text-cyan-400 hover:text-cyan-300">View all</Link>
        </div>

        {summary.recent_comparisons.length === 0 ? (
          <div className="text-center py-10">
            <p className="text-sm text-slate-400">No comparisons yet.</p>
            <Link to="/upload" className="text-sm text-cyan-400 hover:text-cyan-300 mt-1 inline-block">
              Upload your first submission →
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-edge">
            {summary.recent_comparisons.map((c) => (
              <Link
                key={c.id}
                to={`/result/${c.id}`}
                className="flex items-center justify-between py-3.5 hover:bg-surface-alt/50 -mx-2 px-2 rounded-lg transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="font-mono text-xs text-slate-500">#{c.id}</span>
                  <span className="text-sm text-slate-300">
                    Submission {c.submission1_id} vs {c.submission2_id}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="font-mono text-sm text-slate-300">{c.final_score.toFixed(1)}%</span>
                  <span className={RISK_CLASS[c.risk_level]}>{c.risk_level}</span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
