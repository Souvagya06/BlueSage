/**
 * Explore.jsx
 * City search → map showing water bodies nearby → detail panel.
 * Core page of BlueSage.
 */
import { useState, useMemo, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import FilterBar from '../components/FilterBar'
import WaterBodyMap from '../components/WaterBodyMap'
import WaterBodyTable from '../components/WaterBodyTable'
import ClassificationPanel from '../components/ClassificationPanel'
import PredictionChart from '../components/PredictionChart'
import { useWaterBodiesNear, useWaterBodyById, useObservations, usePrediction } from '../hooks/useWaterBodies'
import { Droplets, X, ChevronRight, Eye } from 'lucide-react'
import clsx from 'clsx'

const QUALITY_BADGE = {
  excellent: 'bg-green-100 text-green-800',
  good:      'bg-lime-100 text-lime-800',
  fair:      'bg-amber-100 text-amber-800',
  poor:      'bg-red-100 text-red-800',
  critical:  'bg-red-900 text-white',
}

export default function Explore() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [searchLoc, setSearchLoc] = useState(null)   // { lat, lon, name }
  const [filters, setFilters] = useState({})
  const [selectedId, setSelectedId] = useState(searchParams.get('wb') ? Number(searchParams.get('wb')) : null)
  const [chartMetric, setChartMetric] = useState('ndwi')

  // Fetch nearby water bodies when user searches a city
  const { data: nearbyWbs = [], isLoading: nearbyLoading } = useWaterBodiesNear(
    { lat: searchLoc?.lat, lon: searchLoc?.lon, radius_km: 200 },
    !!searchLoc
  )

  // Fetch detail for selected water body
  const { data: selectedWb } = useWaterBodyById(selectedId)
  const { data: observations = [] } = useObservations(selectedId)
  const { data: predData } = usePrediction(selectedId, 10)

  const predictions = predData?.predictions || []

  // ── Auto-fly: when arriving from Dashboard (?wb=X) with no searchLoc,
  //    use the loaded water body's coordinates to centre the map and load
  //    nearby water bodies so the table and markers populate.
  useEffect(() => {
    if (selectedWb && !searchLoc && selectedWb.latitude && selectedWb.longitude) {
      setSearchLoc({
        lat: selectedWb.latitude,
        lon: selectedWb.longitude,
        name: `${selectedWb.name}, ${selectedWb.country}`,
      })
    }
  }, [selectedWb, searchLoc])

  // Build obs map for map markers
  const obsMap = useMemo(() => {
    const m = {}
    nearbyWbs.forEach(wb => {
      if (wb.observations?.length) {
        const latest = [...wb.observations].sort((a, b) => b.observation_year - a.observation_year)[0]
        m[wb.id] = latest
      }
    })
    return m
  }, [nearbyWbs])

  // Latest observation for selected WB
  const latestObs = useMemo(() => {
    if (!observations.length) return null
    return [...observations].sort((a, b) => b.observation_year - a.observation_year)[0]
  }, [observations])

  const handleSearch = (loc) => {
    setSearchLoc(loc)
    setSelectedId(null)
  }

  const handleSelectWb = (wb) => {
    setSelectedId(wb.id)
    setSearchParams({ wb: wb.id })
  }

  const handleCloseDetail = () => {
    setSelectedId(null)
    setSearchParams({})
  }

  const flyTo = searchLoc
    ? {
        center: [searchLoc.lat, searchLoc.lon],
        // zoom in tighter when arriving directly from a water body link
        zoom: selectedId && !nearbyWbs.length ? 13 : 11,
      }
    : null

  // Always include the selectedWb in the displayed list so its marker shows
  // even before nearbyWbs loads (e.g. arriving from Dashboard with ?wb=X)
  const displayWbs = useMemo(() => {
    if (!selectedWb) return nearbyWbs
    const alreadyIn = nearbyWbs.some(w => w.id === selectedWb.id)
    return alreadyIn ? nearbyWbs : [selectedWb, ...nearbyWbs]
  }, [nearbyWbs, selectedWb])

  const filteredWbs = useMemo(() => {
    return nearbyWbs.filter(wb => {
      if (filters.water_body_type && wb.water_body_type !== filters.water_body_type) return false
      if (filters.quality_status) {
        const obs = obsMap[wb.id]
        if (!obs || obs.water_quality_status !== filters.quality_status) return false
      }
      return true
    })
  }, [nearbyWbs, filters, obsMap])

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-bold text-slate-800">Explore Water Bodies</h1>
        <p className="text-slate-500 text-xs mt-0.5">Search any city — see all water bodies, their history (2014–2024), and future predictions</p>
      </div>

      {/* Search + Filters */}
      <FilterBar onSearch={handleSearch} onFilter={setFilters} loading={nearbyLoading} />

      {/* Main layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Map — takes 2/3 */}
        <div className="lg:col-span-2">
          <WaterBodyMap
            waterBodies={filteredWbs}
            observations={obsMap}
            height="420px"
            flyTo={flyTo}
            selectedId={selectedId}
            onSelectWaterBody={handleSelectWb}
          />
          {searchLoc && (
            <p className="text-xs text-slate-400 mt-1">
              📍 {searchLoc.name?.split(',').slice(0, 3).join(',')} · {filteredWbs.length > 0 ? filteredWbs.length : nearbyWbs.length} water bodies found
              {filteredWbs.length === 0 && nearbyWbs.length > 0 && (
                <span className="ml-1 text-amber-500">(showing nearest {nearbyWbs.length})</span>
              )}
            </p>
          )}
          {!searchLoc && (
            <p className="text-xs text-slate-400 mt-1 text-center">
              ↑ Type a city name above to see water bodies on the map
            </p>
          )}
        </div>

        {/* Right panel — ML Classification */}
        <div className="space-y-4">
          <ClassificationPanel waterBody={selectedWb} latestObs={latestObs} />

          {/* Quick info card for selected WB */}
          {selectedWb && (
            <div className="bg-white border border-slate-200 rounded-xl shadow p-4">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <div className="font-semibold text-slate-800 text-sm">{selectedWb.name}</div>
                  <div className="text-xs text-slate-500 capitalize">{selectedWb.water_body_type} · {selectedWb.country}</div>
                </div>
                <button onClick={handleCloseDetail} className="text-slate-300 hover:text-slate-500">
                  <X className="w-4 h-4" />
                </button>
              </div>
              {latestObs && (
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs mt-2">
                  <div className="bg-slate-50 rounded p-2">
                    <div className="text-slate-400">Area (latest)</div>
                    <div className="font-semibold text-slate-700">{latestObs.area_sq_km?.toFixed(2)} km²</div>
                  </div>
                  <div className="bg-slate-50 rounded p-2">
                    <div className="text-slate-400">NDWI (latest)</div>
                    <div className="font-semibold text-slate-700">{latestObs.ndwi?.toFixed(3)}</div>
                  </div>
                  <div className="bg-slate-50 rounded p-2">
                    <div className="text-slate-400">Water Occurrence</div>
                    <div className="font-semibold text-slate-700">{latestObs.water_occurrence_pct?.toFixed(1)}%</div>
                  </div>
                  <div className="bg-slate-50 rounded p-2">
                    <div className="text-slate-400">Dissolved Oxygen</div>
                    <div className="font-semibold text-slate-700">{latestObs.dissolved_oxygen_mgl?.toFixed(1)} mg/L</div>
                  </div>
                  <div className="bg-slate-50 rounded p-2">
                    <div className="text-slate-400">Turbidity</div>
                    <div className="font-semibold text-slate-700">{latestObs.turbidity_ntu?.toFixed(1)} NTU</div>
                  </div>
                  <div className="bg-slate-50 rounded p-2">
                    <div className="text-slate-400">pH Level</div>
                    <div className="font-semibold text-slate-700">{latestObs.ph?.toFixed(2)}</div>
                  </div>
                  <div className="bg-slate-50 rounded p-2">
                    <div className="text-slate-400">Chlorophyll-a</div>
                    <div className="font-semibold text-slate-700">{latestObs.chlorophyll_a_ugl?.toFixed(1)} µg/L</div>
                  </div>
                  <div className="bg-slate-50 rounded p-2">
                    <div className="text-slate-400">Seasonality</div>
                    <div className="font-semibold text-slate-700">{latestObs.seasonality_months} mo/yr</div>
                  </div>
                  <div className="bg-slate-50 rounded p-2">
                    <div className="text-slate-400">Spatial Index</div>
                    <div className="font-semibold text-slate-700 font-mono truncate">{selectedWb.spatial_grid_index || 'GEO_225_088'}</div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Timeline chart for selected WB */}
      {selectedWb && observations.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-xl shadow p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-slate-700 text-sm">
              Historical + Predicted Trends — {selectedWb.name}
            </h3>
            <div className="flex gap-1">
              {['ndwi', 'area', 'quality'].map(m => (
                <button
                  key={m}
                  onClick={() => setChartMetric(m)}
                  className={clsx(
                    'px-2 py-1 text-xs rounded-md font-medium transition-colors',
                    chartMetric === m
                      ? 'bg-water-600 text-white'
                      : 'bg-slate-100 text-slate-500 hover:bg-slate-200'
                  )}
                >
                  {m === 'ndwi' ? 'NDWI' : m === 'area' ? 'Area' : 'Quality'}
                </button>
              ))}
            </div>
          </div>
          <PredictionChart
            observations={observations}
            predictions={predictions}
            metric={chartMetric}
          />
          <p className="text-xs text-slate-400 mt-2 text-center">
            Solid line = real historical data · Dashed line = ML predictions (2025–{new Date().getFullYear() + 10})
          </p>
        </div>
      )}

      {/* Table — always visible after a search */}
      {searchLoc && (
        <div>
          <div className="flex items-center justify-between mb-2">
            <h2 className="font-semibold text-slate-700 text-sm">
              Water Bodies near {searchLoc?.name?.split(',')[0]}
              {filteredWbs.length > 0 && (
                <span className="ml-2 text-xs font-normal text-slate-400">({filteredWbs.length} found)</span>
              )}
            </h2>
            {filteredWbs.length === 0 && nearbyWbs.length === 0 && !nearbyLoading && (
              <span className="text-xs text-amber-600 font-medium">
                💡 No water bodies in 200 km radius — showing nearest matches
              </span>
            )}
          </div>
          <WaterBodyTable
            waterBodies={filteredWbs.length > 0 ? filteredWbs : nearbyWbs}
            observations={obsMap}
            onSelect={handleSelectWb}
          />
        </div>
      )}
    </div>
  )
}

