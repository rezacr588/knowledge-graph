import { useCallback, useEffect, useMemo, useState } from 'react'
import { Database, RefreshCw, AlertTriangle, Filter } from 'lucide-react'

const limitOptions = [50, 100, 200, 500, 1000]
const languageOptions = [
  { value: 'all', label: 'All Languages' },
  { value: 'en', label: 'English' },
  { value: 'ar', label: 'Arabic (العربية)' },
  { value: 'es', label: 'Spanish (Español)' }
]
const sourceOptions = [
  { value: 'auto', label: 'Combined (Qdrant + Persisted)' },
  { value: 'qdrant', label: 'Qdrant only' },
  { value: 'store', label: 'Persisted store only' }
]

const StoredChunks = () => {
  const [chunks, setChunks] = useState([])
  const [stats, setStats] = useState(null)
  const [limit, setLimit] = useState(limitOptions[2])
  const [language, setLanguage] = useState('all')
  const [source, setSource] = useState('auto')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const queryParams = useMemo(() => {
    const params = new URLSearchParams({ limit: String(limit), source })
    if (language !== 'all') {
      params.set('language', language)
    }
    return params.toString()
  }, [limit, language, source])

  const fetchChunks = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`/api/chunks?${queryParams}`)
      if (!response.ok) {
        const payload = await response.json().catch(() => ({}))
        const detail = payload?.detail || `Request failed with status ${response.status}`
        throw new Error(detail)
      }

      const data = await response.json()
      setChunks(data?.chunks ?? [])
      setStats({
        returned: data?.returned ?? 0,
        limit: data?.limit ?? limit,
        language: data?.language ?? language,
        source: data?.source ?? source,
        sourceCounts: data?.source_counts ?? {},
        totals: data?.total_available ?? {}
      })
    } catch (err) {
      console.error('Failed to fetch stored chunks:', err)
      setChunks([])
      setStats(null)
      setError(err.message || 'Unexpected error')
    } finally {
      setLoading(false)
    }
  }, [queryParams, limit, language, source])

  useEffect(() => {
    fetchChunks()
  }, [fetchChunks])

  const formatLanguage = (value) => (value ? value.toUpperCase() : 'N/A')

  const formatSource = (value) => {
    if (value === 'qdrant') return 'Qdrant'
    if (value === 'chunk_store') return 'Persisted Store'
    return 'Unknown'
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-blue-100 text-blue-600">
            <Database className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              Stored Chunks
            </h2>
            <p className="text-sm text-gray-500">
              Inspect chunk metadata from Qdrant and the persisted chunk store.
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <label className="flex items-center gap-2 rounded-md border border-gray-200 bg-white px-3 py-2 text-sm text-gray-700 shadow-sm">
            <Filter className="h-4 w-4 text-gray-500" />
            <select
              className="rounded-md border-gray-300 text-sm focus:border-blue-500 focus:ring-blue-500"
              value={language}
              onChange={(event) => setLanguage(event.target.value)}
              disabled={loading}
            >
              {languageOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>

          <select
            className="rounded-md border-gray-300 text-sm focus:border-blue-500 focus:ring-blue-500"
            value={source}
            onChange={(event) => setSource(event.target.value)}
            disabled={loading}
          >
            {sourceOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>

          <label className="text-sm text-gray-600">
            Show
            <select
              className="ml-2 rounded-md border-gray-300 text-sm focus:border-blue-500 focus:ring-blue-500"
              value={limit}
              onChange={(event) => setLimit(Number(event.target.value))}
              disabled={loading}
            >
              {limitOptions.map((value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ))}
            </select>
            chunks
          </label>

          <button
            type="button"
            onClick={fetchChunks}
            disabled={loading}
            className="inline-flex items-center gap-2 rounded-md border border-gray-200 bg-white px-3 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          <AlertTriangle className="h-4 w-4" />
          <span>{error}</span>
        </div>
      )}

      {stats && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
          <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
            <p className="text-sm text-gray-500">Returned</p>
            <p className="mt-1 text-2xl font-semibold text-gray-900">
              {stats.returned}
            </p>
          </div>
          <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
            <p className="text-sm text-gray-500">Limit</p>
            <p className="mt-1 text-2xl font-semibold text-gray-900">
              {stats.limit}
            </p>
          </div>
          <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
            <p className="text-sm text-gray-500">Qdrant Stored</p>
            <p className="mt-1 text-2xl font-semibold text-gray-900">
              {stats.totals?.qdrant ?? '—'}
            </p>
          </div>
          <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
            <p className="text-sm text-gray-500">Persisted Chunks</p>
            <p className="mt-1 text-2xl font-semibold text-gray-900">
              {stats.totals?.chunk_store ?? '—'}
            </p>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex h-48 items-center justify-center rounded-lg border border-dashed border-gray-200 bg-white">
          <p className="text-sm text-gray-500">Loading chunks...</p>
        </div>
      ) : chunks.length === 0 ? (
        <div className="flex h-48 items-center justify-center rounded-lg border border-dashed border-gray-200 bg-white">
          <p className="text-sm text-gray-500">
            No chunks found for the selected filters.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {chunks.map((chunk, index) => (
            <article
              key={`${chunk.point_id ?? chunk.doc_id ?? index}`}
              className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <p className="text-xs uppercase tracking-wide text-gray-500">
                    Document ID
                  </p>
                  <p className="font-medium text-gray-900 break-all">
                    {chunk.doc_id}
                  </p>
                </div>
                <div className="flex items-center gap-3 text-sm text-gray-500">
                  <span className="rounded-full bg-gray-100 px-3 py-1 font-medium text-gray-700">
                    Chunk #{index + 1}
                  </span>
                  <span className="rounded-full bg-blue-50 px-3 py-1 font-medium text-blue-600">
                    {formatLanguage(chunk.language)}
                  </span>
                  <span className="rounded-full bg-purple-50 px-3 py-1 font-medium text-purple-600">
                    {formatSource(chunk.source)}
                  </span>
                </div>
              </div>
              <div className="mt-3 rounded-md border border-gray-100 bg-gray-50 p-3">
                <p className="whitespace-pre-wrap text-sm text-gray-700">
                  {chunk.text || '—'}
                </p>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  )
}

export default StoredChunks
