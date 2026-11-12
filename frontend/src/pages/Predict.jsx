/**
 * Predict.jsx
 * Dedicated predictions page — search a city, pick a water body,
 * view 10-year future forecast for NDWI, area, and quality.
 */
import { useState, useMemo } from 'react'
import { TrendingUp, Search } from 'lucide-react'
import { geocodeCity } from '../api/client'
import { useWaterBodiesNear, useObservations, usePrediction } from '../hooks/useWaterBodies'
import PredictionChart from '../components/PredictionChart'
import clsx from 'clsx'

const QUALITY_STYLES = {
  excellent: 'bg-green-100 text-green-800',
  good:      'bg-lime-100 text-lime-800',
  fair:      'bg-amber-100 text-amber-800',
  poor:      'bg-red-100 text-red-800',
  critical:  'bg-red-900 text-white',
}

const TREND_STYLES = {
  stable:    'bg-blue-100 text-blue-800',
  shrink:    'bg-orange-100 text-orange-800',
  expand:    'bg-emerald-100 text-emerald-800',
  disappear: 'bg-red-100 text-red-800',
}

export default function Predict() {
  const [query, setQuery] = useState('')
  const [suggestions, setSuggestions] = useState([])
  const [location, setLocation] = useState(null)
  const [selectedWbId, setSelectedWbId] = useState(null)
  const [metric, setMetric] = useState('ndwi')

  const { data: nearbyWbs = [], isLoading } = useWaterBodiesNear(
    { lat: location?.lat, lon: location?.lon, radius_km: 100 },
    !!location
  )

  const { data: observations = [] } = useObservations(selectedWbId)
  const { data: predData, isLoading: predLoading } = usePrediction(selectedWbId, 10)
  const predictions = predData?.predictions || []

  const selectedWb = nearbyWbs.find(w => w.id === selectedWbId)

  const handleSearch = async (val) => {
    setQuery(val)
    if (val.length < 3) { setSuggestions([]); return }
    try {
      const res = await geocodeCity(val)
      setSuggestions(res.slice(0, 5))
    } catch { setSuggestions([]) }
  }

  const handleSelect = (place) => {
    setQuery(place.display_name.split(',').slice(0, 2).join(', '))
    setSuggestions([])
    setLocation({ lat: parseFloat(place.lat), lon: parseFloat(place.lon), name: place.display_name })
    setSelectedWbId(null)
  }

  // Last prediction row for summary cards
  const lastPred = predictions.length ? predictions[predictions.length - 1] : null

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-800">Future Predictions</h1>
        <p className="text-slate-500 text-xs mt-0.5">
          ML-powered 10-year forecasts for water body NDWI, area, and quality status
        </p>
      </div>

      {/* City search */}
      <div className="bg-white border border-slate-200 rounded-xl shadow p-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text" value={query}
            onChange={e => handleSearch(e.target.value)}
            placeholder="Search a city to find its water bodies..."
            className="w-full pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-water-400 outline-none"
          />
          {suggestions.length > 0 && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-slate-200 rounded-lg shadow-lg z-50">
              {suggestions.map((s, i) => (
                <button key={i} onClick={() => handleSelect(s)}
                  className="w-full text-left px-4 py-2 text-sm hover:bg-water-50 border-b border-slate-50 last:border-0 truncate">
                  {s.display_name}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Water body list */}
        <div className="lg:col-span-1">
          <h2 className="font-semibold text-slate-700 text-sm mb-2">
            {location ? `Water Bodies near ${location.name?.split(',')[0]}` : 'Search a city first'}
          </h2>
          <div className="bg-white border border-slate-200 rounded-xl shadow divide-y divide-slate-100 max-h-[480px] overflow-y-auto">
            {isLoading && (
              <div className="text-center py-8 text-slate-400 text-sm">Loading...</div>
            )}
            {!isLoading && !location && (
              <div className="text-center py-8 text-slate-300 text-sm">
                <TrendingUp className="w-8 h-8 mx-auto mb-2 opacity-30" />
                Search a city to see water bodies
              </div>
            )}
            {!isLoading && location && nearbyWbs.length === 0 && (
              <div className="text-center py-8 text-slate-400 text-sm">No water bodies found nearby.</div>
            )}
            {nearbyWbs.map(wb => (
              <button
                key={wb.id}
                onClick={() => setSelectedWbId(wb.id)}
                className={clsx(
                  'w-full text-left px-4 py-3 hover:bg-water-50 transition-colors',
                  selectedWbId === wb.id && 'bg-water-50 border-l-4 border-water-500'
                )}
              >
                <div className="font-medium text-slate-700 text-sm truncate">{wb.name}</div>
                <div className="text-xs text-slate-400 capitalize">{wb.water_body_type}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Predictions detail */}
        <div className="lg:col-span-2 space-y-4">
          {!selectedWbId ? (
            <div className="bg-white border border-slate-200 rounded-xl shadow flex items-center justify-center h-64">
              <div className="text-center text-slate-300">
                <TrendingUp className="w-10 h-10 mx-auto mb-2 opacity-40" />
                <p className="text-sm">Select a water body to see predictions</p>
              </div>
            </div>
          ) : (
            <>
              {/* Summary prediction cards */}
              {lastPred && (
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                  <div className="bg-white border border-slate-200 rounded-xl shadow p-4 text-center">
                    <div className="text-xs text-slate-400 mb-1">NDWI in {lastPred.target_year}</div>
                    <div className="text-2xl font-bold text-water-700">{lastPred.predicted_ndwi?.toFixed(3)}</div>
                    <div className="text-xs text-slate-400 mt-1">Predicted</div>
                  </div>
                  <div className="bg-white border border-slate-200 rounded-xl shadow p-4 text-center">
                    <div className="text-xs text-slate-400 mb-1">Area in {lastPred.target_year}</div>
                    <div className="text-2xl font-bold text-emerald-600">{lastPred.predicted_area_sq_km?.toFixed(1)} km²</div>
                    <div className="text-xs text-slate-400 mt-1">Predicted</div>
                  </div>
                  <div className="bg-white border border-slate-200 rounded-xl shadow p-4 text-center">
                    <div className="text-xs text-slate-400 mb-1">Quality in {lastPred.target_year}</div>
                    <span className={clsx('text-sm font-semibold px-2 py-1 rounded-full capitalize', QUALITY_STYLES[lastPred.predicted_quality_status])}>
                      {lastPred.predicted_quality_status}
                    </span>
                    <div className="text-xs text-slate-400 mt-2">Predicted</div>
                  </div>
                  <div className="bg-white border border-slate-200 rounded-xl shadow p-4 text-center">
                    <div className="text-xs text-slate-400 mb-1">Trend by {lastPred.target_year}</div>
                    <span className={clsx('text-sm font-semibold px-2 py-1 rounded-full capitalize', TREND_STYLES[lastPred.change_trend || 'stable'])}>
                      {lastPred.change_trend || 'stable'}
                    </span>
                    <div className="text-xs text-slate-400 mt-2">Morphology Forecast</div>
                  </div>
                </div>
              )}

              {/* Chart */}
              <div className="bg-white border border-slate-200 rounded-xl shadow p-4">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-slate-700 text-sm">
                    {selectedWb?.name} — Historical + Forecast
                  </h3>
                  <div className="flex gap-1">
                    {['ndwi', 'area', 'quality'].map(m => (
                      <button key={m} onClick={() => setMetric(m)}
                        className={clsx(
                          'px-2 py-1 text-xs rounded font-medium',
                          metric === m ? 'bg-water-600 text-white' : 'bg-slate-100 text-slate-500 hover:bg-slate-200'
                        )}
                      >
                        {m === 'ndwi' ? 'NDWI' : m === 'area' ? 'Area' : 'Quality'}
                      </button>
                    ))}
                  </div>
                </div>
                {predLoading ? (
                  <div className="h-60 flex items-center justify-center text-slate-400 text-sm">Computing predictions...</div>
                ) : (
                  <PredictionChart observations={observations} predictions={predictions} metric={metric} />
                )}
                <p className="text-xs text-slate-400 mt-2 text-center">
                  Solid = real data (2014–2024) · Dashed = ML polynomial regression predictions
                </p>
              </div>

              {/* Prediction table */}
              {predictions.length > 0 && (
                <div className="bg-white border border-slate-200 rounded-xl shadow overflow-hidden">
                  <div className="px-4 py-3 border-b border-slate-100 text-sm font-semibold text-slate-700">
                    Year-by-Year Predictions
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs">
                      <thead className="bg-slate-50 text-slate-500">
                        <tr>
                          <th className="px-4 py-2 text-left">Year</th>
                          <th className="px-4 py-2 text-right">NDWI</th>
                          <th className="px-4 py-2 text-right">Area (km²)</th>
                          <th className="px-4 py-2 text-center">Trend</th>
                          <th className="px-4 py-2 text-right">Quality Score</th>
                          <th className="px-4 py-2 text-center">Status</th>
                          <th className="px-4 py-2 text-right">Confidence</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-50">
                        {predictions.map(p => (
                          <tr key={p.target_year} className="hover:bg-slate-50">
                            <td className="px-4 py-2 font-medium">{p.target_year}</td>
                            <td className="px-4 py-2 text-right">{p.predicted_ndwi?.toFixed(4)}</td>
                            <td className="px-4 py-2 text-right">{p.predicted_area_sq_km?.toFixed(2)}</td>
                            <td className="px-4 py-2 text-center">
                              <span className={clsx('px-2 py-0.5 rounded-full capitalize font-medium', TREND_STYLES[p.change_trend || 'stable'])}>
                                {p.change_trend || 'stable'}
                              </span>
                            </td>
                            <td className="px-4 py-2 text-right">{p.predicted_quality_score?.toFixed(1)}</td>
                            <td className="px-4 py-2 text-center">
                              <span className={clsx('px-2 py-0.5 rounded-full capitalize', QUALITY_STYLES[p.predicted_quality_status])}>
                                {p.predicted_quality_status}
                              </span>
                            </td>
                            <td className="px-4 py-2 text-right text-slate-500">{(p.confidence_score * 100).toFixed(0)}%</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

