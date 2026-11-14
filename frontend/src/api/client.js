import axios from 'axios'

const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: BASE,
  timeout: 30000,
})

// ── Water Bodies ──────────────────────────────────────────────
export const fetchWaterBodies = (params = {}) =>
  api.get('/api/waterbodies/', { params }).then(r => r.data)

export const fetchWaterBodyById = (id) =>
  api.get(`/api/waterbodies/${id}`).then(r => r.data)

export const fetchWaterBodiesNear = ({ lat, lon, radius_km = 200, limit = 150 }) =>
  api.get('/api/waterbodies/near', { params: { lat, lon, radius_km, limit } }).then(r => r.data)

export const fetchWaterBodiesInBbox = ({ min_lat, max_lat, min_lon, max_lon, limit = 200 }) =>
  api.get('/api/waterbodies/bbox', { params: { min_lat, max_lat, min_lon, max_lon, limit } }).then(r => r.data)

export const fetchObservations = (id, params = {}) =>
  api.get(`/api/waterbodies/${id}/observations`, { params }).then(r => r.data)

// ── Geocoding (Nominatim — free, no key) ─────────────────────
export const geocodeCity = async (query) => {
  const r = await axios.get('https://nominatim.openstreetmap.org/search', {
    params: { q: query, format: 'json', limit: 5, addressdetails: 1 },
    headers: { 'User-Agent': 'BlueSage-App/1.0' },
  })
  return r.data
}

// ── Classification ────────────────────────────────────────────
export const classifyWaterBody = (payload) =>
  api.post('/api/classify/', payload).then(r => r.data)

export const classifyWaterBodyType = (payload) =>
  api.post('/api/classify/body-type', payload).then(r => r.data)

export const getExportDatasetUrl = (type = null) => {
  if (type && type !== 'all') {
    return `${BASE}/api/waterbodies/export-csv?water_body_type=${encodeURIComponent(type)}`
  }
  return `${BASE}/api/waterbodies/export-csv`
}

export const fetchIndexedDatasetsInfo = () =>
  api.get('/api/waterbodies/indexed-datasets').then(r => r.data)

// ── Prediction ────────────────────────────────────────────────
export const fetchPrediction = (id, years_ahead = 10) =>
  api.get(`/api/predict/${id}`, { params: { years_ahead } }).then(r => r.data)

export default api

