/**
 * WaterBodyTable.jsx
 * Sortable, paginated table of water bodies with quality badges.
 */
import { useState } from 'react'
import clsx from 'clsx'

const QUALITY_STYLES = {
  excellent: 'bg-green-100 text-green-800',
  good:      'bg-lime-100 text-lime-800',
  fair:      'bg-amber-100 text-amber-800',
  poor:      'bg-red-100 text-red-800',
  critical:  'bg-red-900 text-white',
}

export default function WaterBodyTable({ waterBodies = [], observations = {}, onSelect }) {
  const [sortKey, setSortKey] = useState('name')
  const [sortAsc, setSortAsc] = useState(true)
  const [page, setPage] = useState(0)
  const PAGE_SIZE = 15

  const handleSort = (key) => {
    if (sortKey === key) setSortAsc(a => !a)
    else { setSortKey(key); setSortAsc(true) }
  }

  const sorted = [...waterBodies].sort((a, b) => {
    let av = a[sortKey] ?? ''
    let bv = b[sortKey] ?? ''
    if (typeof av === 'string') av = av.toLowerCase()
    if (typeof bv === 'string') bv = bv.toLowerCase()
    return sortAsc ? (av > bv ? 1 : -1) : (av < bv ? 1 : -1)
  })

  const page_data = sorted.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE)
  const total_pages = Math.ceil(sorted.length / PAGE_SIZE)

  const TH = ({ label, sortable, sk }) => (
    <th
      className={clsx(
        'px-3 py-2 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide whitespace-nowrap',
        sortable && 'cursor-pointer hover:text-slate-800 select-none'
      )}
      onClick={() => sortable && handleSort(sk)}
    >
      {label}
      {sortKey === sk && <span className="ml-1">{sortAsc ? '↑' : '↓'}</span>}
    </th>
  )

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <TH label="Name" sortable sk="name" />
              <TH label="Type" sortable sk="water_body_type" />
              <TH label="Country" sortable sk="country" />
              <TH label="Quality" />
              <TH label="NDWI" />
              <TH label="Area km²" />
              <TH label="" />
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {page_data.length === 0 && (
              <tr>
                <td colSpan={7} className="text-center text-slate-400 py-8 text-sm">
                  No water bodies found. Search for a city on the map.
                </td>
              </tr>
            )}
            {page_data.map(wb => {
              const obs = observations[wb.id]
              const quality = obs?.water_quality_status
              return (
                <tr
                  key={wb.id}
                  className="hover:bg-water-50 cursor-pointer transition-colors"
                  onClick={() => onSelect && onSelect(wb)}
                >
                  <td className="px-3 py-2 font-medium text-slate-800 max-w-[180px] truncate">{wb.name}</td>
                  <td className="px-3 py-2 text-slate-500 capitalize">{wb.water_body_type}</td>
                  <td className="px-3 py-2 text-slate-500">{wb.country}</td>
                  <td className="px-3 py-2">
                    {quality ? (
                      <span className={clsx('px-2 py-0.5 rounded-full text-xs font-medium capitalize', QUALITY_STYLES[quality])}>
                        {quality}
                      </span>
                    ) : <span className="text-slate-300 text-xs">—</span>}
                  </td>
                  <td className="px-3 py-2 text-slate-600">{obs?.ndwi?.toFixed(3) ?? '—'}</td>
                  <td className="px-3 py-2 text-slate-600">{obs?.area_sq_km?.toFixed(2) ?? '—'}</td>
                  <td className="px-3 py-2">
                    <button className="text-water-600 hover:text-water-800 text-xs font-medium">Details →</button>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {total_pages > 1 && (
        <div className="flex items-center justify-between px-4 py-2 border-t border-slate-100 bg-slate-50">
          <span className="text-xs text-slate-400">{waterBodies.length} total</span>
          <div className="flex gap-1">
            <button
              onClick={() => setPage(p => Math.max(0, p - 1))}
              disabled={page === 0}
              className="px-2 py-1 text-xs rounded border border-slate-200 disabled:opacity-40 hover:bg-white"
            >← Prev</button>
            <span className="px-2 py-1 text-xs text-slate-500">{page + 1} / {total_pages}</span>
            <button
              onClick={() => setPage(p => Math.min(total_pages - 1, p + 1))}
              disabled={page >= total_pages - 1}
              className="px-2 py-1 text-xs rounded border border-slate-200 disabled:opacity-40 hover:bg-white"
            >Next →</button>
          </div>
        </div>
      )}
    </div>
  )
}

