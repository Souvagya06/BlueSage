import { useState, useRef, useEffect } from 'react'
import { Routes, Route, Link, useLocation } from 'react-router-dom'
import { Droplets, Map, BarChart3, TrendingUp, Download, ChevronDown } from 'lucide-react'
import { getExportDatasetUrl } from './api/client'
import Dashboard from './pages/Dashboard'
import Explore from './pages/Explore'
import Predict from './pages/Predict'
import clsx from 'clsx'

const DATASET_PARTITIONS = [
  { id: 'all', label: 'All Water Bodies', count: '3,201 records', icon: '🌐' },
  { id: 'wetland', label: 'Wetlands Only', count: '396 records', icon: '🌿' },
  { id: 'pond', label: 'Ponds Only', count: '374 records', icon: '🫧' },
  { id: 'river', label: 'Rivers Only', count: '473 records', icon: '🏞️' },
  { id: 'lake', label: 'Lakes Only', count: '1,419 records', icon: '🌊' },
  { id: 'reservoir', label: 'Reservoirs Only', count: '539 records', icon: '🏗️' },
]

const NAV = [
  { to: '/',        label: 'Dashboard', icon: BarChart3 },
  { to: '/explore', label: 'Explore Map', icon: Map },
  { to: '/predict', label: 'Predictions', icon: TrendingUp },
]

export default function App() {
  const { pathname } = useLocation()
  const [showExportMenu, setShowExportMenu] = useState(false)
  const menuRef = useRef(null)

  useEffect(() => {
    function handleClickOutside(e) {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setShowExportMenu(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div className="flex flex-col min-h-screen bg-slate-50">
      {/* ── Header ── */}
      <header className="bg-water-800 text-white shadow-lg sticky top-0 z-[9999]">
        <div className="max-w-7xl mx-auto px-4 h-14 flex items-center gap-6">
          <div className="flex items-center gap-2 font-bold text-lg">
            <Droplets className="w-6 h-6 text-water-300" />
            <span>BlueSage</span>
            <span className="text-water-400 font-normal text-sm hidden sm:block">
              — Global Water Body Monitor
            </span>
          </div>
          <nav className="ml-auto flex items-center gap-1">
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

            {/* ── Export Indexed Dataset Dropdown ── */}
            <div className="relative ml-2" ref={menuRef}>
              <button
                onClick={() => setShowExportMenu(v => !v)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm transition-colors"
                title="Download indexed dataset partitioned by water body type"
              >
                <Download className="w-4 h-4" />
                <span className="hidden md:inline">Export Dataset</span>
                <span>CSV</span>
                <ChevronDown className="w-3.5 h-3.5 opacity-80" />
              </button>

              {showExportMenu && (
                <div className="absolute right-0 mt-2 w-64 bg-white border border-slate-200 rounded-xl shadow-2xl py-2 z-[99999] text-slate-800">
                  <div className="px-3 py-1.5 border-b border-slate-100">
                    <div className="text-xs font-bold text-slate-700 uppercase tracking-wide">
                      Indexed Datasets (.CSV)
                    </div>
                    <div className="text-[11px] text-slate-400">
                      Download full or type-indexed subsets
                    </div>
                  </div>
                  <div className="py-1">
                    {DATASET_PARTITIONS.map(p => (
                      <a
                        key={p.id}
                        href={getExportDatasetUrl(p.id)}
                        download={p.id === 'all' ? 'indexed_waterbody_dataset.csv' : `indexed_waterbody_dataset_${p.id}.csv`}
                        onClick={() => setShowExportMenu(false)}
                        className="flex items-center justify-between px-3 py-2 text-xs hover:bg-blue-50 transition-colors"
                      >
                        <span className="flex items-center gap-2 font-medium text-slate-700">
                          <span>{p.icon}</span>
                          <span>{p.label}</span>
                        </span>
                        <span className="text-[11px] font-mono text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded">
                          {p.count}
                        </span>
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>
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

