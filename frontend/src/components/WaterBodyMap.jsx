/**
 * WaterBodyMap.jsx
 * Interactive Leaflet map with multiple tile layers, colored markers, and popups.
 * Tile layers: Street (OSM), Satellite (Esri), Terrain (Stadia), Dark (CartoDB)
 */
import { MapContainer, TileLayer, CircleMarker, Popup, useMap, LayersControl } from 'react-leaflet'
import { useEffect } from 'react'

const { BaseLayer } = LayersControl

const QUALITY_COLOR = {
  excellent: '#22c55e',
  good:      '#84cc16',
  fair:      '#f59e0b',
  poor:      '#ef4444',
  critical:  '#7f1d1d',
  unknown:   '#94a3b8',
}

const QUALITY_LABEL = {
  excellent: 'Excellent',
  good:      'Good',
  fair:      'Fair',
  poor:      'Poor',
  critical:  'Critical',
}

/** Fly map to a new center when props change */
function FlyToHandler({ center, zoom }) {
  const map = useMap()
  useEffect(() => {
    if (center) map.flyTo(center, zoom || map.getZoom(), { duration: 1.2 })
  }, [center, zoom, map])
  return null
}

function WaterBodyPopup({ wb, latestObs, onSelect }) {
  const quality = latestObs?.water_quality_status || 'unknown'
  const color = QUALITY_COLOR[quality]
  return (
    <div style={{ padding: '10px', minWidth: '200px' }}>
      <div style={{ fontWeight: 600, fontSize: '13px', marginBottom: '4px', color: '#1e293b' }}>{wb.name}</div>
      <div style={{ fontSize: '11px', color: '#64748b', marginBottom: '8px', textTransform: 'capitalize' }}>
        {wb.water_body_type} · {wb.country}
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
        <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: color, display: 'inline-block' }} />
        <span style={{ fontSize: '11px', fontWeight: 500, color }}>{QUALITY_LABEL[quality] || 'Unknown'}</span>
      </div>
      {latestObs && (
        <div style={{ fontSize: '11px', color: '#475569', lineHeight: '1.6' }}>
          <div>Area: <strong>{latestObs.area_sq_km?.toFixed(2)} km²</strong></div>
          <div>NDWI: <strong>{latestObs.ndwi?.toFixed(3)}</strong></div>
          {latestObs.ph && <div>pH: <strong>{latestObs.ph?.toFixed(1)}</strong></div>}
          {latestObs.observation_year && <div>Year: <strong>{latestObs.observation_year}</strong></div>}
        </div>
      )}
      <button
        onClick={() => onSelect && onSelect(wb)}
        style={{
          marginTop: '8px',
          width: '100%',
          fontSize: '12px',
          background: '#2563eb',
          color: 'white',
          border: 'none',
          borderRadius: '6px',
          padding: '5px 8px',
          cursor: 'pointer',
          fontWeight: 500,
        }}
      >
        View Details →
      </button>
    </div>
  )
}

// ── Tile layer definitions — all 100% free, no API key needed ────────────────
const TILE_LAYERS = [
  {
    name: '🗺️ Street (OSM)',
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '',
    checked: true,
  },
  {
    name: '🛰️ Satellite (Esri)',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution: '',
    checked: false,
  },
  {
    name: '🏔️ Terrain (OpenTopo)',
    url: 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
    attribution: '',
    checked: false,
  },
  {
    name: '🌙 Dark (CartoDB)',
    url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    attribution: '',
    checked: false,
  },
  {
    name: '🤍 Light (CartoDB)',
    url: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
    attribution: '',
    checked: false,
  },
]

export default function WaterBodyMap({
  waterBodies = [],
  observations = {},
  center = [20, 0],
  zoom = 3,
  flyTo = null,
  selectedId = null,
  onSelectWaterBody,
  height = '100%',
}) {
  return (
    <div style={{ height, borderRadius: '12px', overflow: 'hidden', border: '1px solid #e2e8f0', boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
      <MapContainer center={center} zoom={zoom} style={{ height: '100%', width: '100%' }} zoomControl={true} attributionControl={false}>

        {/* ── Tile Layer Switcher ─────────────────────────────────────── */}
        <LayersControl position="topright">
          {TILE_LAYERS.map(layer => (
            <BaseLayer key={layer.name} checked={layer.checked} name={layer.name}>
              <TileLayer
                attribution={layer.attribution}
                url={layer.url}
                maxZoom={19}
              />
            </BaseLayer>
          ))}
        </LayersControl>

        {flyTo && <FlyToHandler center={flyTo.center} zoom={flyTo.zoom} />}

        {/* ── Water body markers ─────────────────────────────────────── */}
        {waterBodies.map((wb) => {
          if (!wb.latitude || !wb.longitude) return null
          const obs = observations[wb.id]
          const quality = obs?.water_quality_status || 'unknown'
          const color = QUALITY_COLOR[quality]
          const isSelected = wb.id === selectedId

          return (
            <CircleMarker
              key={wb.id}
              center={[wb.latitude, wb.longitude]}
              radius={isSelected ? 12 : 8}
              pathOptions={{
                color: isSelected ? '#1e3a8a' : color,
                fillColor: color,
                fillOpacity: isSelected ? 0.95 : 0.8,
                weight: isSelected ? 3 : 1.5,
              }}
              eventHandlers={{
                // Select water body immediately on marker click — no need to press the popup button
                click: () => onSelectWaterBody && onSelectWaterBody(wb),
              }}
            >
              <Popup>
                <WaterBodyPopup
                  wb={wb}
                  latestObs={obs}
                  onSelect={onSelectWaterBody}
                />
              </Popup>
            </CircleMarker>
          )
        })}
      </MapContainer>
    </div>
  )
}
