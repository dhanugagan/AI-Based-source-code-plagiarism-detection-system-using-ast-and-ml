import { useEffect, useState } from 'react'
import { Users, FileStack, GitCompare, ShieldAlert, TrendingUp } from 'lucide-react'
import { adminApi } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'

const RISK_CLASS = {
  Low: 'risk-pill Low',
  Medium: 'risk-pill Medium',
  High: 'risk-pill High',
  'Very High': 'risk-pill VeryHigh',
}

export default function AdminDashboard() {
  const [stats, setStats] = useState(null)
  const [highRisk, setHighRisk] = useState(null)
  const [users, setUsers] = useState(null)
  const [tab, setTab] = useState('overview')

  useEffect(() => {
    adminApi.statistics().then((res) => setStats(res.data))
    adminApi.highRisk().then((res) => setHighRisk(res.data))
    adminApi.users().then((res) => setUsers(res.data))
  }, [])

  if (!stats) return <LoadingSpinner label="Loading admin data" />

  const cards = [
    { label: 'Total users', value: stats.total_users, icon: Users },
    { label: 'Total submissions', value: stats.total_submissions, icon: FileStack },
    { label: 'Total comparisons', value: stats.total_comparisons, icon: GitCompare },
    { label: 'Avg. similarity', value: `${stats.average_similarity}%`, icon: TrendingUp },
    { label: 'High-risk cases', value: stats.high_risk_cases, icon: ShieldAlert },
  ]

  return (
    <div className="max-w-6xl mx-auto px-6 py-10">
      <p className="label-eyebrow mb-1">Administration</p>
      <h1 className="font-display text-2xl font-bold text-slate-100 mb-8">Admin dashboard</h1>

      <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-4 mb-10">
        {cards.map(({ label, value, icon: Icon }) => (
          <div key={label} className="card p-5">
            <Icon className="w-5 h-5 text-cyan-400 mb-3" />
            <div className="font-display text-2xl font-bold text-slate-100">{value}</div>
            <div className="text-xs text-slate-400 mt-1">{label}</div>
          </div>
        ))}
      </div>

      <div className="flex gap-1 mb-6 border-b border-edge">
        {[
          { key: 'overview', label: 'High-risk cases' },
          { key: 'users', label: 'Users' },
        ].map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-4 py-2.5 text-sm font-medium border-b-2 -mb-px transition-colors ${
              tab === t.key ? 'border-cyan-400 text-cyan-300' : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'overview' && (
        <div className="card divide-y divide-edge">
          {highRisk === null ? (
            <LoadingSpinner label="Loading" />
          ) : highRisk.length === 0 ? (
            <p className="text-sm text-slate-400 text-center py-10">No high-risk cases detected.</p>
          ) : (
            highRisk.map((c) => (
              <div key={c.id} className="flex items-center justify-between px-5 py-3.5">
                <div className="flex items-center gap-3">
                  <span className="font-mono text-xs text-slate-500">#{c.id}</span>
                  <span className="text-sm text-slate-300">Submissions {c.submission1_id} vs {c.submission2_id}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="font-mono text-sm text-slate-200">{c.final_score.toFixed(1)}%</span>
                  <span className={RISK_CLASS[c.risk_level]}>{c.risk_level}</span>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {tab === 'users' && (
        <div className="card divide-y divide-edge">
          {users === null ? (
            <LoadingSpinner label="Loading" />
          ) : (
            users.map((u) => (
              <div key={u.id} className="flex items-center justify-between px-5 py-3.5">
                <div>
                  <p className="text-sm text-slate-200">{u.name}</p>
                  <p className="text-xs text-slate-500 font-mono">{u.email}</p>
                </div>
                <span className="text-xs font-mono px-2.5 py-1 rounded-full border border-edge text-slate-400 capitalize">
                  {u.role}
                </span>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  )
}
