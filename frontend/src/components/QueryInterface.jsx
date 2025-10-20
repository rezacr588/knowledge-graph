import { useState } from 'react'
import { Search, Loader2, Settings } from 'lucide-react'
import axios from 'axios'

export default function QueryInterface({ onResults }) {
  const [query, setQuery] = useState('')
  const [language, setLanguage] = useState('en')
  const [topK, setTopK] = useState(10)
  const [methods, setMethods] = useState(['bm25', 'colbert', 'graph'])
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [searching, setSearching] = useState(false)
  const [error, setError] = useState(null)

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    setSearching(true)
    setError(null)

    try {
      const response = await axios.post('/api/query', {
        query: query.trim(),
        top_k: topK,
        language,
        retrieval_methods: methods,
      })
      onResults(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Search failed')
      onResults(null)
    } finally {
      setSearching(false)
    }
  }

  const toggleMethod = (method) => {
    setMethods(prev =>
      prev.includes(method)
        ? prev.filter(m => m !== method)
        : [...prev, method]
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <form onSubmit={handleSearch} className="space-y-4">
        {/* Search Input */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Search Query
          </label>
          <div className="relative">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your question..."
              className="block w-full pl-4 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
            />
            <div className="absolute inset-y-0 right-0 flex items-center pr-3">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
          </div>
        </div>

        {/* Basic Options */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Language
            </label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="en">English</option>
              <option value="ar">Arabic (العربية)</option>
              <option value="es">Spanish (Español)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Results
            </label>
            <select
              value={topK}
              onChange={(e) => setTopK(Number(e.target.value))}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value={5}>Top 5</option>
              <option value={10}>Top 10</option>
              <option value={20}>Top 20</option>
            </select>
          </div>
        </div>

        {/* Advanced Options */}
        <div>
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center space-x-2 text-sm text-gray-600 hover:text-gray-900"
          >
            <Settings className="h-4 w-4" />
            <span>{showAdvanced ? 'Hide' : 'Show'} Advanced Options</span>
          </button>

          {showAdvanced && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg space-y-3">
              <label className="block text-sm font-medium text-gray-700">
                Retrieval Methods
              </label>
              <div className="space-y-2">
                {[
                  { id: 'bm25', label: 'BM25 (Sparse)', desc: 'Keyword matching' },
                  { id: 'colbert', label: 'ColBERT (Dense)', desc: 'Semantic search' },
                  { id: 'graph', label: 'Graph', desc: 'Entity relationships' },
                ].map((method) => (
                  <label key={method.id} className="flex items-start">
                    <input
                      type="checkbox"
                      checked={methods.includes(method.id)}
                      onChange={() => toggleMethod(method.id)}
                      className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <div className="ml-3">
                      <span className="text-sm font-medium text-gray-900">
                        {method.label}
                      </span>
                      <p className="text-xs text-gray-500">{method.desc}</p>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Search Button */}
        <button
          type="submit"
          disabled={!query.trim() || methods.length === 0 || searching}
          className="w-full flex justify-center items-center px-4 py-3 border border-transparent rounded-lg shadow-sm text-base font-medium text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {searching ? (
            <>
              <Loader2 className="animate-spin h-5 w-5 mr-2" />
              Searching...
            </>
          ) : (
            <>
              <Search className="h-5 w-5 mr-2" />
              Search
            </>
          )}
        </button>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}
      </form>
    </div>
  )
}
