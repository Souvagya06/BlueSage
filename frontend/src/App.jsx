import { Routes, Route, Link, useLocation } from 'react-router-dom'
import { Droplets, Map, BarChart3, TrendingUp, Download } from 'lucide-react'
import { getExportDatasetUrl } from './api/client'
import Dashboard from './pages/Dashboard'
import Explore from './pages/Explore'
import Predict from './pages/Predict'
import clsx from 'clsx'

const NAV = [
  { to: '/',        label: 'Dashboard', icon: BarChart3 },
  { to: '/explore', label: 'Explore Map', icon: Map },
  { to: '/predict', label: 'Predictions', icon: TrendingUp },
]

export default function App() {
  const { pathname } = useLocation()

  return (
    <div className="flex flex-col min-h-screen bg-slate-50">
      {/* ── Header ── */}
      <header className="bg-water-800 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 h-14 flex items-center gap-6">
          <div className="flex items-center gap-2 font-bold text-lg">
            <Droplets className="w-6 h-6 text-water-300" />
            <span>BlueSage</span>
            <span className="text-water-400 font-normal text-sm hidden sm:block">
              — Global Water Body Monitor
            </span>
          </div>
          <nav className="ml-auto flex gap-1">
            {NAV.map(({ to, label, icon: Icon }) => (
              <Link
                key={to}
                to={to}
                className={clsx(
                  'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
                  pathname === to
                    ? 'bg-water-600 text-white'
                    : 'text-water-200 hover:bg-water-700 hover:text-white'
                )}
              >
                <Icon className="w-4 h-4" />
                <span className="hidden sm:block">{label}</span>
              </Link>
            ))}

            <a
              href={getExportDatasetUrl()}
              download="indexed_waterbody_dataset.csv"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm transition-colors ml-2"
              title="Download full indexed temporal water body dataset (CSV)"
            >
              <Download className="w-4 h-4" />
              <span className="hidden md:inline">Export Dataset</span>
              <span>CSV</span>
            </a>
          </nav>
        </div>
      </header>

      {/* ── Main ── */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 py-6">
        <Routes>
          <Route path="/"        element={<Dashboard />} />
          <Route path="/explore" element={<Explore />} />
          <Route path="/predict" element={<Predict />} />
        </Routes>
      </main>

      <footer className="text-center text-xs text-slate-400 py-3 border-t border-slate-200">
        BlueSage — Temporal Water Body Dataset | Data: HydroLAKES · USGS WQP · JRC GSW
      </footer>
    </div>
  )
}

