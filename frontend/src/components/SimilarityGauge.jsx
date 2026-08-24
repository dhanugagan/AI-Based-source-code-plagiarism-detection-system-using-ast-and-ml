const RISK_COLOR = {
  Low: '#34d399',
  Medium: '#facc15',
  High: '#f59e0b',
  'Very High': '#f43f5e',
}

export default function SimilarityGauge({ score = 0, riskLevel = 'Low', size = 200 }) {
  const radius = (size - 24) / 2
  const circumference = 2 * Math.PI * radius
  const clamped = Math.max(0, Math.min(100, score))
  const offset = circumference - (clamped / 100) * circumference
  const color = RISK_COLOR[riskLevel] || '#22d3ee'

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#262f3d"
          strokeWidth={14}
          fill="none"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={14}
          fill="none"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: 'stroke-dashoffset 0.8s ease, stroke 0.4s ease' }}
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="font-display text-4xl font-bold text-slate-100">{clamped.toFixed(0)}%</span>
        <span
          className="font-mono text-xs font-semibold uppercase tracking-wider mt-1"
          style={{ color }}
        >
          {riskLevel}
        </span>
      </div>
    </div>
  )
}
