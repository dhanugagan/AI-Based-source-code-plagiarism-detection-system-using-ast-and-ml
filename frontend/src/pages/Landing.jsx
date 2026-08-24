import { Link } from 'react-router-dom'
import { ShieldCheck, GitCompare, Cpu, FileBarChart, ArrowRight } from 'lucide-react'
import ASTHeroVisual from '../components/ASTHeroVisual'

const FEATURES = [
  {
    icon: GitCompare,
    title: 'Structural comparison, not text diffing',
    desc: 'Programs are parsed into Abstract Syntax Trees and normalized, so renamed variables, reformatted whitespace, and reworded comments do not hide similarity.',
  },
  {
    icon: Cpu,
    title: 'ML-assisted risk scoring',
    desc: 'A Random Forest model trained on labeled code-pair examples adds a learned similarity signal on top of AST, token, and structural feature comparisons.',
  },
  {
    icon: FileBarChart,
    title: 'Explainable reports',
    desc: 'Every score comes with the structural evidence behind it — exportable as a professional PDF report for review, not a black-box number.',
  },
]

const STEPS = [
  { n: '01', title: 'Upload', desc: 'Submit two or more source files for analysis.' },
  { n: '02', title: 'Parse & normalize', desc: 'Each file is parsed into an AST and normalized to strip superficial differences.' },
  { n: '03', title: 'Compare', desc: 'AST, token, structural, and ML similarity scores are computed and combined.' },
  { n: '04', title: 'Review', desc: 'Inspect the breakdown, risk level, and detected structures — or export a report.' },
]

export default function Landing() {
  return (
    <div className="min-h-screen">
      <header className="border-b border-edge">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 font-display font-bold text-slate-100">
            <ShieldCheck className="w-5 h-5 text-cyan-400" />
            <span>CodeGuard</span>
          </div>
          <div className="flex items-center gap-3">
            <Link to="/login" className="btn-secondary">Log in</Link>
            <Link to="/register" className="btn-primary">Get started</Link>
          </div>
        </div>
      </header>

      <section className="max-w-6xl mx-auto px-6 pt-20 pb-16 grid md:grid-cols-2 gap-12 items-center">
        <div>
          <p className="label-eyebrow mb-4">AST-based plagiarism detection</p>
          <h1 className="font-display text-4xl md:text-5xl font-bold text-slate-50 leading-tight">
            Two programs can look nothing alike<br />and still be the same code.
          </h1>
          <p className="mt-5 text-slate-400 text-base leading-relaxed max-w-lg">
            CodeGuard analyzes the structure beneath the syntax — comparing Abstract Syntax
            Trees, normalized tokens, and learned similarity signals to catch what text-diffing
            tools miss: renamed variables, reformatted code, and reworded logic.
          </p>
          <div className="mt-8 flex items-center gap-3">
            <Link to="/register" className="btn-primary">
              Start detecting <ArrowRight className="w-4 h-4" />
            </Link>
            <Link to="/login" className="btn-secondary">I have an account</Link>
          </div>
        </div>
        <ASTHeroVisual />
      </section>

      <section className="max-w-6xl mx-auto px-6 py-16 border-t border-edge">
        <p className="label-eyebrow mb-3">How it works</p>
        <div className="grid md:grid-cols-4 gap-6">
          {STEPS.map((step) => (
            <div key={step.n} className="relative">
              <span className="font-display text-3xl font-bold text-edge">{step.n}</span>
              <h3 className="font-semibold text-slate-100 mt-2">{step.title}</h3>
              <p className="text-sm text-slate-400 mt-1.5 leading-relaxed">{step.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="max-w-6xl mx-auto px-6 py-16 border-t border-edge">
        <p className="label-eyebrow mb-3">Main features</p>
        <div className="grid md:grid-cols-3 gap-6">
          {FEATURES.map(({ icon: Icon, title, desc }) => (
            <div key={title} className="card p-6">
              <Icon className="w-6 h-6 text-cyan-400 mb-4" />
              <h3 className="font-semibold text-slate-100">{title}</h3>
              <p className="text-sm text-slate-400 mt-2 leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="max-w-6xl mx-auto px-6 py-16 border-t border-edge">
        <p className="label-eyebrow mb-3">Technology</p>
        <div className="flex flex-wrap gap-2">
          {['React', 'FastAPI', 'Python AST', 'scikit-learn', 'SQLAlchemy', 'JWT Auth', 'Tailwind CSS'].map((t) => (
            <span key={t} className="font-mono text-xs px-3 py-1.5 rounded-full border border-edge text-slate-400">
              {t}
            </span>
          ))}
        </div>
      </section>

      <footer className="border-t border-edge py-8">
        <div className="max-w-6xl mx-auto px-6 text-xs text-slate-500 font-mono flex flex-col sm:flex-row justify-between gap-2">
          <span>CodeGuard — academic reference project</span>
          <span>Similarity scores indicate structural similarity, not proof of misconduct.</span>
        </div>
      </footer>
    </div>
  )
}
