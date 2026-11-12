/**
 * FilterBar.jsx
 * City search + type/quality/year filters for the Explore page.
 */
import { useState, useRef } from 'react'
import { Search, X, Filter } from 'lucide-react'
import { geocodeCity } from '../api/client'

const TYPES = ['', 'lake', 'pond', 'reservoir', 'river', 'wetland']
const QUALITIES = ['', 'excellent', 'good', 'fair', 'poor', 'critical']

export default function FilterBar({ onSearch, onFilter, loading }) {
  const [query, setQuery] = useState('')
  const [suggestions, setSuggestions] = useState([])
  const [filters, setFilters] = useState({ water_body_type: '', quality_status: '', year: '' })
  const [showFilters, setShowFilters] = useState(false)
  const debounceRef = useRef(null)
  const wrapperRef = useRef(null)

  const handleQueryChange = (val) => {
    setQuery(val)
    clearTimeout(debounceRef.current)
    if (val.length < 3) { setSuggestions([]); return }
    debounceRef.current = setTimeout(async () => {
      try {
        const res = await geocodeCity(val)
        setSuggestions(res.slice(0, 6))
      } catch { setSuggestions([]) }
    }, 350)
  }

  const handleSelectSuggestion = (place) => {
    setQuery(place.display_name.split(',').slice(0, 2).join(', '))
    setSuggestions([])
    onSearch({ lat: parseFloat(place.lat), lon: parseFloat(place.lon), name: place.display_name })
  }

  const handleFilterChange = (key, val) => {
    const newFilters = { ...filters, [key]: val }
    setFilters(newFilters)
    onFilter && onFilter(newFilters)
  }

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow p-4 space-y-3" style={{ position: 'relative', zIndex: 1000 }}>
      {/* City search — isolated stacking context so dropdown always floats above Leaflet */}
      <div ref={wrapperRef} style={{ position: 'relative', isolation: 'isolate' }}>
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" style={{ zIndex: 1 }} />
        <input
          type="text"
          value={query}
          onChange={e => handleQueryChange(e.target.value)}
          onBlur={() => setTimeout(() => setSuggestions([]), 200)}
          placeholder="Search any city in the world... (e.g. Mumbai, Tokyo, Chicago)"
          className="w-full pl-9 pr-8 py-2 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-water-400 focus:border-water-400 outline-none"
        />
        {query && (
          <button onClick={() => { setQuery(''); setSuggestions([]) }} className="absolute right-3 top-1/2 -translate-y-1/2" style={{ zIndex: 2 }}>
            <X className="w-4 h-4 text-slate-400 hover:text-slate-600" />
          </button>
        )}

        {/* Autocomplete dropdown — z-index must beat Leaflet's 400 */}
        {suggestions.length > 0 && (
          <div
            style={{
              position: 'absolute',
              top: '100%',
              left: 0,
              right: 0,
              marginTop: '4px',
              zIndex: 9999,
              background: 'white',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              boxShadow: '0 8px 24px rgba(0,0,0,0.15)',
              overflow: 'hidden',
            }}
          >
            {suggestions.map((s, i) => (
              <button
                key={i}
                onMouseDown={() => handleSelectSuggestion(s)}   /* onMouseDown fires before onBlur */
                className="w-full text-left px-4 py-2.5 text-sm hover:bg-blue-50 border-b border-slate-50 last:border-0"
              >
                <span className="font-medium text-slate-800">{s.display_name.split(',')[0]}</span>
                <span className="text-slate-400 ml-1 text-xs">{s.display_name.split(',').slice(1, 3).join(',')}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Filter toggle */}
      <button
        onClick={() => setShowFilters(f => !f)}
        className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-water-700 font-medium"
      >
        <Filter className="w-3.5 h-3.5" />
        {showFilters ? 'Hide filters' : 'Show filters'}
      </button>

      {showFilters && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
          <div>
            <label className="block text-xs text-slate-500 mb-1">Type</label>
            <select
              value={filters.water_body_type}
              onChange={e => handleFilterChange('water_body_type', e.target.value)}
              className="w-full border border-slate-200 rounded-lg text-sm px-2 py-1.5 focus:ring-2 focus:ring-water-400 outline-none capitalize"
            >
              {TYPES.map(t => <option key={t} value={t}>{t || 'All types'}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs text-slate-500 mb-1">Quality Status</label>
            <select
              value={filters.quality_status}
              onChange={e => handleFilterChange('quality_status', e.target.value)}
              className="w-full border border-slate-200 rounded-lg text-sm px-2 py-1.5 focus:ring-2 focus:ring-water-400 outline-none capitalize"
            >
              {QUALITIES.map(q => <option key={q} value={q}>{q || 'All qualities'}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs text-slate-500 mb-1">Year</label>
            <input
              type="number"
              min="2014" max="2024"
              value={filters.year}
              onChange={e => handleFilterChange('year', e.target.value)}
              placeholder="2014–2024"
              className="w-full border border-slate-200 rounded-lg text-sm px-2 py-1.5 focus:ring-2 focus:ring-water-400 outline-none"
            />
          </div>
        </div>
      )}
    </div>
  )
}

