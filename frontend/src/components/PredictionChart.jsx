/**
 * PredictionChart.jsx
 * Shows historical observations + ML future predictions as a combined line chart.
 */
import {
  ResponsiveContainer, ComposedChart, Line, Area, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend, ReferenceLine
} from 'recharts'

const CURRENT_YEAR = new Date().getFullYear()

function mergeData(observations = [], predictions = []) {
  const map = {}

  observations.forEach(o => {
    map[o.observation_year] = {
      year: o.observation_year,
      ndwi: o.ndwi,
      area: o.area_sq_km,
      quality: o.water_quality_score,
      type: 'historical',
    }
  })

  predictions.forEach(p => {
    map[p.target_year] = {
      year: p.target_year,
      predicted_ndwi: p.predicted_ndwi,
      predicted_area: p.predicted_area_sq_km,
      predicted_quality: p.predicted_quality_score,
      confidence: p.confidence_score,
      type: 'prediction',
    }
  })

  return Object.values(map).sort((a, b) => a.year - b.year)
}

export default function PredictionChart({ observations = [], predictions = [], metric = 'ndwi' }) {
  const data = mergeData(observations, predictions)

  const metricConfig = {
    ndwi: {
      histKey: 'ndwi',
      predKey: 'predicted_ndwi',
      label: 'NDWI',
      domain: [-1, 1],
      color: '#3b97f6',
      predColor: '#f59e0b',
      unit: '',
    },
    area: {
      histKey: 'area',
      predKey: 'predicted_area',
      label: 'Area (km²)',
      domain: ['auto', 'auto'],
      color: '#22c55e',
      predColor: '#f59e0b',
      unit: ' km²',
    },
    quality: {
      histKey: 'quality',
      predKey: 'predicted_quality',
      label: 'Quality Score',
      domain: [0, 100],
      color: '#8b5cf6',
      predColor: '#f59e0b',
      unit: '/100',
    },
  }

  const cfg = metricConfig[metric] || metricConfig.ndwi

  const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null
    const isPred = label > CURRENT_YEAR
    return (
      <div className="bg-white border border-slate-200 rounded-lg shadow-lg p-3 text-sm">
        <div className="font-semibold text-slate-700 mb-1">
          {label} {isPred ? '🔮 Predicted' : '📊 Historical'}
        </div>
        {payload.map((p, i) => (
          <div key={i} className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full" style={{ background: p.color }} />
            <span className="text-slate-600">{p.name}:</span>
            <span className="font-medium">{typeof p.value === 'number' ? p.value.toFixed(3) : p.value}{cfg.unit}</span>
          </div>
        ))}
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <ComposedChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="year" tick={{ fontSize: 11 }} />
        <YAxis domain={cfg.domain} tick={{ fontSize: 11 }} />
        <Tooltip content={<CustomTooltip />} />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <ReferenceLine x={CURRENT_YEAR} stroke="#94a3b8" strokeDasharray="4 4" label={{ value: 'Now', fontSize: 10 }} />

        {/* Historical line */}
        <Line
          type="monotone"
          dataKey={cfg.histKey}
          name={`${cfg.label} (Historical)`}
          stroke={cfg.color}
          strokeWidth={2.5}
          dot={{ r: 3 }}
          connectNulls
        />

        {/* Predicted line */}
        <Line
          type="monotone"
          dataKey={cfg.predKey}
          name={`${cfg.label} (Predicted)`}
          stroke={cfg.predColor}
          strokeWidth={2}
          strokeDasharray="5 3"
          dot={{ r: 3 }}
          connectNulls
        />
      </ComposedChart>
    </ResponsiveContainer>
  )
}

