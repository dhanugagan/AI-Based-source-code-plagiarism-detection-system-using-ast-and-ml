/**
 * Signature visual: a stylized side-by-side AST comparison, echoing the
 * core mechanic of the product (two programs, structurally overlaid).
 */
export default function ASTHeroVisual() {
  return (
    <div className="relative font-mono text-[13px] leading-relaxed">
      <div className="grid grid-cols-2 gap-4">
        <div className="card p-4">
          <div className="flex items-center gap-1.5 mb-3 text-slate-500 text-xs">
            <span className="w-2 h-2 rounded-full bg-risk-critical/70" />
            <span className="w-2 h-2 rounded-full bg-risk-medium/70" />
            <span className="w-2 h-2 rounded-full bg-risk-low/70" />
            <span className="ml-2">submission_a.py</span>
          </div>
          <pre className="text-slate-400">
<span className="text-cyan-300">Module</span>{"\n"}
{"  "}<span className="text-slate-300">Assign</span> → a{"\n"}
{"  "}<span className="text-slate-300">Assign</span> → b{"\n"}
{"  "}<span className="text-slate-300">Assign</span> → c = a + b{"\n"}
{"  "}<span className="text-slate-300">Call</span> → print(c)
          </pre>
        </div>
        <div className="card p-4">
          <div className="flex items-center gap-1.5 mb-3 text-slate-500 text-xs">
            <span className="w-2 h-2 rounded-full bg-risk-critical/70" />
            <span className="w-2 h-2 rounded-full bg-risk-medium/70" />
            <span className="w-2 h-2 rounded-full bg-risk-low/70" />
            <span className="ml-2">submission_b.py</span>
          </div>
          <pre className="text-slate-400">
<span className="text-cyan-300">Module</span>{"\n"}
{"  "}<span className="text-slate-300">Assign</span> → x{"\n"}
{"  "}<span className="text-slate-300">Assign</span> → y{"\n"}
{"  "}<span className="text-slate-300">Assign</span> → total = x + y{"\n"}
{"  "}<span className="text-slate-300">Call</span> → print(total)
          </pre>
        </div>
      </div>
      <div className="mt-4 flex items-center justify-center gap-2">
        <span className="diff-marker plus">≡</span>
        <span className="text-xs text-slate-500 font-mono">structurally identical · 100% AST match</span>
      </div>
    </div>
  )
}
