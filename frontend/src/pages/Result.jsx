import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import Editor from '@monaco-editor/react'
import { Download, ArrowLeft, Info } from 'lucide-react'
import { comparisonsApi, reportsApi } from '../services/api'
import SimilarityGauge from '../components/SimilarityGauge'
import LoadingSpinner from '../components/LoadingSpinner'

const BREAKDOWN_ROWS = [
  { key: 'ast_similarity', label: 'AST Similarity' },
  { key: 'token_similarity', label: 'Token Similarity' },
  { key: 'structural_similarity', label: 'Structural Similarity' },
  { key: 'ml_score', label: 'ML Score' },
]

export default function Result() {
  const { id } = useParams()
  const [comparison, setComparison] = useState(null)
  const [error, setError] = useState('')
  const [generatingReport, setGeneratingReport] = useState(false)

  useEffect(() => {
    comparisonsApi
      .get(id)
      .then((res) => setComparison(res.data))
      .catch(() => setError('Could not load this comparison.'))
  }, [id])

  const handleDownloadReport = async () => {
    setGeneratingReport(true)
    try {
      const gen = await reportsApi.generate(id)
      const reportId = gen.data.report_id
      const file = await reportsApi.download(reportId)
      const url = window.URL.createObjectURL(new Blob([file.data], { type: 'application/pdf' }))
      const a = document.createElement('a')
      a.href = url
      a.download = `plagiarism-report-${id}.pdf`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch {
      setError('Could not generate report.')
    } finally {
      setGeneratingReport(false)
    }
  }

  if (error) return <div className="max-w-5xl mx-auto px-6 py-10 text-risk-critical">{error}</div>
  if (!comparison) return <LoadingSpinner label="Loading result" />

  return (
    <div className="max-w-6xl mx-auto px-6 py-10">
      <Link to="/history" className="inline-flex items-center gap-1.5 text-sm text-slate-400 hover:text-slate-200 mb-6">
        <ArrowLeft className="w-4 h-4" /> Back to history
      </Link>

      <div className="grid lg:grid-cols-[280px_1fr] gap-8 mb-10">
        <div className="card p-6 flex flex-col items-center justify-center">
          <SimilarityGauge score={comparison.final_score} riskLevel={comparison.risk_level} />
          <p className="text-xs text-slate-500 mt-4 text-center">Final Plagiarism Score</p>
        </div>

        <div>
          <p className="label-eyebrow mb-1">Comparison #{comparison.id}</p>
          <h1 className="font-display text-2xl font-bold text-slate-100 mb-6">Similarity breakdown</h1>

          <div className="space-y-4">
            {BREAKDOWN_ROWS.map(({ key, label }) => (
              <div key={key}>
                <div className="flex items-center justify-between text-sm mb-1.5">
                  <span className="text-slate-300">{label}</span>
                  <span className="font-mono text-slate-400">{comparison[key].toFixed(1)}%</span>
                </div>
                <div className="h-2 rounded-full bg-surface-alt overflow-hidden">
                  <div
                    className="h-full rounded-full bg-cyan-400"
                    style={{ width: `${Math.min(100, comparison[key])}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          <button onClick={handleDownloadReport} disabled={generatingReport} className="btn-primary mt-8">
            <Download className="w-4 h-4" />
            {generatingReport ? 'Generating report…' : 'Download PDF report'}
          </button>
        </div>
      </div>

      {comparison.explanation?.length > 0 && (
        <div className="card p-6 mb-8">
          <div className="flex items-center gap-2 mb-4">
            <Info className="w-4 h-4 text-cyan-400" />
            <h2 className="font-semibold text-slate-100">Detected similar structures</h2>
          </div>
          <ul className="space-y-2">
            {comparison.explanation.map((point, i) => (
              <li key={i} className="text-sm text-slate-400 flex gap-2">
                <span className="text-cyan-400 mt-0.5">•</span>
                <span>{point}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div>
        <h2 className="font-semibold text-slate-100 mb-4">Source comparison</h2>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="card overflow-hidden">
            <div className="px-4 py-2.5 border-b border-edge text-xs font-mono text-slate-500">Submission A</div>
            <Editor
              height="420px"
              defaultLanguage="python"
              theme="vs-dark"
              value={comparison.code_a}
              options={{ readOnly: true, minimap: { enabled: false }, fontSize: 13 }}
            />
          </div>
          <div className="card overflow-hidden">
            <div className="px-4 py-2.5 border-b border-edge text-xs font-mono text-slate-500">Submission B</div>
            <Editor
              height="420px"
              defaultLanguage="python"
              theme="vs-dark"
              value={comparison.code_b}
              options={{ readOnly: true, minimap: { enabled: false }, fontSize: 13 }}
            />
          </div>
        </div>
      </div>

      <p className="text-xs text-slate-500 mt-8 font-mono">
        Note: this score indicates structural similarity. It is an indicator to support human review,
        not definitive proof of academic misconduct.
      </p>
    </div>
  )
}
