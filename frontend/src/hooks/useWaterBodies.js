import { useQuery } from '@tanstack/react-query'
import {
  fetchWaterBodies, fetchWaterBodyById, fetchWaterBodiesNear,
  fetchWaterBodiesInBbox, fetchObservations, fetchPrediction
} from '../api/client'

export const useWaterBodies = (params = {}) =>
  useQuery({
    queryKey: ['waterbodies', params],
    queryFn: () => fetchWaterBodies(params),
    enabled: Object.keys(params).length > 0 || true,
  })

export const useWaterBodyById = (id) =>
  useQuery({
    queryKey: ['waterbody', id],
    queryFn: () => fetchWaterBodyById(id),
    enabled: !!id,
  })

export const useWaterBodiesNear = ({ lat, lon, radius_km }, enabled = true) =>
  useQuery({
    queryKey: ['waterbodies-near', lat, lon, radius_km],
    queryFn: () => fetchWaterBodiesNear({ lat, lon, radius_km }),
    enabled: enabled && lat != null && lon != null,
  })

export const useWaterBodiesInBbox = (bbox, enabled = true) =>
  useQuery({
    queryKey: ['waterbodies-bbox', bbox],
    queryFn: () => fetchWaterBodiesInBbox(bbox),
    enabled: enabled && !!bbox,
  })

export const useObservations = (id, params = {}) =>
  useQuery({
    queryKey: ['observations', id, params],
    queryFn: () => fetchObservations(id, params),
    enabled: !!id,
  })

export const usePrediction = (id, years_ahead = 10) =>
  useQuery({
    queryKey: ['prediction', id, years_ahead],
    queryFn: () => fetchPrediction(id, years_ahead),
    enabled: !!id,
  })

