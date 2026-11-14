/**
 * Dashboard.jsx
 * Overview page: global stats, legend, and a world map with all water bodies.
 */
import { useState, useMemo, useRef, useEffect } from 'react'
import { Droplets, Globe, TrendingDown, AlertTriangle, Download, Database, ExternalLink, Satellite, FlaskConical, Map, ChevronDown, Filter, FileSpreadsheet, Layers } from 'lucide-react'
import { getExportDatasetUrl } from '../api/client'
import { useWaterBodies } from '../hooks/useWaterBodies'
import WaterBodyMap from '../components/WaterBodyMap'
import { useNavigate } from 'react-router-dom'

// ─── Partitioned Dataset Cards ───────────────────────────────────────────────
const PARTITION_CARDS = [
  {
    type: 'all',
    title: 'Complete Indexed Dataset',
    subtitle: 'All 5 Water Body Types Combined',
    records: '1,650 records',
    wbCount: '150 water bodies',
    icon: '🌐',
    color: 'border-slate-300 bg-white hover:border-slate-400',
    badge: 'Complete Master',
    badgeColor: 'bg-slate-800 text-white',
    btnColor: 'bg-slate-800 hover:bg-slate-900 text-white',
    desc: 'Full 10-year temporal series (2014–2024) containing 21 attributes: spatial grid indexes, NDWI, water occurrence, chemistry, and all 3 ML targets.',
    filename: 'indexed_waterbody_dataset.csv',
  },
  {
    type: 'wetland',
    title: 'Wetlands Indexed Dataset',
    subtitle: 'Marshes, Swamps & Floodplains',
    records: '154 records',
    wbCount: '14 water bodies',
    icon: '🌿',
    color: 'border-emerald-200 bg-emerald-50/40 hover:border-emerald-300',
    badge: 'Wetlands',
    badgeColor: 'bg-emerald-600 text-white',
    btnColor: 'bg-emerald-600 hover:bg-emerald-700 text-white',
    desc: 'High seasonality, variable occurrence %, critical carbon sinks and natural bio-filtration indicators across 10 annual timestamps.',
    filename: 'indexed_waterbody_dataset_wetland.csv',
  },
  {
    type: 'pond',
    title: 'Ponds Indexed Dataset',
    subtitle: 'Small Freshwater Bodies (< 0.05 km²)',
    records: '396 records',
    wbCount: '36 water bodies',
    icon: '🫧',
    color: 'border-cyan-200 bg-cyan-50/40 hover:border-cyan-300',
    badge: 'Ponds',
    badgeColor: 'bg-cyan-600 text-white',
    btnColor: 'bg-cyan-600 hover:bg-cyan-700 text-white',
    desc: 'Localized urban & rural micro-waterbodies susceptible to high eutrophication, algal blooms, and rapid seasonal evaporation.',
    filename: 'indexed_waterbody_dataset_pond.csv',
  },
  {
    type: 'river',
    title: 'Rivers Indexed Dataset',
    subtitle: 'Flowing Channels & Reaches',
    records: '176 records',
    wbCount: '16 water bodies',
    icon: '🏞️',
    color: 'border-teal-200 bg-teal-50/40 hover:border-teal-300',
    badge: 'Rivers',
    badgeColor: 'bg-teal-600 text-white',
    btnColor: 'bg-teal-600 hover:bg-teal-700 text-white',
    desc: 'Linear stream channels, river reaches, and estuaries characterized by dynamic turbidity gradients and continuous flow regimes.',
    filename: 'indexed_waterbody_dataset_river.csv',
  },
  {
    type: 'lake',
    title: 'Lakes Indexed Dataset',
    subtitle: 'Natural Perennial Water Bodies',
    records: '704 records',
    wbCount: '64 water bodies',
    icon: '🌊',
    color: 'border-blue-200 bg-blue-50/40 hover:border-blue-300',
    badge: 'Lakes',
    badgeColor: 'bg-blue-600 text-white',
    btnColor: 'bg-blue-600 hover:bg-blue-700 text-white',
    desc: 'HydroLAKES registry integration with depth estimates, broad surface areas, stable 12-month annual permanence, and multi-spectral NDWI.',
    filename: 'indexed_waterbody_dataset_lake.csv',
  },
  {
    type: 'reservoir',
    title: 'Reservoirs Indexed Dataset',
    subtitle: 'Anthropogenic Impoundments & Dams',
    records: '220 records',
    wbCount: '20 water bodies',
    icon: '🏗️',
    color: 'border-indigo-200 bg-indigo-50/40 hover:border-indigo-300',
    badge: 'Reservoirs',
    badgeColor: 'bg-indigo-600 text-white',
    btnColor: 'bg-indigo-600 hover:bg-indigo-700 text-white',
    desc: 'Regulated reservoirs demonstrating distinct management-driven level fluctuations, dam capacity trends, and controlled discharge.',
    filename: 'indexed_waterbody_dataset_reservoir.csv',
  },
]

// ─── Data Sources ────────────────────────────────────────────────────────────
const DATA_SOURCES = [
  {
    num: 1,
    name: 'HydroLAKES v1.0',
    org: 'McGill University & WWF',
    url: 'https://www.hydrosheds.org/products/hydrolakes',
    icon: Droplets,
    iconColor: 'text-blue-600',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    provides: [
      'Global lake/reservoir registry',
      'Lake name, lat/lon centroid',
      'Surface area (km²), shoreline length, depth',
      'Water body type classification',
    ],
    access: 'Downloaded via the public HydroSHEDS ArcGIS REST API',
    badge: 'REST API',
    badgeColor: 'bg-blue-100 text-blue-700',
  },
  {
    num: 2,
    name: 'JRC Global Surface Water',
    org: 'European Commission Joint Research Centre',
    url: 'https://global-surface-water.appspot.com/',
    icon: Satellite,
    iconColor: 'text-emerald-600',
    bgColor: 'bg-emerald-50',
    borderColor: 'border-emerald-200',
    provides: [
      '38 years of Landsat satellite observations',
      'Water occurrence % (JRC monthly history)',
      'Seasonality (months of water/year)',
      'Historical surface area changes (2014–2024)',
    ],
    access: 'Published research dataset (Pekel et al., Nature)',
    badge: 'Open Dataset',
    badgeColor: 'bg-emerald-100 text-emerald-700',
  },
  {
    num: 3,
    name: 'USGS Water Quality Portal',
    org: 'US Geological Survey & EPA',
    url: 'https://www.waterqualitydata.us/',
    icon: FlaskConical,
    iconColor: 'text-amber-600',
    bgColor: 'bg-amber-50',
    borderColor: 'border-amber-200',
    provides: [
      'Real in-situ lake monitoring data',
      'pH level measurements',
      'Dissolved Oxygen (DO mg/L)',
      'Turbidity (NTU) & Chlorophyll-a (µg/L)',
    ],
    access: 'Free REST API — /data/Result/search endpoint',
    badge: 'Free REST API',
    badgeColor: 'bg-amber-100 text-amber-700',
  },
  {
    num: 4,
    name: 'OpenStreetMap Nominatim',
    org: 'OpenStreetMap Foundation',
    url: 'https://nominatim.openstreetmap.org/',
    icon: Map,
    iconColor: 'text-violet-600',
    bgColor: 'bg-violet-50',
    borderColor: 'border-violet-200',
    provides: [
      'City-to-coordinate geocoding',
      'Converts city queries (e.g. "Kolkata", "Chicago") to lat/lon bounding boxes',
      'Powers the Explore page city search',
    ],
    access: 'Free Geocoding API — open access, no key needed',
    badge: 'Free Geocoding API',
    badgeColor: 'bg-violet-100 text-violet-700',
  },
]

const DataSourceCard = ({ source }) => {
  const Icon = source.icon
  return (
    <div className={`rounded-xl border ${source.borderColor} ${source.bgColor} p-4 flex flex-col gap-3`}>
      {/* Header */}
      <div className="flex items-start gap-3">
        <div className={`mt-0.5 ${source.iconColor} flex-shrink-0`}>
          <Icon className="w-5 h-5" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="text-xs font-bold text-slate-400">#{source.num}</span>
            <a
              href={source.url}
              target="_blank"
              rel="noopener noreferrer"
              className={`font-semibold text-sm ${source.iconColor} hover:underline flex items-center gap-1`}
            >
              {source.name}
              <ExternalLink className="w-3 h-3 inline opacity-60" />
            </a>
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${source.badgeColor}`}>
              {source.badge}
            </span>
          </div>
          <div className="text-xs text-slate-500 mt-0.5">{source.org}</div>
        </div>
      </div>

      {/* What it provides */}
      <div>
        <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">What It Provides</div>
        <ul className="space-y-1">
          {source.provides.map((item, i) => (
            <li key={i} className="text-xs text-slate-700 flex items-start gap-1.5">
              <span className={`mt-1 w-1.5 h-1.5 rounded-full flex-shrink-0 ${source.iconColor.replace('text-', 'bg-')}`} />
              {item}
            </li>
          ))}
        </ul>
      </div>

      {/* Access method */}
      <div className="text-xs text-slate-500 italic border-t border-slate-200 pt-2">
        📡 {source.access}
      </div>
    </div>
  )
}

const StatCard = ({ icon: Icon, label, value, sub, color = 'text-water-600' }) => (
  <div className="bg-white rounded-xl border border-slate-200 shadow p-4 flex items-start gap-3">
    <div className={`mt-0.5 ${color}`}><Icon className="w-5 h-5" /></div>
    <div>
      <div className="text-2xl font-bold text-slate-800">{value}</div>
      <div className="text-sm font-medium text-slate-600">{label}</div>
      {sub && <div className="text-xs text-slate-400 mt-0.5">{sub}</div>}
    </div>
  </div>
)

export default function Dashboard() {
  const navigate = useNavigate()
  const [headerDropdown, setHeaderDropdown] = useState(false)
  const headerMenuRef = useRef(null)

  useEffect(() => {
    function handleClickOutside(e) {
      if (headerMenuRef.current && !headerMenuRef.current.contains(e.target)) {
        setHeaderDropdown(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Load a global sample of water bodies for the world map
  const { data: wbs = [], isLoading } = useWaterBodies({ limit: 300 })

  // Build a latest-obs map from embedded observation data
  const obsMap = useMemo(() => {
    const m = {}
    wbs.forEach(wb => {
      if (wb.observations?.length) {
        const latest = [...wb.observations].sort((a, b) => b.observation_year - a.observation_year)[0]
        m[wb.id] = latest
      }
    })
    return m
  }, [wbs])

  // Stats
  const stats = useMemo(() => {
    const qualityCounts = { excellent: 0, good: 0, fair: 0, poor: 0, critical: 0 }
    Object.values(obsMap).forEach(o => {
      if (o?.water_quality_status) qualityCounts[o.water_quality_status]++
    })
    return {
      total: wbs.length,
      countries: new Set(wbs.map(w => w.country)).size,
      atRisk: (qualityCounts.poor + qualityCounts.critical),
      qualityCounts,
    }
  }, [wbs, obsMap])

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Global Water Body Dashboard</h1>
          <p className="text-slate-500 text-sm mt-1">
            5–10 year temporal dataset · Real data from HydroLAKES, USGS WQP &amp; JRC GSW
          </p>
        </div>

        {/* ── Header Export Dropdown ── */}
        <div className="relative self-start sm:self-auto" ref={headerMenuRef}>
          <button
            onClick={() => setHeaderDropdown(v => !v)}
            className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-sm px-4 py-2.5 rounded-xl shadow transition-colors"
          >
            <Download className="w-4 h-4" />
            <span>Extract Indexed Dataset (.CSV)</span>
            <ChevronDown className="w-4 h-4 opacity-80" />
          </button>

          {headerDropdown && (
            <div className="absolute right-0 mt-2 w-72 bg-white border border-slate-200 rounded-xl shadow-xl py-2 z-[9999] text-slate-800">
              <div className="px-3 py-1.5 border-b border-slate-100">
                <div className="text-xs font-bold text-slate-700 uppercase tracking-wide">
                  Select Indexed Dataset
                </div>
                <div className="text-[11px] text-slate-400">
                  Partitioned by water body morphology
                </div>
              </div>
              <div className="py-1">
                {PARTITION_CARDS.map(p => (
                  <a
                    key={p.type}
                    href={getExportDatasetUrl(p.type)}
                    download={p.filename}
                    onClick={() => setHeaderDropdown(false)}
                    className="flex items-center justify-between px-3 py-2 text-xs hover:bg-emerald-50 transition-colors"
                  >
                    <span className="flex items-center gap-2 font-medium text-slate-700">
                      <span>{p.icon}</span>
                      <span>{p.title.replace(' Indexed Dataset', '')}</span>
                    </span>
                    <span className="text-[11px] font-mono text-emerald-700 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded">
                      {p.records}
                    </span>
                  </a>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={Droplets} label="Water Bodies Loaded" value={isLoading ? '…' : stats.total.toLocaleString()} sub="From HydroLAKES global dataset" />
        <StatCard icon={Globe} label="Countries" value={isLoading ? '…' : stats.countries} sub="Worldwide coverage" color="text-emerald-600" />
        <StatCard icon={TrendingDown} label="At Risk" value={isLoading ? '…' : stats.atRisk} sub="Poor or critical quality" color="text-amber-600" />
        <StatCard icon={AlertTriangle} label="Data Years" value="2014–2024" sub="10-year temporal coverage" color="text-purple-600" />
      </div>

      {/* Quality legend */}
      <div className="bg-white border border-slate-200 rounded-xl shadow p-4">
        <div className="text-xs font-semibold text-slate-500 mb-3 uppercase tracking-wide">Map Legend — Water Quality</div>
        <div className="flex flex-wrap gap-4 text-xs">
          {[
            { label: 'Excellent', color: '#22c55e' },
            { label: 'Good',      color: '#84cc16' },
            { label: 'Fair',      color: '#f59e0b' },
            { label: 'Poor',      color: '#ef4444' },
            { label: 'Critical',  color: '#7f1d1d' },
          ].map(({ label, color }) => (
            <div key={label} className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full inline-block" style={{ background: color }} />
              <span className="text-slate-600">{label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* World map */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <h2 className="font-semibold text-slate-700">Global Water Bodies Map</h2>
          <button
            onClick={() => navigate('/explore')}
            className="text-xs text-water-600 hover:text-water-800 font-medium"
          >
            Search a specific city →
          </button>
        </div>
        <WaterBodyMap
          waterBodies={wbs}
          observations={obsMap}
          height="480px"
          center={[20, 10]}
          zoom={2}
          onSelectWaterBody={wb => navigate(`/explore?wb=${wb.id}`)}
        />
      </div>

      {/* ── Data Sources ───────────────────────────────────────────────────── */}
      <div className="bg-white border border-slate-200 rounded-xl shadow p-5">
        <div className="flex items-center gap-2 mb-4">
          <Database className="w-4 h-4 text-slate-500" />
          <h2 className="font-semibold text-slate-700">Data Sources</h2>
          <span className="ml-auto text-xs text-slate-400">4 open datasets integrated</span>
        </div>

        {/* Table header (desktop only) */}
        <div className="hidden lg:grid lg:grid-cols-4 gap-3 mb-2 px-1">
          {['Source', 'Organization', 'What It Provides', 'How We Access It'].map(h => (
            <div key={h} className="text-xs font-bold text-slate-500 uppercase tracking-wide">{h}</div>
          ))}
        </div>

        {/* Mobile cards / Desktop rows */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {DATA_SOURCES.map(src => (
            <DataSourceCard key={src.num} source={src} />
          ))}
        </div>

        <p className="text-xs text-slate-400 mt-4 text-center">
          All data is processed, indexed, and stored in the local CSV dataset (1,650 records · 150 water bodies · 2014–2024)
        </p>
      </div>

      {/* ── Indexed Dataset Extraction Hub (By Water Body Type) ────────────── */}
      <div className="bg-white border border-slate-200 rounded-xl shadow p-5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <FileSpreadsheet className="w-5 h-5 text-emerald-600" />
            <div>
              <h2 className="font-semibold text-slate-800">
                Indexed Datasets — Download by Water Body Type
              </h2>
              <p className="text-xs text-slate-500">
                Extract subsets indexed by morphology (wetlands, ponds, rivers, lakes, reservoirs) or full master
              </p>
            </div>
          </div>
          <span className="hidden sm:inline-block text-xs bg-emerald-50 text-emerald-700 font-semibold px-2.5 py-1 rounded-full border border-emerald-200">
            6 CSV Partitions Available
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {PARTITION_CARDS.map(card => (
            <div
              key={card.type}
              className={`rounded-xl border p-4 flex flex-col justify-between transition-all hover:shadow-md ${card.color}`}
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">{card.icon}</span>
                    <div>
                      <h3 className="font-semibold text-sm text-slate-800">{card.title}</h3>
                      <p className="text-xs text-slate-500">{card.subtitle}</p>
                    </div>
                  </div>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${card.badgeColor}`}>
                    {card.badge}
                  </span>
                </div>

                <p className="text-xs text-slate-600 leading-relaxed my-3">
                  {card.desc}
                </p>

                <div className="flex items-center gap-3 text-xs text-slate-500 mb-4 bg-white/70 rounded-lg p-2 border border-slate-200/60">
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase">Records</span>
                    <strong className="text-slate-700">{card.records}</strong>
                  </div>
                  <div className="border-l border-slate-200 pl-3">
                    <span className="text-slate-400 block text-[10px] uppercase">Entities</span>
                    <strong className="text-slate-700">{card.wbCount}</strong>
                  </div>
                  <div className="border-l border-slate-200 pl-3">
                    <span className="text-slate-400 block text-[10px] uppercase">Span</span>
                    <strong className="text-slate-700">2014–2024</strong>
                  </div>
                </div>
              </div>

              <a
                href={getExportDatasetUrl(card.type)}
                download={card.filename}
                className={`flex items-center justify-center gap-2 font-medium text-xs py-2 px-3 rounded-lg shadow-sm transition-colors ${card.btnColor}`}
              >
                <Download className="w-3.5 h-3.5" />
                <span>Download {card.filename}</span>
              </a>
            </div>
          ))}
        </div>
      </div>

      {/* ── ML Pipeline Summary ────────────────────────────────────────────── */}
      <div className="bg-gradient-to-r from-water-50 to-blue-50 border border-water-200 rounded-xl p-5">
        <h2 className="font-semibold text-slate-700 mb-3 flex items-center gap-2">
          <span className="text-lg">🤖</span> ML Pipeline — 3 Trained Models
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {[
            {
              task: 'Task 1',
              title: 'Water Body Type Classification',
              desc: 'Classifies a water body as Lake, Pond, Reservoir, Wetland, or River based on area, NDWI, and depth features.',
              accuracy: '90%',
              color: 'bg-blue-600',
            },
            {
              task: 'Task 2',
              title: 'Water Quality Classification',
              desc: 'Classifies water quality as Excellent / Good / Fair / Poor / Critical using pH, DO, turbidity, and chlorophyll-a.',
              accuracy: '94%',
              color: 'bg-emerald-600',
            },
            {
              task: 'Task 3',
              title: 'Future Change Prediction',
              desc: 'Predicts whether a water body will Expand, Stay Stable, Shrink, or Disappear over the next 10 years.',
              accuracy: 'Per-WB',
              color: 'bg-violet-600',
            },
          ].map(m => (
            <div key={m.task} className="bg-white rounded-lg border border-slate-200 p-3 shadow-sm">
              <div className="flex items-center gap-2 mb-1.5">
                <span className={`text-white text-xs font-bold px-2 py-0.5 rounded-full ${m.color}`}>{m.task}</span>
                <span className="text-xs text-slate-400 font-mono">{m.accuracy} accuracy</span>
              </div>
              <div className="text-sm font-semibold text-slate-700 mb-1">{m.title}</div>
              <div className="text-xs text-slate-500 leading-relaxed">{m.desc}</div>
            </div>
          ))}
        </div>
        <p className="text-xs text-slate-400 mt-3 text-center">
          Try the models on the <button onClick={() => navigate('/explore')} className="text-water-600 hover:underline font-medium">Explore page</button> → select any water body → Classification Panel
        </p>
      </div>
    </div>
  )
}

