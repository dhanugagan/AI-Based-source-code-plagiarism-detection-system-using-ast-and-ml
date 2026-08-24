import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6 text-center">
      <span className="font-display text-6xl font-bold text-edge">404</span>
      <p className="text-slate-400 mt-3 mb-6">This page doesn't exist.</p>
      <Link to="/" className="btn-primary">Go home</Link>
    </div>
  )
}
