import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { ShieldCheck, LayoutDashboard, UploadCloud, GitCompare, Grid3x3, History, ShieldAlert, LogOut } from 'lucide-react'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  if (!user) return null

  const links = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/upload', label: 'Upload', icon: UploadCloud },
    { to: '/compare', label: 'Compare', icon: GitCompare },
    { to: '/batch', label: 'Batch', icon: Grid3x3 },
    { to: '/history', label: 'History', icon: History },
  ]
  if (user.role === 'admin') {
    links.push({ to: '/admin', label: 'Admin', icon: ShieldAlert })
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <header className="border-b border-edge bg-surface/80 backdrop-blur sticky top-0 z-40">
      <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link to="/dashboard" className="flex items-center gap-2 font-display font-bold text-slate-100">
          <ShieldCheck className="w-5 h-5 text-cyan-400" />
          <span>CodeGuard</span>
        </Link>

        <nav className="hidden md:flex items-center gap-1">
          {links.map(({ to, label, icon: Icon }) => {
            const active = location.pathname === to
            return (
              <Link
                key={to}
                to={to}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  active ? 'bg-cyan-400/10 text-cyan-300' : 'text-slate-400 hover:text-slate-200 hover:bg-surface-alt'
                }`}
              >
                <Icon className="w-4 h-4" />
                {label}
              </Link>
            )
          })}
        </nav>

        <div className="flex items-center gap-3">
          <span className="hidden sm:block text-sm text-slate-400 font-mono">{user.name}</span>
          <button onClick={handleLogout} className="btn-secondary !px-3 !py-2">
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
      <nav className="md:hidden flex overflow-x-auto gap-1 px-4 pb-2">
        {links.map(({ to, label, icon: Icon }) => {
          const active = location.pathname === to
          return (
            <Link
              key={to}
              to={to}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap ${
                active ? 'bg-cyan-400/10 text-cyan-300' : 'text-slate-400'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              {label}
            </Link>
          )
        })}
      </nav>
    </header>
  )
}
