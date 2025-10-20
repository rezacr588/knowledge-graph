import { FileText, TrendingUp, Database, Network, Zap } from 'lucide-react'

export default function ResultsDisplay({ results }) {
  if (!results || !results.results || results.results.length === 0) {
    return null
  }

  const { results: items, retrieval_time_ms, fusion_time_ms, methods_used } = results

  return (
    <div className="space-y-6">
      {/* Metrics */}
      <div className="bg-white rounded-lg shadow-sm border p-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {items.length}
            </div>
            <div className="text-xs text-gray-500 mt-1">Results Found</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {retrieval_time_ms.toFixed(0)}ms
            </div>
            <div className="text-xs text-gray-500 mt-1">Retrieval Time</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              {fusion_time_ms.toFixed(0)}ms
            </div>
            <div className="text-xs text-gray-500 mt-1">Fusion Time</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">
              {methods_used.length}
            </div>
            <div className="text-xs text-gray-500 mt-1">Methods Used</div>
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Search Results</h3>
        {items.map((item, index) => (
          <div key={index} className="bg-white rounded-lg shadow-sm border p-5 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center space-x-2">
                <div className="flex items-center justify-center w-8 h-8 bg-blue-100 rounded-full">
                  <span className="text-sm font-bold text-blue-600">#{item.rank}</span>
                </div>
                <div>
                  <span className="text-xs font-medium text-gray-500">RRF Score</span>
                  <div className="text-sm font-semibold text-gray-900">{item.rrf_score.toFixed(4)}</div>
                </div>
              </div>
              <div className="flex items-center space-x-1">
                <FileText className="h-4 w-4 text-gray-400" />
                <span className="text-xs text-gray-500">{item.language.toUpperCase()}</span>
              </div>
            </div>
            <p className="text-gray-800 mb-4 leading-relaxed">{item.text}</p>
            <div className="flex flex-wrap gap-2">
              {Object.entries(item.method_scores).map(([method, score]) => (
                <div key={method} className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
                  <span className="capitalize">{method}:</span>
                  <span className="ml-1 font-semibold">{typeof score === 'number' ? score.toFixed(2) : score}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
