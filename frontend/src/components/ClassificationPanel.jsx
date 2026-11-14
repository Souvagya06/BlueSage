/**
 * ClassificationPanel.jsx
 * Multi-Task ML Classification Panel:
 *   - Task 1: Water-Body Type (Pond, Lake, Reservoir, Wetland, River)
 *   - Task 2: Water Quality (Excellent, Good, Fair, Poor, Critical)
 */
import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { classifyWaterBody, classifyWaterBodyType } from '../api/client'
import { Cpu, Tag, ChevronDown, ChevronUp } from 'lucide-react'
import clsx from 'clsx'

const QUALITY_STYLES = {
  excellent: 'bg-green-100 text-green-800 border-green-200',
  good:      'bg-lime-100 text-lime-800 border-lime-200',
  fair:      'bg-amber-100 text-amber-800 border-amber-200',
  poor:      'bg-red-100 text-red-800 border-red-200',
  critical:  'bg-red-900 text-white border-red-900',
}

const TYPE_STYLES = {
  lake:      'bg-blue-100 text-blue-800 border-blue-200',
  pond:      'bg-cyan-100 text-cyan-800 border-cyan-200',
  reservoir: 'bg-indigo-100 text-indigo-800 border-indigo-200',
  wetland:   'bg-emerald-100 text-emerald-800 border-emerald-200',
  river:     'bg-teal-100 text-teal-800 border-teal-200',
}

// Fixed display orders — never re-sort by probability
const QUALITY_ORDER = ['excellent', 'good', 'fair', 'poor', 'critical']
const TYPE_ORDER    = ['wetland', 'pond', 'river', 'lake', 'reservoir']

export default function ClassificationPanel({ waterBody, latestObs }) {
  const [activeTab, setActiveTab] = useState('type') // 'type' | 'quality'  — Task 1 is default
  const [showProbs, setShowProbs] = useState(false)

  // Quality Mutation
  const qualityMutation = useMutation({
    mutationFn: classifyWaterBody,
  })

  // Body Type Mutation
  const typeMutation = useMutation({
    mutationFn: classifyWaterBodyType,
  })

  const handleClassifyQuality = () => {
    if (!waterBody || !latestObs) return
    qualityMutation.mutate({
      ndwi: latestObs.ndwi ?? 0.3,
      area_sq_km: latestObs.area_sq_km ?? 1.0,
      water_body_type: waterBody.water_body_type,
      water_occurrence_pct: latestObs.water_occurrence_pct,
      seasonality_months: latestObs.seasonality_months,
      turbidity_ntu: latestObs.turbidity_ntu,
      ph: latestObs.ph,
      dissolved_oxygen_mgl: latestObs.dissolved_oxygen_mgl,
      chlorophyll_a_ugl: latestObs.chlorophyll_a_ugl,
    })
  }

  const handleClassifyType = () => {
    if (!waterBody) return
    typeMutation.mutate({
      name: waterBody.name,
      area_sq_km: latestObs?.area_sq_km ?? waterBody.area_sq_km ?? 1.0,
      perimeter_km: waterBody.perimeter_km ?? latestObs?.perimeter_km,
      elongation_ratio: waterBody.elongation_ratio ?? latestObs?.elongation_ratio,
      water_occurrence_pct: latestObs?.water_occurrence_pct ?? 85.0,
      seasonality_months: latestObs?.seasonality_months ?? 10,
      ndwi: latestObs?.ndwi ?? 0.4,
      turbidity_ntu: latestObs?.turbidity_ntu,
    })
  }

  const qualResult = qualityMutation.data
  const qualStatus = qualResult?.predicted_quality_status

  const typeResult = typeMutation.data
  const typeStatus = typeResult?.predicted_water_body_type

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow p-4">
      {/* Header Tabs */}
      <div className="flex items-center justify-between border-b border-slate-100 pb-2 mb-3">
        <div className="flex gap-1">
          <button
            onClick={() => setActiveTab('type')}
            className={clsx(
              'flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold transition-colors',
              activeTab === 'type'
                ? 'bg-water-600 text-white shadow-sm'
                : 'text-slate-500 hover:bg-slate-100'
            )}
          >
            <Tag className="w-3.5 h-3.5" />
            <span>Task 1: Body Type</span>
          </button>
          <button
            onClick={() => setActiveTab('quality')}
            className={clsx(
              'flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold transition-colors',
              activeTab === 'quality'
                ? 'bg-water-600 text-white shadow-sm'
                : 'text-slate-500 hover:bg-slate-100'
            )}
          >
            <Cpu className="w-3.5 h-3.5" />
            <span>Task 2: Quality</span>
          </button>
        </div>
      </div>

      {!waterBody ? (
        <p className="text-xs text-slate-400">Select a water body from the map or table.</p>
      ) : (
        <>
          <div className="text-xs text-slate-500 mb-3">
            Target: <strong className="text-slate-700">{waterBody.name}</strong>
            {latestObs && ` (${latestObs.observation_year} data)`}
          </div>

          {/* TAB 1: QUALITY CLASSIFIER */}
          {activeTab === 'quality' && (
            <div>
              <button
                onClick={handleClassifyQuality}
                disabled={qualityMutation.isPending || !latestObs}
                className="w-full bg-water-600 text-white text-xs py-2 rounded-lg hover:bg-water-700 disabled:opacity-50 transition-colors font-medium shadow-sm"
              >
                {qualityMutation.isPending ? 'Classifying...' : '🔬 Run ML Quality Classification'}
              </button>

              {qualityMutation.isError && (
                <div className="mt-2 text-xs text-red-600 bg-red-50 rounded p-2">
                  Classification failed.
                </div>
              )}

              {qualResult && (
                <div className="mt-3 space-y-2">
                  <div className={clsx('border rounded-lg px-3 py-2 flex items-center justify-between', QUALITY_STYLES[qualStatus])}>
                    <span className="font-semibold capitalize text-sm">{qualStatus} Quality</span>
                    <span className="text-xs font-medium opacity-90">
                      {(qualResult.confidence * 100).toFixed(1)}% confidence
                    </span>
                  </div>

                  <button
                    onClick={() => setShowProbs(s => !s)}
                    className="flex items-center gap-1 text-xs text-slate-400 hover:text-slate-600 pt-1"
                  >
                    Class probabilities {showProbs ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                  </button>

                  {showProbs && qualResult.class_probabilities && (
                    <div className="space-y-1.5 pt-1">
                      {QUALITY_ORDER.map(cls => {
                        const prob = qualResult.class_probabilities[cls] ?? 0
                        return (
                          <div key={cls} className="flex items-center gap-2">
                            <span className="text-xs text-slate-500 w-16 capitalize">{cls}</span>
                            <div className="flex-1 bg-slate-100 rounded-full h-1.5">
                              <div
                                className="bg-water-500 h-1.5 rounded-full transition-all duration-500"
                                style={{ width: `${(prob * 100).toFixed(1)}%` }}
                              />
                            </div>
                            <span className="text-xs text-slate-400 w-10 text-right">
                              {(prob * 100).toFixed(0)}%
                            </span>
                          </div>
                        )
                      })}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* TAB 2: WATER BODY TYPE CLASSIFIER */}
          {activeTab === 'type' && (
            <div>
              <button
                onClick={handleClassifyType}
                disabled={typeMutation.isPending}
                className="w-full bg-water-600 text-white text-xs py-2 rounded-lg hover:bg-water-700 disabled:opacity-50 transition-colors font-medium shadow-sm"
              >
                {typeMutation.isPending ? 'Classifying...' : '🏷️ Run ML Type Classification'}
              </button>

              {typeResult && (
                <div className="mt-3 space-y-2">
                  <div className={clsx('border rounded-lg px-3 py-2 flex items-center justify-between', TYPE_STYLES[typeStatus] || 'bg-slate-100')}>
                    <span className="font-semibold capitalize text-sm">{typeStatus}</span>
                    <span className="text-xs font-medium opacity-90">
                      {(typeResult.confidence * 100).toFixed(1)}% confidence
                    </span>
                  </div>

                  <div className="text-xs text-slate-400 pt-1">Model: {typeResult.model_used || 'RandomForest'}</div>

                  {typeResult.type_probabilities && (
                    <div className="space-y-1.5 pt-1">
                      {TYPE_ORDER.map(t => {
                        const prob = typeResult.type_probabilities[t] ?? 0
                        return (
                          <div key={t} className="flex items-center gap-2">
                            <span className="text-xs text-slate-500 w-16 capitalize">{t}</span>
                            <div className="flex-1 bg-slate-100 rounded-full h-1.5">
                              <div
                                className="bg-water-500 h-1.5 rounded-full transition-all duration-500"
                                style={{ width: `${(prob * 100).toFixed(1)}%` }}
                              />
                            </div>
                            <span className="text-xs text-slate-400 w-10 text-right">
                              {(prob * 100).toFixed(0)}%
                            </span>
                          </div>
                        )
                      })}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}
